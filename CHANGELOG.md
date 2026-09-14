# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-12

First public release. The firmware itself has been running on a built device
since November 2025; this is the point at which it became something another
person could reproduce.

### Added

- **UV index and illuminance on a 128×64 OLED**, redrawn a little under once a
  second. Characters are blitted at double size through a per-glyph framebuffer so
  both values stay readable at arm's length in sunlight.
- **An LTR390 driver** that reads both channels in one call by switching the
  sensor between UVS and ALS mode. Reading the status register immediately after
  each mode switch clears the data-ready flag, which is what forces the wait to
  block for a conversion taken in the new mode. Without it the stale flag from the
  previous mode satisfies the wait at once and the value returned belongs to the
  other channel — the readings look plausible and are wrong.
- **Errors drawn on the display**, not just printed to a serial port nobody is
  watching. `Init: FAIL` with the exception text when the sensor or screen is
  missing at startup, and a recoverable `Runtime Error` that pauses a second and
  carries on.
- **Documentation for the whole build**: [flashing](docs/flashing.md),
  [hardware](docs/hardware.md) with a wiring diagram,
  [measurement](docs/measurement.md), and symptom-first
  [troubleshooting](docs/troubleshooting.md).
- **A CI check that the pin numbers agree** across `src/main.py`,
  `docs/hardware.md` and the wiring diagram. Three places now have to say the same
  thing about four GPIOs, and nobody notices by eye when one of them moves.

### Fixed

- **`Init: FAIL` now reaches the screen.** The display is brought up before the
  sensor, so a missing or miswired sensor is reported on the OLED rather than only
  on a serial console nobody is watching.
- **Waiting for a conversion times out** after a second and raises the same
  `RuntimeError` the main loop already recovers from, instead of freezing the last
  frame for ever if the sensor stops answering.
- **Changing the resolution no longer resets the measurement rate**, because the
  driver now rewrites only the resolution bits of the shared register.
- **Corrected the documented pinout.** The working notes this project grew from
  recorded the sensor and the display as sharing one I²C bus on GPIO6 and GPIO7.
  They do not. The sensor is on a separate software bus on GPIO4 and GPIO3,
  because it would not respond on the hardware controller alongside the display.
  Following the old note produces a meter that never finds its sensor.

### Removed

- `import esp32` and `import machine` from `main.py`, left over from a deep-sleep
  experiment that was researched and abandoned. Neither was used.
