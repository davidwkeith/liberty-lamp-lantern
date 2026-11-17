"""Minimal KiCad schematic (.kicad_sch) generator — stdlib only.

Parts are placed unrotated on a grid and connected by local net labels placed
exactly on pin endpoints (no hand-routed wires). Symbols are embedded from the
installed KiCad libraries, falling back to the project library.
"""

from __future__ import annotations

import os
import re
import uuid as _uuid
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------- S-expressions


class Sym(str):
    """A bare (unquoted) S-expression atom."""


def parse(text: str):
    """Parse one S-expression (lists of Sym / str / numbers-as-Sym)."""
    tokens = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+', text)
    stack: list[list] = [[]]
    for tok in tokens:
        if tok == "(":
            stack.append([])
        elif tok == ")":
            done = stack.pop()
            stack[-1].append(done)
        elif tok.startswith('"'):
            stack[-1].append(bytes(tok[1:-1], "utf-8").decode("unicode_escape"))
        else:
            stack[-1].append(Sym(tok))
    return stack[0][0] if len(stack[0]) == 1 else stack[0]


def _atom(x) -> str:
    if isinstance(x, Sym):
        return str(x)
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, (int, float)):
        return _num(x)
    s = str(x).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{s}"'


def _num(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def dump(expr, indent: int = 0) -> str:
    """Serialize with one sub-list per line (KiCad accepts any whitespace)."""
    if not isinstance(expr, list):
        return _atom(expr)
    pad = "\t" * indent
    head = [_atom(x) for x in expr if not isinstance(x, list)]
    subs = [x for x in expr if isinstance(x, list)]
    if not subs:
        return "(" + " ".join(head) + ")"
    inner = "\n".join(pad + "\t" + dump(s, indent + 1) for s in subs)
    return "(" + " ".join(head) + "\n" + inner + "\n" + pad + ")"


def find(expr, key):
    """Direct child lists whose head is `key`."""
    return [x for x in expr if isinstance(x, list) and x and x[0] == key]


def find1(expr, key):
    got = find(expr, key)
    return got[0] if got else None


def walk(expr):
    yield expr
    for x in expr:
        if isinstance(x, list):
            yield from walk(x)


# ---------------------------------------------------------------- libraries

KICAD_SYMBOL_DIRS = [
    os.environ.get("KICAD_SYMBOL_DIR", ""),
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols",
    "/Library/Application Support/kicad/symbols",
    "/usr/share/kicad/symbols",
]
def kicad_cli() -> str | None:
    """kicad-cli from $KICAD_CLI, PATH, or the macOS app bundle."""
    import shutil
    for c in (os.environ.get("KICAD_CLI", ""), shutil.which("kicad-cli") or "",
              "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"):
        if c and Path(c).exists():
            return c
    return None


PROJECT_LIB = Path(__file__).resolve().parent.parent / "lib" / "liberty.kicad_sym"
_lib_cache: dict[str, list] = {}


def _lib_file(nickname: str) -> Path:
    if nickname == "liberty":
        return PROJECT_LIB
    for d in KICAD_SYMBOL_DIRS:
        if d and (p := Path(d) / f"{nickname}.kicad_sym").exists():
            return p
    raise FileNotFoundError(f"KiCad symbol library '{nickname}' not found in {KICAD_SYMBOL_DIRS}")


def _library(nickname: str) -> list:
    if nickname not in _lib_cache:
        _lib_cache[nickname] = parse(_lib_file(nickname).read_text())
    return _lib_cache[nickname]


def load_symbol(lib_id: str) -> list:
    """Return a flattened symbol definition named `lib_id` (e.g. 'Device:R')."""
    nick, name = lib_id.split(":", 1)
    lib = _library(nick)
    defs = {s[1]: s for s in find(lib, "symbol")}
    if name not in defs:
        raise KeyError(f"{lib_id} not in library")
    sym = defs[name]
    ext = find1(sym, "extends")
    if ext:
        parent = defs[ext[1]]
        props = {p[1]: p for p in find(sym, "property")}
        body = [x for x in parent[2:] if not (isinstance(x, list) and x and x[0] == "property")]
        # parent's unit sub-symbols are named "<parent>_u_v"; rename to child
        body = [_rename_units(x, ext[1], name) for x in body]
        merged_props = [props.get(p[1], p) for p in find(parent, "property")]
        merged_props += [p for k, p in props.items() if k not in {q[1] for q in merged_props}]
        sym = [Sym("symbol"), name] + merged_props + body
    out = [Sym("symbol"), lib_id] + [x for x in sym[2:]]
    return out


def _rename_units(x, old: str, new: str):
    if isinstance(x, list) and x and x[0] == "symbol" and isinstance(x[1], str) and x[1].startswith(old + "_"):
        return [x[0], new + x[1][len(old):]] + x[2:]
    return x


def symbol_pins(symdef: list, unit: int = 1) -> dict[str, dict]:
    """Pins of a symbol (unit 0 = common, plus `unit`): number → {x, y, type, name}."""
    pins = {}
    for sub in find(symdef, "symbol"):
        m = re.search(r"_(\d+)_(\d+)$", sub[1])
        if m and int(m.group(1)) not in (0, unit):
            continue
        for p in find(sub, "pin"):
            at = find1(p, "at")
            num = find1(p, "number")[1]
            name = find1(p, "name")[1]
            pins[num] = {"x": float(at[1]), "y": float(at[2]), "type": str(p[1]), "name": name}
    return pins


# ---------------------------------------------------------------- schematic


def _uid() -> str:
    return str(_uuid.uuid4())


@dataclass
class Part:
    ref: str
    lib_id: str
    value: str
    footprint: str
    at: tuple[float, float]
    fields: dict = field(default_factory=dict)
    unit: int = 1
    in_bom: bool = True

    @property
    def pins(self) -> dict[str, dict]:
        return symbol_pins(load_symbol(self.lib_id), self.unit)


def pin_endpoints(part: Part) -> dict[str, tuple[float, float]]:
    """Schematic coordinates of each pin's connection point (unrotated, unmirrored).

    Library coordinates are Y-up; schematic coordinates are Y-down.
    """
    x0, y0 = part.at
    return {n: (round(x0 + p["x"], 4), round(y0 - p["y"], 4)) for n, p in part.pins.items()}


class Sheet:
    def __init__(self, title: str, project: str, paper: str = "A3"):
        self.title, self.project, self.paper = title, project, paper
        self.parts: dict[str, Part] = {}
        self.nets: dict[tuple[str, str], str] = {}
        self.ncs: set[tuple[str, str]] = set()
        self.notes: list[tuple[str, float, float]] = []
        self.uuid = _uid()

    def add(self, ref, lib_id, value, footprint, at, **fields) -> Part:
        in_bom = fields.pop("in_bom", True)
        p = Part(ref, lib_id, value, footprint, (float(at[0]), float(at[1])), fields, in_bom=in_bom)
        self.parts[ref] = p
        return p

    def connect(self, ref: str, pin: str, net: str):
        """Label a pin by number, or by name with a leading '@' (e.g. '@PA7')."""
        self.nets[(ref, self.pin_number(ref, str(pin)))] = net

    def pin_number(self, ref: str, pin: str) -> str:
        if not pin.startswith("@"):
            return pin
        want = pin[1:]
        pins = self.parts[ref].pins
        exact = [n for n, p in pins.items() if p["name"] == want]
        loose = [n for n, p in pins.items() if want in re.split(r"[/ ]", p["name"])]
        hits = exact or loose
        if len(hits) != 1:
            raise KeyError(f"{ref}: pin name '{want}' matched {hits} among {[p['name'] for p in pins.values()]}")
        return hits[0]

    def no_connect(self, ref: str, pin: str):
        self.ncs.add((ref, self.pin_number(ref, str(pin))))

    def note(self, text: str, x: float, y: float):
        self.notes.append((text, x, y))

    def netlist(self) -> dict[str, set[tuple[str, str]]]:
        out: dict[str, set] = {}
        for (ref, pin), net in self.nets.items():
            out.setdefault(net, set()).add((ref, pin))
        return out

    def check(self):
        """Every pin labeled or no-connected; no pin both; no label on a missing pin."""
        problems = []
        for ref, part in self.parts.items():
            for num in part.pins:
                k = (ref, num)
                if k not in self.nets and k not in self.ncs:
                    problems.append(f"{ref}.{num} ({part.pins[num]['name']}) unconnected")
                if k in self.nets and k in self.ncs:
                    problems.append(f"{ref}.{num} both labeled and no-connect")
        for ref, num in list(self.nets) + list(self.ncs):
            if ref not in self.parts or num not in self.parts[ref].pins:
                problems.append(f"{ref}.{num} does not exist")
        if problems:
            raise ValueError("schematic check failed:\n  " + "\n  ".join(problems))

    # -- serialization

    def _symbol_instance(self, part: Part) -> list:
        x, y = part.at
        props = [("Reference", part.ref), ("Value", part.value), ("Footprint", part.footprint), ("Datasheet", part.fields.get("Datasheet", ""))]
        props += [(k, v) for k, v in part.fields.items() if k != "Datasheet"]
        prop_exprs = []
        for i, (k, v) in enumerate(props):
            hide = k not in ("Reference", "Value")
            # Keep text clear of the net labels that sit on pin ends: ref above, value below.
            dy = -7.62 if k == "Reference" else (7.62 if k == "Value" else 0)
            eff = [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]]]
            if hide:
                eff.append([Sym("hide"), Sym("yes")])
            prop_exprs.append([Sym("property"), k, v, [Sym("at"), x, y + dy, 0], eff])
        return [
            Sym("symbol"),
            [Sym("lib_id"), part.lib_id],
            [Sym("at"), x, y, 0],
            [Sym("unit"), part.unit],
            [Sym("exclude_from_sim"), Sym("no")],
            [Sym("in_bom"), Sym("yes" if part.in_bom else "no")],
            [Sym("on_board"), Sym("yes" if part.in_bom else "no")],
            [Sym("dnp"), Sym("no")],
            [Sym("uuid"), _uid()],
            *prop_exprs,
            *[[Sym("pin"), n, [Sym("uuid"), _uid()]] for n in part.pins],
            [Sym("instances"), [Sym("project"), self.project, [Sym("path"), "/" + self.uuid, [Sym("reference"), part.ref], [Sym("unit"), part.unit]]]],
        ]

    def to_sexpr(self) -> list:
        self.check()
        lib_ids = sorted({p.lib_id for p in self.parts.values()})
        items: list = [
            Sym("kicad_sch"),
            [Sym("version"), Sym("20250114")],
            [Sym("generator"), "liberty-gen"],
            [Sym("generator_version"), "1"],
            [Sym("uuid"), self.uuid],
            [Sym("paper"), self.paper],
            [Sym("title_block"), [Sym("title"), self.title], [Sym("company"), "Liberty Lamp"], [Sym("comment"), 1, "Generated by pcb/gen — edit boards.py, then run make pcb"]],
            [Sym("lib_symbols"), *[load_symbol(i) for i in lib_ids]],
        ]
        for part in self.parts.values():
            ends = pin_endpoints(part)
            for num, (px, py) in ends.items():
                key = (part.ref, num)
                if key in self.nets:
                    items.append([Sym("label"), self.nets[key], [Sym("at"), px, py, 0],
                                  [Sym("effects"), [Sym("font"), [Sym("size"), 1.0, 1.0]], [Sym("justify"), Sym("left"), Sym("bottom")]],
                                  [Sym("uuid"), _uid()]])
                elif key in self.ncs:
                    items.append([Sym("no_connect"), [Sym("at"), px, py], [Sym("uuid"), _uid()]])
            items.append(self._symbol_instance(part))
        for text, x, y in self.notes:
            items.append([Sym("text"), text, [Sym("exclude_from_sim"), Sym("no")], [Sym("at"), x, y, 0],
                          [Sym("effects"), [Sym("font"), [Sym("size"), 2.0, 2.0], [Sym("bold"), Sym("yes")]], [Sym("justify"), Sym("left"), Sym("bottom")]],
                          [Sym("uuid"), _uid()]])
        items.append([Sym("sheet_instances"), [Sym("path"), "/", [Sym("page"), "1"]]])
        return items

    def write(self, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dump(self.to_sexpr()) + "\n")
        pro = path.with_suffix(".kicad_pro")
        if not pro.exists():
            pro.write_text('{\n  "meta": {"filename": "%s", "version": 1},\n  "schematic": {},\n  "boards": [],\n  "sheets": [["%s", ""]]\n}\n' % (pro.name, self.uuid))
        table = path.parent / "sym-lib-table"
        if PROJECT_LIB.exists():
            _write_sym_lib_table(path.parent)
        elif table.exists():
            table.unlink()


def _write_sym_lib_table(project_dir: Path):
    rel = os.path.relpath(PROJECT_LIB, project_dir)
    (project_dir / "sym-lib-table").write_text(
        '(sym_lib_table\n\t(version 7)\n\t(lib (name "liberty")(type "KiCad")(uri "${KIPRJMOD}/%s")(options "")(descr "Liberty Lamp project symbols"))\n)\n' % rel
    )
