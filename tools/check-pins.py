#!/usr/bin/env python3
"""Check that the code, the wiring table and the diagram agree about pins.

Four GPIO numbers are written down in three places: the constants in
src/main.py, the wiring table in docs/hardware.md, and the labels in
docs/img/wiring.svg. The working notes this project grew from already drifted
once and claimed the sensor and the display shared one I2C bus, which sends
anyone following them to a meter that never finds its sensor. Nobody spots that
by eye, so it is checked here instead.

The XIAO silkscreen names are checked too, against the board's own pin map, so
that a table saying "D1 / GPIO4" fails rather than being copied onto somebody's
soldering iron.
"""

import ast
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Seeed Studio XIAO ESP32-C3, silkscreen name to GPIO number.
XIAO_PINS = {"D0": 2, "D1": 3, "D2": 4, "D3": 5, "D4": 6,
             "D5": 7, "D6": 21, "D7": 20, "D8": 8, "D9": 9, "D10": 10}

CONSTANTS = {"PIN_LTR_SCL": ("LTR390", "SCL"), "PIN_LTR_SDA": ("LTR390", "SDA"),
             "PIN_OLED_SCL": ("OLED", "SCL"), "PIN_OLED_SDA": ("OLED", "SDA")}

# A label is treated as belonging to the wire whose pin name sits within this
# many user units of it vertically. SCL and SDA are 30 apart in the diagram, so
# the gap is unambiguous until somebody redraws it much tighter.
ROW_TOLERANCE = 15


def from_code():
    tree = ast.parse((ROOT / "src" / "main.py").read_text(encoding="utf-8"))
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in CONSTANTS:
                    found[CONSTANTS[target.id]] = node.value.value
    return found


def from_table():
    text = (ROOT / "docs" / "hardware.md").read_text(encoding="utf-8")
    found = {}
    for line in text.splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) != 4 or not re.fullmatch(r"GPIO\d+", cells[3]):
            continue
        device = "LTR390" if "LTR390" in cells[0] else "OLED"
        signal = "SCL" if "SCL" in cells[0] else "SDA"
        found[(device, signal)] = (cells[2], int(cells[3][4:]))
    return found


def from_diagram():
    """Pair each GPIO label in the SVG with the pin names drawn beside it.

    Sides are taken from x order rather than fixed coordinates: the sensor is
    drawn left of the display, and the labels for one bus are the two nearest
    that side. Signals are then matched by vertical proximity.
    """
    labels = []
    for el in ET.parse(ROOT / "docs" / "img" / "wiring.svg").iter():
        if el.tag.endswith("text") and el.text:
            labels.append((float(el.get("x")), float(el.get("y")), el.text.strip()))

    def pick(pattern):
        hits = sorted((x, y, t) for x, y, t in labels if re.fullmatch(pattern, t))
        if len(hits) != 4:
            raise SystemExit(f"wiring.svg: expected 4 labels matching {pattern}, "
                             f"found {len(hits)}")
        return {"LTR390": hits[:2], "OLED": hits[2:]}

    gpios, signals, dpins = pick(r"GPIO\d+"), pick(r"SCL|SDA"), pick(r"D\d")

    found = {}
    for device in ("LTR390", "OLED"):
        for gx, gy, gtext in gpios[device]:
            near = [t for _, y, t in signals[device] if abs(y - gy) <= ROW_TOLERANCE]
            pin = [t for _, y, t in dpins[device] if abs(y - gy) <= ROW_TOLERANCE]
            if len(near) != 1 or len(pin) != 1:
                raise SystemExit(f"wiring.svg: {gtext} is not clearly beside one "
                                 f"signal and one pin name")
            found[(device, near[0])] = (pin[0], int(gtext[4:]))
    return found


def main():
    code, table, diagram = from_code(), from_table(), from_diagram()
    problems = []

    for key in sorted(CONSTANTS.values()):
        device, signal = key
        where = f"{device} {signal}"

        if key not in code:
            problems.append(f"{where}: no constant in src/main.py")
            continue
        gpio = code[key]

        for name, source in (("docs/hardware.md", table), ("wiring.svg", diagram)):
            if key not in source:
                problems.append(f"{where}: missing from {name}")
                continue
            pin, said = source[key]
            if said != gpio:
                problems.append(f"{where}: src/main.py says GPIO{gpio}, "
                                f"{name} says GPIO{said}")
            if XIAO_PINS.get(pin) != said:
                problems.append(f"{where}: {name} pairs {pin} with GPIO{said}, "
                                f"but {pin} is GPIO{XIAO_PINS.get(pin, '?')} "
                                f"on the XIAO ESP32-C3")

    if problems:
        print("Pin definitions disagree:")
        for p in problems:
            print("  " + p)
        return 1

    for (device, signal), gpio in sorted(code.items()):
        print(f"{device} {signal}: GPIO{gpio} - code, table and diagram agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
