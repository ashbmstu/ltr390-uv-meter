# Contributing to ltr390-uv-meter

Thank you for considering a contribution. This is a small piece of firmware for a
specific set of parts, and most changes to it only mean anything on a real device.

## Before you open a pull request

There is no simulator. CI checks that the files parse, that the pin numbers agree
across the code and the documentation, and that the links in the documentation
resolve — it cannot read a sensor or light a display. Anything beyond that has to
be tried on hardware.

If your change touches the measurement path, say in the pull request what you saw
on the screen before and after, and under what light. A reading taken next to a
calibrated meter is worth a great deal more than an argument about the arithmetic.

## Running the checks locally

```bash
python -m compileall -q src tools
python tools/check-pins.py
```

## Code style

- MicroPython, 4-space indent, no tabs.
- `snake_case` for functions and variables.
- Match the style of the existing files in `src/`.
- Comments explain why, not what. Most of this code needs none; the two that are
  there mark places where the obvious change is the wrong one.

`src/ssd1306.py` is carried unmodified from the MicroPython project so that it can
be checked against upstream. Please do not edit it. If the display needs different
behaviour, do it in `main.py`.

## Commit messages

Use an imperative subject line under about 72 characters, with no type prefix. In
the body, explain the reasoning. When a change comes from something you measured,
say what you measured and with what, so a reviewer can follow the trail.

## Reporting a problem with a device you built

Useful reports include:

- What the screen shows, exactly, including any error text
- MicroPython version (`import sys; sys.implementation` at the REPL)
- Which LTR390 breakout and which OLED module, and where they came from
- The output of an I²C scan on both buses — see
  [troubleshooting.md](docs/troubleshooting.md#the-screen-shows-init-fail)
- Whether it is running from USB or from the cell
- Indoors or outdoors, and roughly how bright

Open bugs through GitHub Issues on this repository.
