"use strict";
(() => {
  const D = JSON.parse(document.getElementById("atlas-data").textContent);
  const $ = (id) => document.getElementById(id);
  const P = D.provinces,
    S = new Map(D.catalog_states.map((s) => [s.id, s]));
  const byIndex = new Map(D.catalog_states.map((s) => [s.index, s]));
  const provincesByState = new Map();
  P.forEach((p, i) => {
    if (p) {
      if (!provincesByState.has(p.state)) provincesByState.set(p.state, []);
      provincesByState.get(p.state).push(i);
    }
  });
  const clone = (x) => JSON.parse(JSON.stringify(x));
  const safeObject = (x) => x && typeof x === "object" && !Array.isArray(x);
  const owns = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const initial = clone(D.scenario);
  let draft = clone(initial),
    countries,
    owners,
    selected = new Set(),
    active = null,
    province = null;
  let history = [],
    future = [],
    hit,
    width,
    height,
    pixels,
    pixelCounts,
    beforeImage,
    currentImage,
    beforeBorder = null,
    scale = 1,
    tx = 0,
    ty = 0,
    ready = false;
  const canvas = $("map"),
    ctx = canvas.getContext("2d"),
    viewport = $("viewport");
  const storageKey = "tgc-atlas-v1-" + D.fingerprint;
  let storageAvailable = true;
  function status(message, error = false) {
    $("status").textContent = message;
    $("status").classList.toggle("error", error);
  }
  function el(tag, text, cls) {
    const n = document.createElement(tag);
    if (text !== undefined) n.textContent = text;
    if (cls) n.className = cls;
    return n;
  }
  function download(name, content, type = "application/json") {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const a = el("a");
    a.href = url;
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function save() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(draft));
    } catch {
      storageAvailable = false;
    }
  }
  function canonical(id) {
    return id.startsWith("STATE_") ? id : "STATE_" + id.toUpperCase();
  }
  function statePlan(state, spec, tags) {
    if (typeof spec === "string") spec = { owner: spec };
    if (!safeObject(spec))
      throw Error(state.id + ": eyalet tanımı nesne veya ülke etiketi olmalı.");
    const allowed = [
      "owner",
      "split",
      "pops",
      "buildings",
      "homelands",
      "claims",
      "state_type",
      "notes",
      "phase", "population", "industry",
    ];
    for (const k of Object.keys(spec))
      if (!allowed.includes(k))
        throw Error(state.id + ": bilinmeyen alan " + k);
    if (!owns(spec, "owner") && !owns(spec, "split") &&
        ["population", "industry", "homelands", "claims", "state_type"].some(k => owns(spec, k))) {
      return new Map((provincesByState.get(state.index) || []).map(i => [P[i].hex, P[i].base]));
    }
    if (owns(spec, "owner") === owns(spec, "split"))
      throw Error(
        state.id + ": owner veya split alanlarından yalnızca biri gerekli.",
      );
    for (const k of ["pops", "buildings"])
      if (owns(spec, k) && !["inherit", "drop"].includes(spec[k]))
        throw Error(k + ": inherit veya drop olmalı.");
    const parts = owns(spec, "owner")
      ? [{ owner: spec.owner, rest: true }]
      : spec.split;
    if (!Array.isArray(parts) || !parts.length)
      throw Error(state.id + ": boş bölünme.");
    const assignment = new Map(),
      all = new Set(state.provinces);
    let rest = null;
    for (const part of parts) {
      if (
        !safeObject(part) ||
        typeof part.owner !== "string" ||
        !owns(tags, part.owner)
      )
        throw Error(state.id + ": bilinmeyen ülke etiketi.");
      for (const k of Object.keys(part))
        if (!["owner", "provinces", "rest", "state_type"].includes(k))
          throw Error(state.id + ": bilinmeyen bölünme alanı " + k);
      if (owns(part, "rest") && typeof part.rest !== "boolean")
        throw Error("rest alanı true veya false olmalı.");
      if (part.rest) {
        if (rest !== null)
          throw Error(state.id + ": yalnızca bir rest payı olabilir.");
        if (part.provinces?.length)
          throw Error("rest ve provinces birlikte kullanılamaz.");
        rest = part.owner;
      } else {
        if (!Array.isArray(part.provinces) || !part.provinces.length)
          throw Error(state.id + ": il listesi gerekli.");
        for (const hex of part.provinces) {
          if (!all.has(hex)) throw Error(state.id + ": geçersiz il " + hex);
          if (assignment.has(hex))
            throw Error(state.id + ": iki kez atanan il " + hex);
          assignment.set(hex, part.owner);
        }
      }
    }
    let required = state.provinces.filter((p) => !state.impassable.includes(p));
    if (!required.length) required = state.provinces;
    for (const hex of required) {
      if (!assignment.has(hex)) {
        if (rest === null)
          throw Error(state.id + ": sahipsiz il; rest payı ekleyin.");
        assignment.set(hex, rest);
      }
    }
    return assignment;
  }
  const countryKeys = [
    "color",
    "country_type",
    "tier",
    "cultures",
    "religion",
    "tech_tier",
    "literacy",
    "capital",
    "name",
    "adjective",
    "name_tr",
    "adjective_tr",
    "religion_map",
    "religion_split",
    "culture_religion_split",
    "culture_map",
    "overlord",
    "subject_type",
    "liberty_desire",
    "market_capital",
    "notes",
    "coat_of_arms",
    "is_named_from_capital",
    "phase", "population", "industry", "technology", "laws", "institutions",
    "interest_groups", "companies", "military", "history_mode",
  ];
  function parseDocument(text) {
    const value = JSON.parse(text);
    const tokens = text.match(/"(?:\\[\s\S]|[^"\\])*"|[{}\[\]:]/g) || [];
    const stack = [];
    for (let i = 0; i < tokens.length; i++) {
      const token = tokens[i];
      if (token === "{") stack.push(new Set());
      else if (token === "[") stack.push(null);
      else if (token === "}" || token === "]") stack.pop();
      else if (token.startsWith('"') && tokens[i + 1] === ":" && stack.at(-1)) {
        const key = JSON.parse(token),
          keys = stack.at(-1);
        if (keys.has(key)) throw Error("Tekrarlanan JSON alanı: " + key);
        keys.add(key);
      }
    }
    return value;
  }
  function validated(raw) {
    if (!safeObject(raw) || ![1, 2].includes(raw.version))
      throw Error("Senaryo version: 1 veya 2 içeren bir JSON nesnesi olmalı.");
    for (const k of Object.keys(raw))
      if (
        !["version", "title", "description", "countries", "states", "diplomacy", "subject_types"].includes(k)
      )
        throw Error("Bilinmeyen senaryo alanı: " + k);
    for (const k of ["title", "description"])
      if (owns(raw, k) && typeof raw[k] !== "string")
        throw Error(k + " metin olmalı.");
    for (const k of ["diplomacy", "subject_types"])
      if (owns(raw,k) && (raw.version !== 2 || !safeObject(raw[k])))
        throw Error(k + ": version 2 nesnesi gerekli.");
    const next = clone(raw);
    next.countries ??= {};
    next.states ??= {};
    if (!safeObject(next.countries) || !safeObject(next.states))
      throw Error("countries ve states nesne olmalı.");
    const tags = Object.assign(Object.create(null), D.base_countries);
    for (const [tag, c] of Object.entries(next.countries)) {
      if (!/^(?=.*[A-Z])[A-Z0-9]{2,4}$/.test(tag) || !safeObject(c))
        throw Error("Geçersiz ülke tanımı: " + tag);
      for (const k of Object.keys(c))
        if (!countryKeys.includes(k))
          throw Error(tag + ": bilinmeyen alan " + k);
      for (const k of ["name", "name_tr", "religion"])
        if (owns(c, k) && c[k] !== null && typeof c[k] !== "string")
          throw Error(tag + ": " + k + " metin olmalı.");
      if (
        c.color !== undefined &&
        c.color !== null &&
        (!Array.isArray(c.color) ||
          c.color.length !== 3 ||
          c.color.some(
            (v) =>
              typeof v !== "number" || !Number.isFinite(v) || v < 0 || v > 255,
          ))
      )
        throw Error(tag + ": color üç adet 0–255 sayısı içermeli.");
      tags[tag] = c;
    }
    const states = Object.create(null);
    for (const [id, spec] of Object.entries(next.states)) {
      const key = canonical(id);
      if (owns(states, key)) throw Error("Tekrarlanan eyalet: " + key);
      if (!S.has(key))
        throw Error(
          key +
            ": atlas kapsamı dışında. Dünya atlasında açın veya bu eyaleti içeren bir atlas üretin.",
        );
      statePlan(S.get(key), spec, tags);
      states[key] = spec;
    }
    next.states = states;
    return next;
  }
  function mutate(next, message) {
    try {
      next = validated(next);
      history.push(clone(draft));
      if (history.length > 80) history.shift();
      future = [];
      draft = next;
      refresh();
      status(
        message +
          (storageAvailable
            ? ""
            : " Otomatik kayıt kullanılamıyor; taslağı indirin."),
      );
    } catch (e) {
      status(e.message, true);
    }
  }
  function colorRgb(c) {
    if (!c) return [150, 150, 150];
    const max = Math.max(...c);
    return c.map((v) => Math.round(v * (max <= 1.001 ? 255 : 1)));
  }
  function rebuild() {
    countries = Object.assign(Object.create(null), clone(D.base_countries));
    for (const [tag, c] of Object.entries(draft.countries || {})) {
      const old = countries[tag] || {
        tag,
        name: tag,
        color: [150, 150, 150],
        religion: "none",
        phase: null,
      };
      countries[tag] = {
        ...old,
        ...c,
        name: c.name_tr || c.name || old.name,
        color: c.color ? colorRgb(c.color) : old.color,
      };
    }
    owners = P.map((p) => (p ? p.base : null));
    for (const [id, spec] of Object.entries(draft.states || {})) {
      const s = S.get(id);
      const plan = statePlan(s, spec, countries);
      for (const i of provincesByState.get(s.index) || [])
        owners[i] = plan.get(P[i].hex) || null;
    }
  }
  function stateOwners(s) {
    const counts = new Map();
    for (const i of provincesByState.get(s.index) || []) {
      const tag = owners[i];
      if (tag) counts.set(tag, (counts.get(tag) || 0) + 1);
    }
    return [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  }
  function stateChanged(s) {
    return (provincesByState.get(s.index) || []).some(
      (i) => owners[i] !== P[i].before,
    );
  }
  function refresh() {
    rebuild();
    save();
    $("title").textContent = draft.title || D.title;
    $("scenario-title").value = draft.title || D.title;
    $("draft-count").textContent =
      Object.keys(draft.states || {}).length + " eyalet";
    $("change-count").textContent =
      D.states.filter(stateChanged).length + " eyalet değişti";
    $("undo").disabled = !history.length;
    $("redo").disabled = !future.length;
    $("countries").replaceChildren(
      ...Object.keys(countries)
        .sort()
        .map((t) => {
          const o = el("option");
          o.value = t;
          o.label = countries[t].name;
          return o;
        }),
    );
    $("changes").replaceChildren(
      ...Object.keys(draft.states || {}).map((id) => {
        const b = el(
          "button",
          id.replace("STATE_", "") +
            " → " +
            stateOwners(S.get(id))
              .map((v) => v[0])
              .join(" / "),
        );
        b.onclick = () => selectState(id, false, true);
        return b;
      }),
    );
    list();
    inspect();
    if (ready) render();
  }
  function normalize(v) {
    return String(v)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/ı/g, "i")
      .toLowerCase();
  }
  function list() {
    const query = normalize($("search").value.trim());
    const region = $("region").value;
    const found = D.states.filter((s) => {
      if (region && s.region !== region) return false;
      if ($("changed-only").checked && !stateChanged(s)) return false;
      const tags = stateOwners(s).map((v) => v[0]);
      return (
        !query ||
        normalize(
          [
            s.id,
            s.name,
            ...s.aliases,
            ...tags,
            ...tags.map((t) => countries[t]?.name || ""),
            ...s.provinces,
          ].join(" "),
        ).includes(query)
      );
    });
    $("state-count").textContent = found.length + " / " + D.states.length;
    $("results").replaceChildren(
      ...found.map((s) => {
        const b = el(
          "button",
          undefined,
          "state-row" + (selected.has(s.id) ? " selected" : ""),
        );
        b.setAttribute("aria-pressed", selected.has(s.id));
        const label = el("span", s.name);
        label.append(el("small", s.id.replace("STATE_", "")));
        b.append(
          label,
          el(
            "span",
            stateOwners(s)
              .slice(0, 3)
              .map((v) => v[0])
              .join(" / ") +
              (stateOwners(s).length > 3
                ? " +" + (stateOwners(s).length - 3)
                : ""),
            "tags",
          ),
        );
        b.onclick = (e) =>
          selectState(
            s.id,
            e.shiftKey,
            true,
            (provincesByState.get(s.index) || []).find(
              (i) => normalize(P[i].hex) === query,
            ) || null,
          );
        return b;
      }),
    );
    if (!found.length)
      $("results").append(
        el("p", "Eşleşme yok. Adı veya ülke etiketini değiştirin.", "muted"),
      );
  }
  function selectState(id, extend = false, focus = false, prov = null) {
    if (!S.has(id)) {
      status(
        "Komşu eyalet bu atlasın kapsamı dışında; dünya atlasını kullanın.",
        true,
      );
      return;
    }
    if (!extend) selected.clear();
    if (extend && selected.has(id)) selected.delete(id);
    else selected.add(id);
    active = selected.has(id) ? id : [...selected].at(-1) || null;
    province = prov;
    list();
    inspect();
    render();
    if (focus && active) focusState(S.get(active));
  }
  function inspect() {
    $("empty").hidden = !!active;
    $("details").hidden = !active;
    if (!active) return;
    const s = S.get(active);
    $("state-id").textContent = s.id;
    $("state-name").textContent = s.name;
    $("source").textContent =
      (owns(draft.states || {}, s.id) ? "Senaryo taslağı" : s.source) +
      " · " +
      s.region;
    $("ownership").replaceChildren(
      ...stateOwners(s).map(([tag, n]) => {
        const row = el("div", undefined, "owner-row");
        const sw = el("span", undefined, "swatch");
        sw.style.background = "rgb(" + countries[tag].color + ")";
        row.append(
          sw,
          el("span", countries[tag].name + " · " + tag),
          el("span", n + " il"),
        );
        return row;
      }),
    );
    $("facts").replaceChildren(
      ...[
        [s.provinces.length, "il / province"],
        [s.neighbors.length, "kara komşusu"],
      ].map(([n, l]) => {
        const f = el("div", undefined, "fact");
        f.append(el("strong", n), el("span", l));
        return f;
      }),
    );
    const economy = $("development");
    economy.replaceChildren();
    const report = D.development;
    const stale = JSON.stringify(draft) !== JSON.stringify(initial);
    economy.hidden = !report && draft.version !== 2;
    if (!economy.hidden) {
      economy.append(el("h3", "Başlangıç dünyası"));
      if (!report || stale) {
        economy.append(el("p", "Taslak değişti. Ekonomi ve diplomasi için scenario validate/report ile yeniden derleyin; bu görünüm haritayı günceller.", "muted"));
      } else {
        const st = report.states[s.id];
        for (const [tag, data] of Object.entries(st?.owners || {})) {
          const c = report.countries[tag] || {};
          economy.append(el("h4", tag + " · " + data.population.toLocaleString("tr-TR") + " kişi"));
          const lit = data.settings.literacy;
          const info = [lit === undefined ? "Okuryazarlık: oyun başlangıcı" : "Okuryazarlık girdisi: %" + Math.round(lit*100),
            data.buildings.reduce((n,b) => n+b.level,0) + " bina seviyesi",
            "Tahmini iş: " + data.estimated_jobs.toLocaleString("tr-TR"),
            "Altyapı talebi: " + data.infrastructure_demand_base,
            "Bağlılık: " + (c.overlord || "Bağımsız"),
            (c.military?.battalions || 0) + " tabur / " + (c.military?.ships || 0) + " gemi (ülke)"];
          for (const line of info) economy.append(el("p", line));
          const ratios = (values) => Object.entries(values).map(([k,v]) => k + " %" + (100*v/(data.population || 1)).toFixed(1)).join(" · ");
          economy.append(el("p", ratios(data.cultures), "muted"), el("p", ratios(data.religions), "muted"));
          const details = el("details");
          details.append(el("summary", "Binalar ve ülke kanunları"));
          for (const b of data.buildings) details.append(el("p", b.type + " × " + b.level));
          details.append(el("p", (c.laws || []).join(", "), "muted"));
          economy.append(details);
        }
      }
    }
    const choices = provincesByState.get(s.index) || [];
    if (!choices.includes(province))
      province = choices.find((i) => !P[i].impassable) || choices[0] || null;
    $("province").replaceChildren(
      ...choices.map((i) => {
        const p = P[i],
          o = el(
            "option",
            p.hex +
              " · " +
              (owners[i] || "sahipsiz") +
              (p.impassable ? " · geçilemez" : ""),
          );
        o.value = i;
        return o;
      }),
    );
    if (province) $("province").value = province;
    provinceInfo();
    $("assign-state").textContent =
      selected.size > 1 ? selected.size + " eyaleti ata" : "Eyaleti ata";
    $("neighbors").replaceChildren(
      ...s.neighbors.map((id) => {
        const b = el("button", S.get(id)?.name || id.replace("STATE_", ""));
        b.onclick = () => selectState(id, false, true);
        return b;
      }),
    );
    $("state-json").textContent = JSON.stringify(
      { ...s, current_owners: stateOwners(s), draft: draft.states?.[s.id] },
      null,
      2,
    );
  }
  function provinceInfo() {
    const p = P[province];
    $("province-info").textContent = p
      ? "Önce: " +
        (p.before || "sahipsiz") +
        " → Şimdi: " +
        (owners[province] || "sahipsiz") +
        (p.impassable ? " · Geçilemez arazi" : "")
      : "";
    $("assign-province").disabled = !p || p.impassable;
  }
  function hash(v) {
    let h = 2166136261;
    for (const b of new TextEncoder().encode(String(v)))
      h = Math.imul(h ^ b, 16777619) >>> 0;
    return h;
  }
  function distinct(i) {
    const h = (i * 0.61803398875) % 1,
      s = 0.42 + 0.22 * (Math.floor(i / 3) % 3),
      v = 0.78 + 0.14 * (Math.floor(i / 7) % 2);
    const k = (n) => (n + h * 6) % 6;
    return [5, 3, 1].map((n) =>
      Math.floor(255 * (v - v * s * Math.max(0, Math.min(k(n), 4 - k(n), 1)))),
    );
  }
  const religionColors = {
    catholic: [214, 160, 60],
    protestant: [70, 100, 170],
    orthodox: [140, 80, 160],
    oriental_orthodox: [40, 140, 165],
    sunni: [35, 140, 90],
    shiite: [25, 105, 120],
    ibadi: [90, 165, 120],
    hindu: [225, 130, 60],
    sikh: [235, 190, 70],
    mahayana: [200, 110, 140],
    theravada: [220, 150, 90],
    gelugpa: [185, 95, 60],
    confucian: [170, 60, 70],
    shinto: [200, 90, 110],
    jewish: [110, 120, 200],
    animist: [130, 150, 80],
    atheist: [140, 140, 140],
  };

  function palette(mode) {
    return P.map((p, i) => {
      if (!p) return [245, 243, 238];
      const s = byIndex.get(p.state);
      if (!s) return D.palettes[mode][i];
      const tag = owners[i],
        c = countries[tag];
      if (mode === "reference") return D.palettes.reference[i];
      if (mode === "changes")
        return tag !== p.before ? [230, 174, 78] : [96, 116, 123];
      if (!tag) return p.impassable ? [182, 177, 160] : [215, 212, 205];
      if (mode === "religion") {
        const r = c?.religion || "none";
        return religionColors[r] || distinct(hash(r) % 97);
      }
      if (mode === "phase") {
        const spec = draft.states?.[s.id];
        const phase =
          (typeof spec === "object" ? spec.phase : null) ||
          (spec ? null : s.base_phase) ||
          c?.phase;
        return phase ? distinct(hash(phase) % 97) : [215, 212, 205];
      }
      return c?.color || [150, 150, 150];
    });
  }
  function imageData(pal, before = false) {
    const data = ctx.createImageData(width, height),
      out = data.data,
      borders = $("borders").value;
    const keys = P.map((p, i) =>
      !p
        ? 0
        : borders === "province"
          ? i
          : borders === "state"
            ? p.state
            : before
              ? p.before
              : owners[i],
    );
    const selectedIndices = new Set([...selected].map((id) => S.get(id).index));
    for (let i = 0; i < pixels.length; i++) {
      const id = pixels[i],
        p = P[id],
        x = i % width,
        right = x < width - 1 ? pixels[i + 1] : id,
        down = i + width < pixels.length ? pixels[i + width] : id;
      let color = pal[id];
      if (
        borders !== "none" &&
        (keys[id] !== keys[right] || keys[id] !== keys[down])
      )
        color = [60, 60, 60];
      if (
        !before &&
        p &&
        selectedIndices.has(p.state) &&
        (P[right]?.state !== p.state ||
          P[down]?.state !== p.state ||
          (x > 0 && P[pixels[i - 1]]?.state !== p.state) ||
          (i >= width && P[pixels[i - width]]?.state !== p.state))
      )
        color = [255, 239, 172];
      const j = i * 4;
      out[j] = color[0];
      out[j + 1] = color[1];
      out[j + 2] = color[2];
      out[j + 3] = 255;
    }
    return data;
  }
  function render() {
    if (!ready) return;
    const mode = $("mode").value;
    const pal = palette(mode);
    currentImage = imageData(pal);
    if (beforeBorder !== $("borders").value) {
      beforeImage = imageData(D.beforePalette, true);
      beforeBorder = $("borders").value;
    }
    compare();
    legend(mode);
  }
  function compare() {
    if (!ready) return;
    ctx.putImageData(currentImage, 0, 0);
    const ratio = Number($("compare").value) / 100;
    if (ratio) {
      ctx.putImageData(
        beforeImage,
        0,
        0,
        0,
        0,
        Math.round(width * ratio),
        height,
      );
      ctx.fillStyle = "#f1d59a";
      ctx.fillRect(Math.round(width * ratio) - 1, 0, 2, height);
    }
    drawLabels(ratio);
    $("compare-value").textContent = "%" + Math.round(ratio * 100) + " önce";
  }
  function drawLabels(ratio) {
    const overlay = $("map-labels");
    overlay.replaceChildren();
    if (!$("labels").checked) return;
    const boxes = [],
      k = D.geometry.scale,
      [x0, y0] = D.geometry.box;
    ctx.font = "12px Arial";
    for (const s of [...D.states].sort(
      (a, b) =>
        (b.bbox[2] - b.bbox[0]) * (b.bbox[3] - b.bbox[1]) -
        (a.bbox[2] - a.bbox[0]) * (a.bbox[3] - a.bbox[1]),
    )) {
      const nativeX = (s.anchor[0] - x0) * k,
        nativeY = (s.anchor[1] - y0) * k,
        x = tx + nativeX * scale,
        y = ty + nativeY * scale;
      if (
        nativeX < 0 || nativeX >= width || nativeY < 0 || nativeY >= height ||
        x < 0 ||
        x > viewport.clientWidth ||
        y < 14 ||
        y > viewport.clientHeight - 8
      )
        continue;
      const tags =
        nativeX < width * ratio
          ? s.before.map((o) => o.tag)
          : stateOwners(s).map((v) => v[0]);
      const text =
        $("mode").value === "reference"
          ? s.name
          : s.name + " · " + tags.join("/");
      const w = ctx.measureText(text).width,
        box = [x - w / 2 - 4, y - 14, x + w / 2 + 4, y + 5];
      if (
        box[0] < 0 ||
        box[2] > viewport.clientWidth ||
        boxes.some(
          (b) =>
            box[0] < b[2] && box[2] > b[0] && box[1] < b[3] && box[3] > b[1],
        )
      )
        continue;
      boxes.push(box);
      const label = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "text",
      );
      label.setAttribute("x", x);
      label.setAttribute("y", y);
      label.textContent = text;
      overlay.append(label);
    }
  }
  function legend(mode) {
    const entries = new Map(),
      areas = new Map();
    if (mode === "political")
      for (let i = 0; i < pixelCounts.length; i++) {
        const tag = owners[i];
        if (tag) areas.set(tag, (areas.get(tag) || 0) + pixelCounts[i]);
      }
    if (mode === "political")
      for (const s of D.states)
        for (const [tag] of stateOwners(s))
          entries.set(tag, [
            countries[tag].name + " · " + tag,
            countries[tag].color,
          ]);
    else if (mode === "religion")
      for (const s of D.states)
        for (const [tag] of stateOwners(s)) {
          const r = countries[tag].religion || "none";
          entries.set(r, [r, religionColors[r] || distinct(hash(r) % 97)]);
        }
    else if (mode === "changes") {
      entries.set("changed", ["Sahibi değişti", [230, 174, 78]]);
      entries.set("same", ["Aynı kaldı", [96, 116, 123]]);
    } else if (mode === "phase")
      for (const s of D.states)
        for (const [tag] of stateOwners(s)) {
          const spec = draft.states?.[s.id],
            phase =
              (typeof spec === "object" ? spec.phase : null) ||
              (spec ? null : s.base_phase) ||
              countries[tag].phase;
          entries.set(String(phase || "vanilla"), [
            String(phase || "vanilla"),
            phase ? distinct(hash(phase) % 97) : [215, 212, 205],
          ]);
        }
    else
      entries.set("reference", [
        "Renkler komşu eyaletleri ayırır; siyasi aidiyet göstermez.",
        [201, 181, 141],
      ]);
    $("legend").replaceChildren(
      ...[...entries]
        .sort(
          (a, b) =>
            (areas.get(b[0]) || 0) - (areas.get(a[0]) || 0) ||
            a[0].localeCompare(b[0]),
        )
        .map(([, [name, color]]) => {
          const n = el("span", undefined, "legend-item"),
            sw = el("span", undefined, "swatch");
          sw.style.background = "rgb(" + color + ")";
          n.append(sw, el("span", name));
          return n;
        }),
    );
  }
  function transform() {
    canvas.style.transform = `translate(${tx}px,${ty}px) scale(${scale})`;
    if (ready) drawLabels(Number($("compare").value) / 100);
  }
  function fit() {
    if (!ready) return;
    scale = Math.min(
      viewport.clientWidth / width,
      viewport.clientHeight / height,
    );
    tx = (viewport.clientWidth - width * scale) / 2;
    ty = (viewport.clientHeight - height * scale) / 2;
    transform();
  }
  function zoom(
    factor,
    x = viewport.clientWidth / 2,
    y = viewport.clientHeight / 2,
  ) {
    const old = scale;
    scale = Math.max(0.05, Math.min(12, scale * factor));
    tx = x - ((x - tx) * scale) / old;
    ty = y - ((y - ty) * scale) / old;
    transform();
  }
  function focusState(s) {
    if (!ready) return;
    const [x0, y0, x1, y1] = D.geometry.box,
      k = D.geometry.scale;
    const a = Math.max(x0, s.bbox[0]), b = Math.max(y0, s.bbox[1]);
    const c = Math.min(x1, s.bbox[2] + 1), d = Math.min(y1, s.bbox[3] + 1);
    if (a >= c || b >= d) {
      status("Bu eyalet kadrajın dışında; dünya atlasında görüntüleyin.", true);
      return;
    }
    scale = Math.min(
      viewport.clientWidth / Math.max(100, (c - a) * k + 100),
      viewport.clientHeight / Math.max(100, (d - b) * k + 100),
      6,
    );
    tx = viewport.clientWidth / 2 - ((a + c) / 2 - x0) * k * scale;
    ty = viewport.clientHeight / 2 - ((b + d) / 2 - y0) * k * scale;
    transform();
  }
  function at(e) {
    const r = viewport.getBoundingClientRect(),
      x = Math.floor((e.clientX - r.left - tx) / scale),
      y = Math.floor((e.clientY - r.top - ty) / scale);
    return x >= 0 && x < width && y >= 0 && y < height
      ? pixels[y * width + x]
      : 0;
  }
  let drag = null;
  viewport.addEventListener("pointerdown", (e) => {
    if (e.target.closest("button") || !ready) return;
    drag = {
      id: e.pointerId,
      x: e.clientX,
      y: e.clientY,
      tx,
      ty,
      moved: false,
    };
    viewport.setPointerCapture(e.pointerId);
  });
  viewport.addEventListener("pointermove", (e) => {
    if (!ready) return;
    if (drag) {
      const dx = e.clientX - drag.x,
        dy = e.clientY - drag.y;
      if (Math.abs(dx) + Math.abs(dy) > 5) drag.moved = true;
      if (drag.moved) {
        tx = drag.tx + dx;
        ty = drag.ty + dy;
        transform();
      }
    } else {
      const p = P[at(e)],
        s = p && byIndex.get(p.state);
      $("hover").hidden = !s;
      if (s)
        $("hover").textContent =
          s.name + " · " + p.hex + " · " + (owners[at(e)] || "sahipsiz");
    }
  });
  viewport.addEventListener("pointerup", (e) => {
    if (!drag) return;
    if (!drag.moved) {
      const i = at(e),
        p = P[i],
        s = p && byIndex.get(p.state);
      if (s) selectState(s.id, e.shiftKey, false, i);
    }
    drag = null;
  });
  viewport.addEventListener("pointercancel", () => {
    drag = null;
  });
  viewport.addEventListener("pointerleave", () => {
    $("hover").hidden = true;
  });
  viewport.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();
      const r = viewport.getBoundingClientRect();
      zoom(Math.exp(-e.deltaY * 0.001), e.clientX - r.left, e.clientY - r.top);
    },
    { passive: false },
  );
  viewport.addEventListener("keydown", (e) => {
    if (e.target !== viewport) return;
    const delta = {
      ArrowLeft: [40, 0],
      ArrowRight: [-40, 0],
      ArrowUp: [0, 40],
      ArrowDown: [0, -40],
    }[e.key];
    if (delta) {
      e.preventDefault();
      tx += delta[0];
      ty += delta[1];
      transform();
    }
    if (["+", "="].includes(e.key)) {
      e.preventDefault();
      zoom(1.3);
    }
    if (e.key === "-") {
      e.preventDefault();
      zoom(1 / 1.3);
    }
    if (e.key === "0") fit();
  });
  $("zoom-in").onclick = () => zoom(1.4);
  $("zoom-out").onclick = () => zoom(1 / 1.4);
  $("fit").onclick = fit;
  $("search").oninput = list;
  $("region").onchange = list;
  $("changed-only").onchange = list;
  $("labels").onchange = compare;
  $("mode").onchange = render;
  $("borders").onchange = render;
  let queued = false;
  $("compare").oninput = () => {
    if (!queued) {
      queued = true;
      requestAnimationFrame(() => {
        queued = false;
        compare();
      });
    }
  };
  $("clear").onclick = () => {
    selected.clear();
    active = null;
    province = null;
    list();
    inspect();
    render();
  };
  $("province").onchange = () => {
    province = Number($("province").value);
    provinceInfo();
  };
  function targetTag() {
    const tag = $("owner").value.trim().toUpperCase();
    if (!owns(countries, tag))
      throw Error("Geçerli bir ülke etiketi seçin veya yeni ülke oluşturun.");
    return tag;
  }
  $("assign-state").onclick = () => {
    try {
      const tag = targetTag(),
        next = clone(draft);
      next.states ??= {};
      for (const id of selected) {
        const old = next.states[id];
        next.states[id] = { ...(safeObject(old) ? old : {}), owner: tag };
        delete next.states[id].split;
      }
      mutate(next, selected.size + " eyalet " + tag + " ülkesine atandı.");
    } catch (e) {
      status(e.message, true);
    }
  };
  $("assign-province").onclick = () => {
    try {
      const tag = targetTag(),
        s = S.get(active),
        next = clone(draft),
        groups = new Map();
      if (!s || !province || P[province].impassable) return;
      for (const i of provincesByState.get(s.index)) {
        const t = i === province ? tag : owners[i];
        if (!t) continue;
        if (!groups.has(t)) groups.set(t, []);
        groups.get(t).push(P[i].hex);
      }
      next.states ??= {};
      const old = next.states[s.id];
      next.states[s.id] = {
        ...(safeObject(old) ? old : {}),
        split: [...groups].map(([owner, provinces]) => ({ owner, provinces })),
      };
      delete next.states[s.id].owner;
      mutate(
        next,
        P[province].hex + " → " + tag + ". Diğer il payları korundu.",
      );
    } catch (e) {
      status(e.message, true);
    }
  };
  $("scenario-title").onchange = () => {
    const next = clone(draft);
    next.title = $("scenario-title").value.trim() || "Yeni senaryo";
    mutate(next, "Senaryo adı güncellendi.");
  };
  $("add-country").onclick = () => {
    const tag = $("new-tag").value.trim().toUpperCase(),
      name = $("new-name").value.trim(),
      hex = $("new-color").value;
    if (!/^(?=.*[A-Z])[A-Z0-9]{2,4}$/.test(tag) || !name) {
      status("2–4 karakterli ülke etiketi ve görünen ad gerekli.", true);
      return;
    }
    const next = clone(draft);
    next.countries ??= {};
    next.countries[tag] = {
      ...next.countries[tag],
      name,
      name_tr: name,
      color: [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)),
    };
    mutate(
      next,
      tag +
        " taslağa eklendi. Oyuna aktarırken kültür, başkent ve diğer tanımları tamamlayın.",
    );
  };
  $("undo").onclick = () => {
    if (!history.length) return;
    future.push(clone(draft));
    draft = history.pop();
    refresh();
    status("Son değişiklik geri alındı.");
  };
  $("redo").onclick = () => {
    if (!future.length) return;
    history.push(clone(draft));
    draft = future.pop();
    refresh();
    status("Değişiklik yinelendi.");
  };
  $("reset").onclick = () =>
    mutate(
      clone(initial),
      "Başlangıç taslağına dönüldü. Geri al ile kurtarabilirsiniz.",
    );
  document.addEventListener("keydown", (e) => {
    if (
      (e.ctrlKey || e.metaKey) &&
      e.key.toLowerCase() === "z" &&
      !e.target.matches("input,textarea")
    ) {
      e.preventDefault();
      $(e.shiftKey ? "redo" : "undo").click();
    }
  });
  $("export").onclick = () => {
    download("scenario.json", JSON.stringify(draft, null, 2));
    status(
      "Senaryo indirildi. CLI: .venv/bin/python tools/tgc.py atlas --scenario scenario.json",
    );
  };
  $("import").onclick = () => $("file").click();
  $("file").onchange = async () => {
    const f = $("file").files[0];
    if (!f) return;
    try {
      if (f.size > 8 * 1024 * 1024)
        throw Error("Senaryo dosyası 8 MB sınırını aşıyor.");
      const parsed = parseDocument(await f.text());
      mutate(parsed, "Senaryo yüklendi ve harita güncellendi.");
    } catch (e) {
      status("Dosya açılamadı: " + e.message, true);
    } finally {
      $("file").value = "";
    }
  };
  function context() {
    const result = { ...D };
    for (const k of [
      "provinces",
      "palettes",
      "hitImage",
      "beforePalette",
      "fingerprint",
      "catalog_states",
    ])
      delete result[k];
    result.scenario = draft;
    if (JSON.stringify(draft) !== JSON.stringify(initial)) {
      result.development = null;
      result.warnings = [...result.warnings, "Development report invalidated by edits. Run scenario report on the exported draft."];
    }
    result.countries = countries;
    result.title = draft.title;
    result.states = D.states.map((s) => {
      const groups = new Map();
      for (const i of provincesByState.get(s.index) || []) {
        const t = owners[i];
        if (t) {
          if (!groups.has(t)) groups.set(t, []);
          groups.get(t).push(P[i].hex);
        }
      }
      return {
        ...s,
        changed: stateChanged(s),
        owners: [...groups].map(([tag, provinces]) => ({ tag, provinces })),
      };
    });
    const tags = new Set(
      result.states.flatMap((s) =>
        [...s.owners, ...s.before].map((o) => o.tag),
      ),
    );
    for (const t of Object.keys(draft.countries || {})) tags.add(t);
    result.country_tags = Object.keys(countries).sort();
    result.countries = Object.fromEntries(
      Object.entries(countries).filter(([t]) => tags.has(t)),
    );
    delete result.base_countries;
    delete result.before_countries;
    return result;
  }
  $("context").onclick = () => {
    download("atlas-context.json", JSON.stringify(context(), null, 2));
    status(
      "Güncel eyaletler, gerçek il kimlikleri ve senaryo LLM bağlamına aktarıldı.",
    );
  };
  $("prompt").onclick = async () => {
    const text =
      "Bu Victoria 3 modu için hayali senaryomu geliştir. Eklediğim atlas-context.json dosyasını gerçek eyalet, ülke ve il kimliklerinin kaynağı olarak kullan. Kimlik uydurma. Önce tools/LLM_SCENARIO_WORKFLOW.md dosyasını oku. Senaryomu version: 2 içeren scenario.json olarak üret; countries, states, subject_types ve diplomacy alanlarını kullan. tools/tgc.py rules ve scenario schema ile gerçek kimlik ve sözleşmeyi sorgula. Nüfus, okuryazarlık, kültür/din oranları, binalar, üretim yöntemleri, şirketler, teknoloji, kanunlar, kurumlar, çıkar grupları, ordu/donanma ve bağlılıkları senaryoya göre birlikte düşün. Önce scenario validate, sonra scenario report ve scenario build ile ayrı önizleme üret. countries alanı ülke özelliklerini birleştirir; states alanı mevcut sahiplik planını değiştirir. Bölünmede owner ve provinces kullan; kalan illeri tek bir rest: true payıyla tamamla. Kapsam dışındaki yerler için önce tgc.py catalog ile veri edin. Sonucu .venv/bin/python tools/tgc.py atlas --scenario scenario.json ve .venv/bin/python tools/tgc.py map --scenario scenario.json --mode changes --data ile doğrula. Harita önizlemesinin olay veya save simülasyonu olmadığını dikkate al. world/ dosyalarına entegrasyondan sonra build ve check çalıştır. Senaryom: ";
    try {
      await navigator.clipboard.writeText(text);
      status(
        "LLM yönergesi kopyalandı. atlas-context.json dosyasını da ekleyin.",
      );
    } catch {
      download("llm-prompt.txt", text, "text/plain");
      status("Panoya erişilemedi; yönerge metin dosyası olarak indirildi.");
    }
  };
  $("png").onclick = () => {
    const out = document.createElement("canvas");
    out.width = width;
    out.height = height + 92;
    const c = out.getContext("2d");
    c.fillStyle = "#142028";
    c.fillRect(0, 0, out.width, out.height);
    c.fillStyle = "#eedfb9";
    c.font = "24px Georgia";
    c.fillText((draft.title || D.title).slice(0, 100), 20, 35);
    c.fillStyle = "#c2d1d7";
    c.font = "14px Arial";
    c.fillText(
      $("mode").selectedOptions[0].text +
        " · 1836 kaynak önizlemesi · Önce: " +
        D.baseline +
        " (%" +
        $("compare").value +
        ")",
      20,
      63,
    );
    c.drawImage(canvas, 0, 92);
    if ($("labels").checked) {
      c.font = "13px Arial";
      c.fillStyle = "#172229";
      c.strokeStyle = "#f5f3ee";
      c.lineWidth = 3;
      c.textAlign = "center";
      for (const label of $("map-labels").children) {
        const x = (Number(label.getAttribute("x")) - tx) / scale,
          y = (Number(label.getAttribute("y")) - ty) / scale + 92;
        c.strokeText(label.textContent, x, y);
        c.fillText(label.textContent, x, y);
      }
    }
    const a = el("a");
    a.download = "scenario-map.png";
    a.href = out.toDataURL("image/png");
    a.click();
    status("Harita PNG olarak indirildi.");
  };
  $("baseline").textContent = "(" + D.baseline + ")";
  $("warnings").replaceChildren(...D.warnings.map((w) => el("li", w)));
  for (const region of [...new Set(D.states.map((s) => s.region))].sort()) {
    const o = el("option", region);
    o.value = region;
    $("region").append(o);
  }
  try {
    const saved = localStorage.getItem(storageKey);
    if (saved) draft = validated(JSON.parse(saved));
  } catch {
    status(
      "Yerel taslak okunamadı; atlasın başlangıç senaryosu kullanılıyor.",
      true,
    );
  }
  refresh();
  const image = new Image();
  image.onload = () => {
    width = image.width;
    height = image.height;
    canvas.width = width;
    canvas.height = height;
    const off = document.createElement("canvas");
    off.width = width;
    off.height = height;
    const c = off.getContext("2d", { willReadFrequently: true });
    c.drawImage(image, 0, 0);
    hit = c.getImageData(0, 0, width, height).data;
    pixels = new Uint32Array(width * height);
    for (let i = 0; i < pixels.length; i++)
      pixels[i] = (hit[i * 4] << 16) | (hit[i * 4 + 1] << 8) | hit[i * 4 + 2];
    pixelCounts = new Uint32Array(P.length);
    for (const id of pixels) pixelCounts[id]++;
    hit = null;
    ready = true;
    $("loading").hidden = true;
    $("resolution").textContent = width + " × " + height + " · çevrimdışı";
    render();
    fit();
    status(
      "Atlas hazır. " +
        D.states.length +
        " eyalet; senaryo değişiklikleri oyun dosyalarına yazılmaz.",
    );
  };
  image.onerror = () => {
    $("loading").textContent =
      "Harita verisi okunamadı. Atlası CLI ile yeniden üretin.";
    status("Harita yüklenemedi.", true);
  };
  image.src = D.hitImage;
  new ResizeObserver(() => {
    if (ready) fit();
  }).observe(viewport);
})();
