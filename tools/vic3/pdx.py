"""Clausewitz (Paradox script) tokenizer, parser and serializer.

The whole toolchain reads vanilla Victoria 3 data through this module, so it
has to survive every quirk actually present in the 1.13 install:

  * UTF-8 BOM on most files, plain UTF-8 on some, cp1252 on a stray few
  * "#" comments anywhere, including after a value on the same line
  * quoted and unquoted keys and values, freely mixed for the same concept
  * typed blocks written without a space: color = hsv{ 0.99 0.7 0.9 }
  * repeated keys inside one block (add_homeland appears many times)
  * comparison operators in triggers

Parsed data is a Node: an *ordered* list of (key, op, value) items. Order and
repetition are preserved because both matter when we re-emit filtered copies
of vanilla files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterator

__all__ = ["Node", "Item", "TypedBlock", "parse", "parse_file", "dumps",
           "read_text", "PdxSyntaxError"]

_WS = " \t\r\n"
_DELIM = "{}=<>!?" + _WS
_OPS = ("?=", ">=", "<=", "!=", "==", "=", ">", "<")   # longest first
_DQUOTE = chr(34)
_SQUOTE = chr(39)


class QuotedString(str):
    """Keep lexical spelling when copying a game string (including escapes)."""
    def __new__(cls, value, raw=None):
        result = super().__new__(cls, value)
        result.raw = raw
        return result


class PdxSyntaxError(ValueError):
    """Raised when a file cannot be parsed; carries file and line number."""


# --------------------------------------------------------------------------
# reading

def read_text(path) -> str:
    """Read a Paradox file, stripping the BOM and tolerating bad encodings."""
    with open(path, "rb") as handle:
        raw = handle.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


# --------------------------------------------------------------------------
# tokenizer

@dataclass(slots=True)
class _Tok:
    kind: str      # "scalar" | "op" | "{" | "}" | "eof"
    text: str
    line: int
    glued: bool    # no whitespace between this token and the previous one


def _tokenize(src: str, origin="<string>") -> list[_Tok]:
    toks: list[_Tok] = []
    i, n, line = 0, len(src), 1
    glued = False
    while i < n:
        c = src[i]
        if c in _WS:
            if c == "\n":
                line += 1
            i += 1
            glued = False
            continue
        if c == "#":
            while i < n and src[i] != "\n":
                i += 1
            glued = False
            continue
        if c == "{" or c == "}":
            toks.append(_Tok(c, c, line, glued))
            i += 1
            glued = True
            continue
        for op in _OPS:
            if src.startswith(op, i):
                toks.append(_Tok("op", op, line, glued))
                i += len(op)
                glued = True
                break
        else:
            if c == _DQUOTE:
                start_line = line
                j, buf = i + 1, []
                while j < n and src[j] != _DQUOTE:
                    if src[j] == "\\" and j + 1 < n:
                        buf.append(src[j + 1])
                        j += 2
                        continue
                    if src[j] == "\n":
                        line += 1
                    buf.append(src[j])
                    j += 1
                if j >= n:
                    raise PdxSyntaxError(f"{origin}:{start_line}: unterminated quoted string")
                toks.append(_Tok("scalar", QuotedString("".join(buf), src[i:j+1]), start_line, glued))
                i = j + 1
            else:
                j = i
                while j < n and src[j] not in _DELIM and src[j] != "#":
                    j += 1
                if j == i:
                    raise PdxSyntaxError(f"{origin}:{line}: unexpected delimiter {c!r}")
                toks.append(_Tok("scalar", src[i:j], line, glued))
                i = j
            glued = True
            continue
    toks.append(_Tok("eof", "", line, False))
    return toks


# --------------------------------------------------------------------------
# tree

@dataclass(slots=True)
class TypedBlock:
    """A block carrying a type prefix, such as hsv{ ... } or rgb{ ... }."""
    type: str
    node: "Node"


@dataclass(slots=True)
class Item:
    key: str | None    # None for a bare value inside a list
    op: str
    value: "str | Node | TypedBlock"


@dataclass(slots=True)
class Node:
    items: list[Item] = field(default_factory=list)

    # -- keyed access -----------------------------------------------------
    def get(self, key: str, default=None):
        """Last value stored under key (Paradox semantics: later wins)."""
        out = default
        for it in self.items:
            if it.key == key:
                out = it.value
        return out

    def getall(self, key: str) -> list:
        return [it.value for it in self.items if it.key == key]

    def get_str(self, key: str, default=None):
        v = self.get(key)
        return v if isinstance(v, str) else default

    def get_int(self, key: str, default=None):
        try:
            return int(float(self.get_str(key)))
        except (TypeError, ValueError):
            return default

    def get_float(self, key: str, default=None):
        try:
            return float(self.get_str(key))
        except (TypeError, ValueError):
            return default

    def get_node(self, key: str):
        v = self.get(key)
        if isinstance(v, TypedBlock):
            return v.node
        return v if isinstance(v, Node) else None

    def get_list(self, key: str) -> list[str]:
        """Bare scalars inside `key = { a b c }`; [] when absent."""
        nd = self.get_node(key)
        return nd.values() if nd else []

    def __contains__(self, key: str) -> bool:
        return any(it.key == key for it in self.items)

    # -- list access ------------------------------------------------------
    def values(self) -> list[str]:
        return [it.value for it in self.items
                if it.key is None and isinstance(it.value, str)]

    def blocks(self) -> list["Node"]:
        return [it.value for it in self.items
                if it.key is None and isinstance(it.value, Node)]

    # -- iteration / mutation ---------------------------------------------
    def pairs(self) -> Iterator[tuple]:
        for it in self.items:
            if it.key is not None:
                yield it.key, it.value

    def keys(self) -> list[str]:
        return [it.key for it in self.items if it.key is not None]

    def set(self, key: str, value, op: str = "=") -> None:
        """Replace the first occurrence of key, or append when absent."""
        for it in self.items:
            if it.key == key:
                it.value, it.op = value, op
                return
        self.items.append(Item(key, op, value))

    def add(self, key, value, op: str = "=") -> None:
        self.items.append(Item(key, op, value))

    def remove(self, key: str) -> None:
        self.items = [it for it in self.items if it.key != key]

    def __len__(self) -> int:
        return len(self.items)

    def __bool__(self) -> bool:
        return True


# --------------------------------------------------------------------------
# parser

def parse(src: str, origin: str = "<string>") -> Node:
    toks = _tokenize(src, origin)
    pos = 0

    def fail(tok, msg):
        raise PdxSyntaxError(f"{origin}:{tok.line}: {msg} (near {tok.text!r})")

    def parse_block(depth: int) -> Node:
        nonlocal pos
        node = Node()
        while True:
            tok = toks[pos]
            if tok.kind == "eof":
                if depth:
                    fail(tok, "unexpected end of file, unclosed brace")
                return node
            if tok.kind == "}":
                if not depth:
                    fail(tok, "unexpected closing brace")
                pos += 1
                return node
            if tok.kind == "{":
                pos += 1                      # bare block inside a list
                node.items.append(Item(None, "=", parse_block(depth + 1)))
                continue
            if tok.kind == "op":
                fail(tok, "operator without a key")

            nxt = toks[pos + 1]
            if nxt.kind == "op":
                key, op = tok.text, nxt.text
                pos += 2
                node.items.append(Item(key, op, parse_value(depth)))
            elif nxt.kind == "{" and not isinstance(tok.text, QuotedString) and (nxt.glued or tok.text in ("rgb", "hsv", "hsv360")):
                typ = tok.text                # typed block as a bare list item
                pos += 2
                node.items.append(
                    Item(None, "=", TypedBlock(typ, parse_block(depth + 1))))
            else:
                pos += 1
                node.items.append(Item(None, "=", tok.text))

    def parse_value(depth: int):
        nonlocal pos
        tok = toks[pos]
        if tok.kind == "{":
            pos += 1
            return parse_block(depth + 1)
        if tok.kind == "scalar":
            nxt = toks[pos + 1]
            if nxt.kind == "{" and not isinstance(tok.text, QuotedString) and (nxt.glued or tok.text in ("rgb", "hsv", "hsv360")):
                typ = tok.text
                pos += 2
                return TypedBlock(typ, parse_block(depth + 1))
            pos += 1
            return tok.text
        fail(tok, "expected a value")

    return parse_block(0)


def parse_file(path) -> Node:
    return parse(read_text(path), origin=str(path))


# --------------------------------------------------------------------------
# serializer

_BARE_OK = re.compile(r"^[A-Za-z0-9_:.@|/-]+$")


def _scalar(s: str) -> str:
    if isinstance(s, QuotedString) and s.raw is not None:
        return s.raw
    if s == "" or not _BARE_OK.match(s):
        return _DQUOTE + s.replace("\\", "\\\\").replace(_DQUOTE, "\\" + _DQUOTE) + _DQUOTE
    return s


def _fits_inline(node: Node) -> bool:
    """Short all-scalar lists read better on one line."""
    if any(it.key is not None or not isinstance(it.value, str)
           for it in node.items):
        return False
    return len(node.items) <= 12 and sum(len(v) + 1 for v in node.values()) <= 90


def _dump(node: Node, indent: int, out: list[str]) -> None:
    pad = "\t" * indent
    for it in node.items:
        if it.key is None:
            if isinstance(it.value, str):
                out.append(pad + _scalar(it.value))
            elif isinstance(it.value, TypedBlock):
                out.append(pad + it.value.type + "{")
                _dump(it.value.node, indent + 1, out)
                out.append(pad + "}")
            else:
                out.append(pad + "{")
                _dump(it.value, indent + 1, out)
                out.append(pad + "}")
            continue
        key = _scalar(it.key)
        if isinstance(it.value, str):
            out.append(f"{pad}{key} {it.op} {_scalar(it.value)}")
        elif isinstance(it.value, TypedBlock):
            inner: list[str] = []
            _dump(it.value.node, 0, inner)
            joined = " ".join(x.strip() for x in inner)
            out.append(f"{pad}{key} {it.op} {it.value.type}" + "{ " + joined + " }")
        elif _fits_inline(it.value):
            vals = " ".join(_scalar(v) for v in it.value.values())
            body = "{ " + vals + " }" if vals else "{}"
            out.append(f"{pad}{key} {it.op} " + body)
        else:
            out.append(f"{pad}{key} {it.op} " + "{")
            _dump(it.value, indent + 1, out)
            out.append(pad + "}")


def dumps(node: Node, indent: int = 0) -> str:
    out: list[str] = []
    _dump(node, indent, out)
    return "\n".join(out)
