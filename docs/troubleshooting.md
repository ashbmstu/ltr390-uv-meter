# Troubleshooting

Arranged by what you see, not by what is wrong.

## The screen stays completely dark

Nothing is reaching the display. In order of likelihood:

- **The switch is off**, or its centre pin is not the one wired to the battery. A
  3-pin slide switch connects the centre pin to one outer pin; the battery lead
  must go to the centre.
- **`VCC` and `GND` are swapped** at the display. Most SSD1306 modules survive
  this, but they do not light up.
- **`SDA` and `SCL` are swapped.** The display needs `SCL` on `D5` (GPIO7) and
  `SDA` on `D4` (GPIO6). Every generic module labels these differently from its
  neighbours; trust the silkscreen on the module, not the colour of the wire.
- **The files are not on the board**, or are inside a folder. Connect Thonny and
  check that `main.py`, `ltr390.py` and `ssd1306.py` are all at the top level.

Plug the board into a computer and open the Thonny console. If MicroPython is
running you get a traceback, which names the problem directly.

## The screen shows `Init: FAIL`

The display works and the sensor does not. The second line is the error.

**`Failed to find LTR390 sensor`** — the sensor did not answer at address `0x53`.
Check `SCL` on `D2` (GPIO4) and `SDA` on `D1` (GPIO3), and check `VIN` is on `3V3`
rather than `5V`. This is the most common mistake: the two I²C buses are easy to
cross, and the sensor on the display's pins looks perfectly plausible.

Scan the bus from the Thonny console to see what is actually out there:

```python
from machine import Pin, SoftI2C
SoftI2C(scl=Pin(4), sda=Pin(3)).scan()
```

`[83]` is the LTR390 at `0x53`. An empty list means the wiring is wrong, not the
sensor.

**`[Errno 19] ENODEV`** or a similar OSError — the bus pins are not connected at
all, or a joint is dry.

## `Runtime Error` appears after it has been working

A read failed mid-loop. The firmware draws the error, waits a second and carries
on, so an occasional one is survivable; a constant one is a bad joint that has
gone intermittent. Wires soldered to the sensor breakout flex every time the case
is opened, and that is usually where it breaks.

## UV reads `0.00` outdoors

- **Something is over the sensor window.** A clear printed cover, a sticker, a film
  of glue. Most plastics block UV thoroughly — that is the point of the open hole.
- **It is genuinely low.** Under heavy cloud, in winter, indoors near a window, or
  in full shade, `0.00` is the right answer. Glass blocks nearly all UVB and much
  UVA, so a reading taken through a window is supposed to be near zero.
- Check the lux line at the same time. If lux is high and UV is zero, the sensor is
  covered or the UVA path is blocked. If both are low, it is simply dark.

## Lux stops rising at about 52 000

That is the ceiling of the ADC at the default 3× gain and 18-bit resolution.
Direct sun is brighter than the sensor can count at that setting. Lower the gain to
get headroom — see [measurement.md](measurement.md#range-and-saturation). The UV
figure is not affected.

## The numbers look plausible but do not match a forecast

Expected, within an index point or so. The meter reads UVA only, has no
calibration, and is reporting the spot you are standing in rather than a regional
figure for noon. [measurement.md](measurement.md#how-far-to-trust-it) explains what
the number is and is not.

## It works on USB but dies on battery

- The cell is flat, or its protection circuit has latched off. Charge it.
- The switch or a battery joint is intermittent. The `BAT` pads are small and the
  wire pulls on them every time the case is closed.
- The cell has no protection circuit and has been run down too far. Cells in this
  size are sold both ways; the unprotected ones do not come back.

## The battery never charges

**The switch has to be on.** It sits in the positive lead between the cell and the
board, so switching off disconnects the cell from the charger as well as from the
ESP32. Left on a charger switched off, the meter charges nothing.

## The board does not appear as a serial port

- The USB-C cable is charge-only. Many are. Try another.
- The board needs bootloader mode: hold **B**, press and release **R**, release
  **B**.

## Related

- [hardware.md](hardware.md) — the wiring diagram and every connection
- [flashing.md](flashing.md) — getting MicroPython and the files onto the board
- [measurement.md](measurement.md) — what the numbers mean
