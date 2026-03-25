#!/usr/bin/env python3
"""
Generate a visual HTML cheat sheet from config/chocofi.keymap.
Usage: python3 cheatsheet.py [output.html]
Opens the result in the default browser.

Hover a key to see:
  - A legend of tap / hold / alt / double-tap actions
  - Arrows pointing to any layers that key activates
"""

import re
import sys
import webbrowser
from pathlib import Path

KEYMAP = Path(__file__).parent / "config" / "chocofi.keymap"
OUTPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "cheatsheet.html"

TOTAL = 36  # 3 rows × 10 cols + 6 thumbs

# ── Display labels ────────────────────────────────────────────────────────────

_KP: dict[str, str] = {
    **{c: c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
    **{f"N{i}": str(i) for i in range(10)},
    **{f"NUMBER_{i}": str(i) for i in range(10)},
    **{f"F{i}": f"F{i}" for i in range(1, 13)},
    "SPACE": "Spc",   "SPACEBAR": "Spc",
    "ENTER": "↵",     "RETURN": "↵",
    "BACKSPACE": "⌫", "BSPC": "⌫",
    "DELETE": "⌦",
    "TAB": "⇥",
    "ESCAPE": "Esc",  "ESC": "Esc",
    "LEFT_BRACKET":  "`·",
    "RIGHT_BRACKET": "+",
    "APOSTROPHE":    "´·",  "SINGLE_QUOTE": "´·",
    "BACKSLASH":     "ç",
    "GRAVE":         "º",
    "MINUS":         "'",
    "EQUAL":         "¡",
    "SLASH":         "-",
    "SEMI":          "ñ",   "SEMICOLON": ";",
    "COMMA": ",",    "DOT": ".", "PERIOD": ".",
    "NON_US_BACKSLASH": "<",
    "LEFT_SHIFT":   "⇧", "LSHIFT": "⇧", "LSHFT": "⇧",
    "RIGHT_SHIFT":  "⇧", "RSHIFT": "⇧", "RSHFT": "⇧",
    "LEFT_CONTROL": "⌃", "LCTRL": "⌃",  "LEFT_CTRL": "⌃",
    "RIGHT_CONTROL":"⌃", "RCTRL": "⌃",
    "LEFT_ALT":     "⌥", "LALT": "⌥",
    "RIGHT_ALT":    "⌥", "RALT": "⌥",
    "LEFT_GUI":     "⌘", "LGUI": "⌘",
    "RIGHT_GUI":    "⌘", "RGUI": "⌘",
    "LEFT": "←",  "LEFT_ARROW": "←",
    "RIGHT": "→", "RIGHT_ARROW": "→",
    "UP": "↑",    "UP_ARROW": "↑",
    "DOWN": "↓",  "DOWN_ARROW": "↓",
    "HOME": "Home", "END": "End",
    "PAGE_UP": "PgUp", "PAGE_DOWN": "PgDn",
    "C_VOL_UP": "Vol+",  "C_VOL_DN": "Vol-", "C_MUTE": "Mute",
    "C_PLAY_PAUSE": "⏯", "C_NEXT": "⏭",     "C_PREV": "⏮",
    "C_BRIGHTNESS_INC": "Bri+", "C_BRIGHTNESS_DEC": "Bri-",
    "C_BRIGHTNESS_AUTO": "BriA",
    "K_LOCK": "Lock", "K_COPY": "Copy", "K_PASTE": "Paste",
    "PRCNT": "%",
    "LT": "<", "GT": ">",
}

_ES: dict[str, str] = {
    "LS(N1)": "!",  "LS(N2)": '"',  "LS(N3)": "·",  "LS(N4)": "$",
    "LS(N5)": "%",  "LS(N6)": "&",  "LS(N7)": "/",  "LS(N8)": "(",
    "LS(N9)": ")",  "LS(N0)": "=",
    "RA(N1)": "|",  "RA(N2)": "@",  "RA(N3)": "#",
    "RA(N4)": "~",  "RA(N5)": "€",
    "RA(LEFT_BRACKET)":  "[",  "RA(RIGHT_BRACKET)": "]",
    "RA(APOSTROPHE)":    "{",  "RA(BACKSLASH)":     "}",
    "RA(GRAVE)":         "\\",
    "LS(MINUS)":              "?",
    "LS(SLASH)":              "_",
    "LS(LEFT_BRACKET)":       "^",
    "LS(RIGHT_BRACKET)":      "*",
    "LS(RA(N4))":             "£",
    "LS(NON_US_BACKSLASH)":   ">",
    "LG(RIGHT)": "⌘→", "LG(LEFT)": "⌘←", "LG(LEFT_ARROW)": "⌘←",
    "LG(Z)": "⌘Z",     "LS(LG(Z))": "⌘⇧Z",
    "LS(ENTER)": "⇧↵",
    "LA(RIGHT)": "⌥→", "LA(LEFT)": "⌥←",
    "LA(BACKSPACE)": "⌥⌫", "LA(DELETE)": "⌥⌦",
}

_NAMED: dict[str, str] = {
    "c_cedilla":          "ç",
    "punt_volat":         "·",
    "vim_o":              "o/O",
    "vim_backspace":      "⌥⌫",
    "end":                "⌘→",
    "grave_sym":          "`",
    "caret_sym":          "^",
    "acute_sym":          "´",
    "thin_arrow":         "->",
    "thic_arrow":         "=>",
    "gte":                ">=",
    "lte":                "<=",
    "esc_0":              "Esc",
    "vim_word":           "vw",
    "vim_I":              "^I",
    "next_line_enter":    "o",
    "previous_line_enter":"O",
    "caps_word":          "CaW",
    "key_repeat":         "Rep",
}

# Verbose descriptions used in tooltips
_NAMED_DESC: dict[str, str] = {
    "c_cedilla":          "c — Alt: ç",
    "punt_volat":         "l — Alt: ·",
    "vim_o":              "o (Shift: O — prev line)",
    "vim_backspace":      "⌥⌫ (Alt: ⌥⌦)",
    "end":                "⌘→ end of line",
    "grave_sym":          "` (standalone backtick)",
    "caret_sym":          "^ (standalone caret)",
    "acute_sym":          "´ (standalone acute)",
    "thin_arrow":         "-> thin arrow",
    "thic_arrow":         "=> thick arrow",
    "gte":                ">= greater or equal",
    "lte":                "<= less or equal",
    "esc_0":              "Esc → return to DEF",
    "vim_word":           "jump word (⌥→⌥→⌥←)",
    "vim_I":              "⌘← then exit VIM",
    "next_line_enter":    "open line below",
    "previous_line_enter":"open line above",
    "caps_word":          "Caps Word — auto-caps until space",
    "key_repeat":         "repeat last key",
}

_LAYERS: dict[int, str] = {
    0: "DEF", 1: "SYM", 2: "VIM",
    3: "FN_R", 4: "MED_R", 5: "MED_L", 6: "FN_L", 7: "NUM",
}

_MOD_SYM = {
    "LS":"⇧","RS":"⇧","LA":"⌥","RA":"⌥",
    "LG":"⌘","RG":"⌘","LC":"⌃","RC":"⌃",
}

_MOD_NAME = {
    "LEFT_SHIFT":"Shift","LSHIFT":"Shift","LSHFT":"Shift",
    "RIGHT_SHIFT":"Shift","RSHIFT":"Shift",
    "LEFT_CONTROL":"Ctrl","LCTRL":"Ctrl","LEFT_CTRL":"Ctrl",
    "RIGHT_CONTROL":"Ctrl","RCTRL":"Ctrl",
    "LEFT_ALT":"Alt/⌥","LALT":"Alt/⌥",
    "RIGHT_ALT":"Alt/⌥","RALT":"Alt/⌥",
    "LEFT_GUI":"Cmd/⌘","LGUI":"Cmd/⌘",
    "RIGHT_GUI":"Cmd/⌘","RGUI":"Cmd/⌘",
}

LAYER_COLORS = {
    "DEF":   "#1565C0", "SYM":   "#6A1B9A",
    "VIM":   "#B71C1C", "FN_R":  "#D84315",
    "MED_R": "#2E7D32", "MED_L": "#2E7D32",
    "FN_L":  "#D84315", "NUM":   "#00695C",
}

# ── Label helpers ─────────────────────────────────────────────────────────────

def kp_label(code: str) -> str:
    code = code.strip()
    compact = re.sub(r"\s+", "", code)
    if compact in _ES:
        return _ES[compact]
    if code in _KP:
        return _KP[code]
    if re.match(r"^[A-Z]$", code):
        return code
    m = re.match(r"^(LS|RS|LA|RA|LG|RG|LC|RC)\((.+)\)$", compact)
    if m:
        sym = _MOD_SYM.get(m.group(1), m.group(1))
        return sym + kp_label(m.group(2))
    return code[:5]


def mod_name(code: str) -> str:
    return _MOD_NAME.get(code, kp_label(code))


# ── Binding parser ────────────────────────────────────────────────────────────
# Each cell is a dict with:
#   top, bot        – display labels
#   behavior        – ZMK behavior name
#   tap, hold, alt  – tooltip strings (or None)
#   dtap            – double-tap description (or None)
#   layer           – target layer int (or None)

def binding_cell(tokens: list[str], pos: int) -> tuple[dict, int]:
    if pos >= len(tokens):
        return {"top":"?","bot":"","behavior":"?","tap":None,"hold":None,"alt":None,"dtap":None,"layer":None}, pos+1

    tok = tokens[pos]
    if not tok.startswith("&"):
        return {"top":tok[:5],"bot":"","behavior":"raw","tap":tok,"hold":None,"alt":None,"dtap":None,"layer":None}, pos+1

    beh = tok[1:]

    def p(offset=1):
        return tokens[pos + offset] if pos + offset < len(tokens) else "?"

    # cell() already returns (dict, pos+advance) — never append ", pos+N" after calling it
    def cell(top, bot="", tap=None, hold=None, alt=None, dtap=None, layer=None, advance=1):
        return {"top":top,"bot":bot,"behavior":beh,
                "tap":tap or top,"hold":hold,"alt":alt,"dtap":dtap,"layer":layer}, pos+advance

    # ── Zero-param ──────────────────────────────────────────────────────────
    if beh == "trans":
        return cell("▽", tap="(transparent — inherits layer below)")
    if beh == "none":
        return cell("", tap="(no action)")
    if beh == "sys_reset":
        return cell("RST", tap="Reset firmware")
    if beh == "bootloader":
        return cell("Boot", tap="Enter bootloader (flash mode)")
    if beh == "key_repeat":
        return cell("Rep", tap="Repeat last key")
    if beh == "caps_word":
        return cell("CaW", tap="Caps Word — capitalises until space/punctuation")
    if beh in _NAMED:
        desc = _NAMED_DESC.get(beh, _NAMED[beh])
        return cell(_NAMED[beh], tap=desc)

    # ── One-param ───────────────────────────────────────────────────────────
    if beh == "kp":
        lbl = kp_label(p())
        return cell(lbl, tap=lbl, advance=2)

    if beh == "to":
        try: n = int(p())
        except ValueError: n = -1
        name = _LAYERS.get(n, f"L{n}")
        return cell(f"→{name}", tap=f"Switch to {name} layer (latching)", layer=n, advance=2)

    if beh == "kt":
        lbl = kp_label(p())
        return cell(f"⇣{lbl}", tap=f"Toggle {lbl} key held", advance=2)

    if beh == "out":
        label = {"OUT_USB":"USB","OUT_BLE":"BLE"}.get(p(), p())
        desc  = {"OUT_USB":"Force USB output","OUT_BLE":"Force BLE output"}.get(p(), p())
        return cell(label, tap=desc, advance=2)

    # ── Two-param ───────────────────────────────────────────────────────────
    if beh == "lt":
        try: n = int(p(1))
        except ValueError: n = -1
        key  = p(2)
        lbl  = kp_label(key)
        name = _LAYERS.get(n, f"L{n}")
        return cell(
            lbl, bot=name,
            tap=lbl,
            hold=f"→ {name} layer",
            dtap=f"Repeat {lbl} (quick-tap)",
            layer=n,
            advance=3,
        )

    if beh in ("hm", "shift_tap", "mt"):
        mod = p(1); key = p(2)
        lbl = kp_label(key); mname = mod_name(mod)
        return cell(
            lbl, bot=kp_label(mod),
            tap=lbl,
            hold=mname,
            dtap=f"Repeat {lbl} (quick-tap)",
            advance=3,
        )

    if beh == "hm_l":
        mod = p(1)
        mname = mod_name(mod)
        return cell(
            "l/·", bot=kp_label(mod),
            tap="l — Alt while tapping: · (punt volat)",
            hold=mname,
            dtap="Repeat l (quick-tap)",
            advance=3,
        )

    # ── BT ──────────────────────────────────────────────────────────────────
    if beh == "bt":
        action = p(1)
        if action == "BT_SEL":
            n = p(2)
            return cell(f"BT{n}", tap=f"Select Bluetooth profile {n}", advance=3)
        if action == "BT_CLR":
            return cell("BT✕", tap="Clear current Bluetooth pairing", advance=2)
        return cell("BT", tap=action, advance=2)

    # Fallback
    return cell(beh[:6], tap=beh)


# ── Keymap parser ─────────────────────────────────────────────────────────────

def extract_block(text: str, start: int) -> tuple[str, int]:
    depth = 0
    for i, c in enumerate(text[start:], start):
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start:i+1], i+1
    return text[start:], len(text)


def parse_layers(keymap_text: str) -> list[tuple[str, list[dict]]]:
    text = re.sub(r"//[^\n]*", "", keymap_text)

    km_m = re.search(r"\bkeymap\s*\{", text)
    if not km_m:
        sys.exit("Could not find 'keymap { }' block.")
    km_block, _ = extract_block(text, km_m.start() + km_m.group().index("{"))
    inner = km_block[km_block.index("{")+1:-1]

    layers = []
    pos = 0
    while pos < len(inner):
        m = re.match(r"\s*(\w+)\s*\{", inner[pos:])
        if not m:
            pos += 1
            continue
        layer_name = m.group(1)
        brace_pos  = pos + m.start() + m.group().rindex("{")
        block, end = extract_block(inner, brace_pos)
        pos = brace_pos + len(block)

        bm = re.search(r"bindings\s*=\s*<(.*?)>", block, re.DOTALL)
        if not bm:
            continue

        tokens = bm.group(1).split()
        cells, ti = [], 0
        while ti < len(tokens) and len(cells) < TOTAL:
            if tokens[ti].startswith("&"):
                cell, ti = binding_cell(tokens, ti)
                cells.append(cell)
            else:
                ti += 1
        layers.append((layer_name, cells))

    return layers


# ── HTML renderer ─────────────────────────────────────────────────────────────

KEY_W, KEY_H, GAP  = 52, 46, 4
HALF_GAP           = 18
THUMB_INDENT       = 2 * (KEY_W + GAP)


def esc(s: str) -> str:
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")


def key_html(cell: dict, color: str, lid: int) -> str:
    top, bot = cell["top"], cell["bot"]
    cls = "key"
    if top == "▽": cls += " trans"
    elif top == "": cls += " empty"

    data = f'data-behavior="{esc(cell["behavior"])}" data-lid="{lid}"'
    if cell.get("tap"):  data += f' data-tap="{esc(cell["tap"])}"'
    if cell.get("hold"): data += f' data-hold="{esc(cell["hold"])}"'
    if cell.get("alt"):  data += f' data-alt="{esc(cell["alt"])}"'
    if cell.get("dtap"): data += f' data-dtap="{esc(cell["dtap"])}"'
    if cell.get("layer") is not None:
        data += f' data-target-layer="{cell["layer"]}"'

    bot_html = f'<span class="sub">{esc(bot)}</span>' if bot else ""
    return (
        f'<div class="{cls}" style="--accent:{color}" {data}>'
        f'<span class="main">{esc(top)}</span>{bot_html}</div>'
    )


def layer_html(name: str, cells: list[dict], index: int) -> str:
    display = name.replace("default_layer", "DEF")
    short   = next((v for k,v in _LAYERS.items() if v == display), display)
    color   = LAYER_COLORS.get(short, LAYER_COLORS.get(display, "#444"))

    def row_html(keys):
        lh = "".join(key_html(c, color, index) for c in keys[:5])
        rh = "".join(key_html(c, color, index) for c in keys[5:10])
        return (f'<div class="row">'
                f'<div class="half">{lh}</div>'
                f'<div class="half-gap"></div>'
                f'<div class="half">{rh}</div>'
                f'</div>')

    rows  = "".join(row_html(cells[r*10:(r+1)*10]) for r in range(3))
    tl    = "".join(key_html(c, color, index) for c in cells[30:33])
    tr    = "".join(key_html(c, color, index) for c in cells[33:36])
    thumb = (f'<div class="thumb-row">'
             f'<div class="thumb-half">{tl}</div>'
             f'<div class="half-gap"></div>'
             f'<div class="thumb-half">{tr}</div>'
             f'</div>')

    return (f'<section class="layer" id="layer-{index}" data-layer-id="{index}"'
            f' style="--layer-color:{color}">'
            f'<div class="layer-title" style="background:{color}">{esc(display)}</div>'
            f'<div class="keyboard">{rows}{thumb}</div>'
            f'</section>')


# ── CSS & JS ──────────────────────────────────────────────────────────────────

CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: system-ui, -apple-system, sans-serif;
    background: #111827;
    color: #e5e7eb;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}}
h1 {{
    font-size: 13px;
    color: #6b7280;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
.layer {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: fit-content;
    border-radius: 10px;
    padding: 8px;
    border: 2px solid transparent;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.layer.arrow-target {{
    border-color: var(--layer-color);
    box-shadow: 0 0 18px -4px var(--layer-color);
}}
.layer-title {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 4px;
    color: #fff;
    width: fit-content;
}}
.keyboard {{
    display: flex;
    flex-direction: column;
    gap: {GAP}px;
}}
.row {{
    display: flex;
    gap: {GAP}px;
    align-items: stretch;
}}
.half, .thumb-half {{
    display: flex;
    gap: {GAP}px;
}}
.half-gap {{
    width: {HALF_GAP}px;
    flex-shrink: 0;
}}
.thumb-row {{
    display: flex;
    gap: {GAP}px;
    align-items: stretch;
    padding-left: {THUMB_INDENT}px;
}}
.key {{
    width: {KEY_W}px;
    height: {KEY_H}px;
    background: #1f2937;
    border: 1px solid #374151;
    border-bottom: 3px solid var(--accent, #374151);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    flex-shrink: 0;
    cursor: default;
    transition: background 0.1s, transform 0.1s;
    position: relative;
}}
.key:hover {{
    background: #263548;
    transform: translateY(-1px);
}}
.key.trans {{
    background: transparent;
    border-color: #1f2937;
    border-bottom-color: #1f2937;
    opacity: 0.3;
}}
.key.empty {{
    background: transparent;
    border: 1px dashed #1f2937;
}}
.main {{
    font-size: 13px;
    font-weight: 600;
    color: #f9fafb;
    line-height: 1;
    user-select: none;
}}
.sub {{
    font-size: 9px;
    font-weight: 600;
    color: var(--accent, #6b7280);
    line-height: 1;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    user-select: none;
}}

/* ── Tooltip ── */
#tooltip {{
    position: fixed;
    z-index: 1000;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 12px;
    min-width: 160px;
    max-width: 260px;
    pointer-events: none;
    display: none;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}}
.tt-row {{
    display: flex;
    align-items: baseline;
    gap: 8px;
    padding: 3px 0;
}}
.tt-row + .tt-row {{
    border-top: 1px solid #1e293b;
}}
.tt-mode {{
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    min-width: 60px;
    flex-shrink: 0;
}}
.tt-val {{
    font-size: 12px;
    color: #e2e8f0;
    line-height: 1.3;
}}

/* ── Arrow SVG overlay ── */
#arrow-svg {{
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 500;
    overflow: visible;
}}
"""

JS = """
const tooltip = document.getElementById('tooltip');
const arrowSvg = document.getElementById('arrow-svg');

let activeArrows = [];

function clearArrows() {
    activeArrows.forEach(el => el.remove());
    activeArrows = [];
    document.querySelectorAll('.layer.arrow-target').forEach(l => l.classList.remove('arrow-target'));
}

function drawArrow(fromEl, toEl, color) {
    const fr = fromEl.getBoundingClientRect();
    const tr = toEl.getBoundingClientRect();

    const x1 = fr.left + fr.width / 2;
    const y1 = fr.top + window.scrollY;
    const x2 = tr.left + 12;
    const y2 = tr.top + tr.height / 2 + window.scrollY;

    const cp1x = x1;
    const cp1y = (y1 + y2) / 2;
    const cp2x = x2 - 60;
    const cp2y = y2;

    // Marker
    const markerId = `arrow-${Math.random().toString(36).slice(2)}`;
    const defs = document.createElementNS('http://www.w3.org/2000/svg','defs');
    defs.innerHTML = `<marker id="${markerId}" markerWidth="8" markerHeight="8"
        refX="6" refY="3" orient="auto">
        <path d="M0,0 L0,6 L8,3 z" fill="${color}" opacity="0.85"/>
    </marker>`;

    const path = document.createElementNS('http://www.w3.org/2000/svg','path');
    path.setAttribute('d', `M ${x1} ${y1} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${x2} ${y2}`);
    path.setAttribute('stroke', color);
    path.setAttribute('stroke-width', '2');
    path.setAttribute('stroke-dasharray', '5,3');
    path.setAttribute('fill', 'none');
    path.setAttribute('opacity', '0.8');
    path.setAttribute('marker-end', `url(#${markerId})`);

    arrowSvg.appendChild(defs);
    arrowSvg.appendChild(path);
    activeArrows.push(defs, path);
}

function positionTooltip(keyEl) {
    const rect  = keyEl.getBoundingClientRect();
    const tw    = tooltip.offsetWidth;
    const th    = tooltip.offsetHeight;
    const vw    = window.innerWidth;
    const vh    = window.innerHeight;

    let left = rect.left + rect.width / 2 - tw / 2;
    let top  = rect.bottom + 8;

    if (left + tw > vw - 8) left = vw - tw - 8;
    if (left < 8) left = 8;
    if (top + th > vh - 8) top = rect.top - th - 8;

    tooltip.style.left = left + 'px';
    tooltip.style.top  = top  + 'px';
}

document.querySelectorAll('.key').forEach(key => {
    key.addEventListener('mouseenter', () => {
        const beh  = key.dataset.behavior;
        const tap  = key.dataset.tap;
        const hold = key.dataset.hold;
        const alt  = key.dataset.alt;
        const dtap = key.dataset.dtap;

        if (!tap && !hold && !alt && !dtap) return;

        const rows = [];
        if (tap)  rows.push(['Tap',        tap]);
        if (hold) rows.push(['Hold',       hold]);
        if (alt)  rows.push(['Alt',        alt]);
        if (dtap) rows.push(['Double-tap', dtap]);

        tooltip.innerHTML = rows.map(([mode, val]) =>
            `<div class="tt-row">
                <span class="tt-mode">${mode}</span>
                <span class="tt-val">${val}</span>
            </div>`
        ).join('');

        tooltip.style.display = 'block';
        positionTooltip(key);

        // Layer arrows
        const targetLayer = key.dataset.targetLayer;
        if (targetLayer !== undefined) {
            const layerEl = document.getElementById('layer-' + targetLayer);
            if (layerEl) {
                layerEl.classList.add('arrow-target');
                const titleEl = layerEl.querySelector('.layer-title');
                const accentColor = getComputedStyle(layerEl).getPropertyValue('--layer-color').trim();
                if (titleEl) drawArrow(key, titleEl, accentColor || '#888');
            }
        }
    });

    key.addEventListener('mouseleave', () => {
        tooltip.style.display = 'none';
        clearArrows();
    });
});

// Reposition tooltip on scroll
window.addEventListener('scroll', () => {
    if (tooltip.style.display !== 'none') {
        const hovered = document.querySelector('.key:hover');
        if (hovered) positionTooltip(hovered);
    }
    clearArrows();
}, { passive: true });
"""


def generate_html(layers: list[tuple[str, list[dict]]]) -> str:
    sections = "\n".join(
        layer_html(name, cells, i) for i, (name, cells) in enumerate(layers)
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Chocofi Cheat Sheet</title>
<style>{CSS}</style>
</head>
<body>
<h1>Chocofi Keymap — hover any key for details</h1>
{sections}
<div id="tooltip"></div>
<svg id="arrow-svg" xmlns="http://www.w3.org/2000/svg"></svg>
<script>{JS}</script>
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    text   = KEYMAP.read_text(encoding="utf-8")
    layers = parse_layers(text)
    if not layers:
        sys.exit("No layers found — check keymap path.")
    html = generate_html(layers)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Written: {OUTPUT}")
    if not os.environ.get("CI"):
        webbrowser.open(OUTPUT.as_uri())

if __name__ == "__main__":
    main()
