"""Paradox (Clausewitz) script dosyalari icin parser ve yazici.

Vic3 script formatinin ihtiyac duydugumuz tum ozelliklerini destekler:
  - `key = value`, `key = { ... }`, cipilak diziler `{ a b c }`
  - tirnakli/tirnaksiz degerler, `#` yorumlari
  - ayni anahtarin birden fazla kez gecmesi (create_pop, resource, ...)
  - `rgb{ ... }` / `hsv{ ... }` gibi onekli bloklar
  - `>=`, `<=`, `!=`, `>`, `<`, `?=` operatorleri
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

_TOKEN_RE = re.compile(
    r"""
      \#[^\n]*                      # yorum
    | "(?:[^"\\]|\\.)*"             # tirnakli string
    | \{ | \}                       # blok
    | >= | <= | != | \?= | = | > | <   # operatorler
    | [^\s{}=<>!?"\#]+              # cipilak token
    """,
    re.VERBOSE,
)

_OPERATORS = {"=", ">=", "<=", "!=", ">", "<", "?="}


def _tokenize(text: str) -> Iterator[str]:
    for match in _TOKEN_RE.finditer(text):
        token = match.group(0)
        if token.startswith("#"):
            continue
        yield token


def unquote(token: str) -> str:
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return token[1:-1]
    return token


@dataclass
class Node:
    """Bir blok: sirali (key, op, value) ciftleri ve/veya cipilak skalerler."""

    prefix: str = ""  # "rgb", "hsv" gibi blok onekleri
    pairs: list[tuple[str, str, "str | Node"]] = field(default_factory=list)
    scalars: list[str] = field(default_factory=list)

    # ---- okuma yardimcilari -------------------------------------------------

    def get(self, key: str, default=None):
        """Anahtarin son degerini dondurur (vanilla'da sonraki tanim kazanir)."""
        found = default
        for k, _op, v in self.pairs:
            if k == key:
                found = v
        return found

    def get_all(self, key: str) -> list:
        return [v for k, _op, v in self.pairs if k == key]

    def get_str(self, key: str, default: str | None = None) -> str | None:
        value = self.get(key)
        if value is None:
            return default
        if isinstance(value, Node):
            return default
        return unquote(value)

    def get_int(self, key: str, default: int | None = None) -> int | None:
        value = self.get_str(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def get_list(self, key: str) -> list[str]:
        """`key = { a b c }` seklindeki diziyi tirnaksiz string listesi olarak verir."""
        value = self.get(key)
        if not isinstance(value, Node):
            return []
        return [unquote(s) for s in value.scalars]

    def get_block(self, key: str) -> "Node | None":
        value = self.get(key)
        return value if isinstance(value, Node) else None

    def keys(self) -> list[str]:
        return [k for k, _op, _v in self.pairs]

    def has(self, key: str) -> bool:
        return any(k == key for k, _op, _v in self.pairs)

    # ---- yazma yardimcilari -------------------------------------------------

    def set(self, key: str, value: "str | Node") -> None:
        """Anahtari degistirir; yoksa sona ekler. Sirayi korur."""
        for i, (k, op, _v) in enumerate(self.pairs):
            if k == key:
                self.pairs[i] = (k, op, value)
                return
        self.pairs.append((key, "=", value))

    def remove(self, key: str) -> None:
        self.pairs = [(k, op, v) for k, op, v in self.pairs if k != key]

    # ---- serilestirme -------------------------------------------------------

    def dumps(self, indent: int = 0, inline_scalars: bool = True) -> str:
        pad = "\t" * indent
        inner_pad = "\t" * (indent + 1)
        parts: list[str] = []

        if self.scalars and not self.pairs and inline_scalars:
            return "{ " + " ".join(self.scalars) + " }"

        lines: list[str] = []
        if self.scalars:
            lines.append(inner_pad + " ".join(self.scalars))
        for key, op, value in self.pairs:
            if isinstance(value, Node):
                rendered = value.dumps(indent + 1, inline_scalars)
                lines.append(f"{inner_pad}{key} {op} {value.prefix}{rendered}")
            else:
                lines.append(f"{inner_pad}{key} {op} {value}")

        if not lines:
            return "{}"
        parts.append("{")
        parts.extend(lines)
        parts.append(pad + "}")
        return "\n".join(parts)


def parse(text: str) -> Node:
    tokens = list(_tokenize(text))
    root, pos = _parse_block(tokens, 0, top_level=True)
    if pos != len(tokens):
        raise ValueError(f"Beklenmeyen token: {tokens[pos]!r} (konum {pos})")
    return root


def parse_file(path: Path) -> Node:
    # Vic3 dosyalari genellikle UTF-8-BOM. utf-8-sig ikisini de dogru okur.
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    try:
        return parse(text)
    except ValueError as exc:
        raise ValueError(f"{path}: {exc}") from None


def _parse_block(tokens: list[str], pos: int, top_level: bool = False) -> tuple[Node, int]:
    node = Node()
    while pos < len(tokens):
        token = tokens[pos]

        if token == "}":
            if top_level:
                raise ValueError("fazladan '}'")
            return node, pos + 1

        if token == "{":
            # anahtarsiz alt blok (nadiren; ornegin ic ice dizi)
            sub, pos = _parse_block(tokens, pos + 1)
            node.pairs.append(("", "=", sub))
            continue

        # ileriye bak: operator var mi?
        if pos + 1 < len(tokens) and tokens[pos + 1] in _OPERATORS:
            key = unquote(token)
            op = tokens[pos + 1]
            pos += 2
            if pos >= len(tokens):
                raise ValueError(f"'{key} {op}' sonrasi deger yok")
            value_token = tokens[pos]
            if value_token == "{":
                sub, pos = _parse_block(tokens, pos + 1)
                node.pairs.append((key, op, sub))
            elif pos + 1 < len(tokens) and tokens[pos + 1] == "{":
                # rgb{ ... } / hsv{ ... } gibi onekli blok
                sub, pos = _parse_block(tokens, pos + 2)
                sub.prefix = value_token
                node.pairs.append((key, op, sub))
            else:
                node.pairs.append((key, op, value_token))
                pos += 1
            continue

        node.scalars.append(token)
        pos += 1

    if not top_level:
        raise ValueError("kapanmamis '{'")
    return node, pos


# ---------------------------------------------------------------------------
# Yazma
# ---------------------------------------------------------------------------

GENERATED_HEADER = (
    "# ============================================================\n"
    "#  OTOMATIK URETILDI - ELLE DUZENLEME\n"
    "#  Kaynak: world/  |  Uretici: tools/tgc.py build\n"
    "#  Bu dosyayi elle degistirirsen bir sonraki build'de kaybolur.\n"
    "# ============================================================\n"
)


def write_game_file(path: Path, body: str, header: bool = True) -> None:
    """Vic3 dosyasini BOM'lu UTF-8 olarak yazar (vanilla ile ayni kodlama)."""
    from . import paths as _paths

    target = _paths.assert_safe_write(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = (GENERATED_HEADER + "\n" if header else "") + body
    if not text.endswith("\n"):
        text += "\n"
    target.write_text(text, encoding="utf-8-sig", newline="\n")


def check_braces(text: str) -> tuple[bool, str]:
    """Yorum ve stringleri atlayarak brace dengesini kontrol eder."""
    depth = 0
    line = 1
    last_end = 0
    for token_match in _TOKEN_RE.finditer(text):
        token = token_match.group(0)
        line += text.count("\n", last_end, token_match.end())
        last_end = token_match.end()
        if token.startswith("#"):
            continue
        if token == "{":
            depth += 1
        elif token == "}":
            depth -= 1
            if depth < 0:
                return False, f"satir {line} civarinda fazladan '}}'"
    if depth != 0:
        return False, f"{depth} adet kapanmamis '{{'"
    return True, "ok"
