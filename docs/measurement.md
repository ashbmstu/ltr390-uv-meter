# Measurement

How the two numbers on the screen are produced, and how far to trust them.

## What the sensor sees

The LTR-390UV-01 has two photodiodes and one analogue-to-digital converter shared
between them. A mode bit selects which diode the converter is looking at:

- **UVS mode** — a UVA photodiode, sensitive roughly between 300 and 350 nm.
- **ALS mode** — a visible-light photodiode with a response shaped to approximate
  the human eye.

There is no UVB channel and no UVC channel. Everything the meter says about
ultraviolet comes from that one UVA diode.

## From counts to numbers

The firmware sets **3× gain** and **18-bit resolution** at startup
(`LTR390.__init__` in [`src/ltr390.py`](../src/ltr390.py)). Both are readable back
from the sensor, and `read_all_channels()` re-reads them on every call, so the
arithmetic follows if you change them.

### UV index

```
uvi = raw_uvs / (gain_scale × res_scale × 2300)

  gain_scale = gain / 18            the gain relative to the 18× maximum
  res_scale  = integration / 4      the integration time relative to 20-bit
  2300                              rated counts per UV index at 18× gain, 20-bit
```

At the defaults that is `3/18 × 1/4 × 2300 = 95.83` counts per UV index, so one
count is about 0.01 of an index point. The screen shows two decimal places; the
underlying step is larger than the last digit.

### Illuminance

```
lux = 0.6 × raw_als / (gain × integration)
```

At the defaults, `0.6 / 3 = 0.2` lux per count.

The `0.6` is a window factor — the amount of light the sensor's package lets
through. It assumes a bare sensor. Putting anything in front of the hole, even
clear plastic, makes the reading low by however much that material absorbs.

### Gain and integration settings

| Resolution | Integration | Factor used |
|---|---|---|
| 20-bit | 400 ms | 4 |
| 19-bit | 200 ms | 2 |
| **18-bit** | **100 ms** | **1** (default) |
| 17-bit | 50 ms | 0.5 |
| 16-bit | 25 ms | 0.25 |

A 13-bit mode also exists. Its factor in the table is inherited from the upstream
driver and the firmware never selects it.

## Range and saturation

An 18-bit conversion tops out at 262 143 counts. That ceiling matters for lux, and
not at all for UV:

| Gain | Highest UV index | Highest lux |
|---|---|---|
| 1× | ~13 500 | ~157 000 |
| **3× (default)** | **~4 500** | **~52 000** |
| 18× | ~750 | ~8 700 |

Direct summer sun is around 100 000 lux, which is **above the ceiling at the
default 3× gain**. Point the meter straight at a bright sky and the lux figure
stops climbing near 52 000 and stays there. The UV index is unaffected — nothing
on Earth comes close to 4 500.

If you care more about lux than about UV, drop the gain to 1× and you get headroom
to 157 000 at the cost of coarser UV steps:

```python
sensor.set_gain(sensor.GAIN_1)
```

## Timing

`read_all_channels()` switches to UVS mode, waits for a conversion, switches to
ALS mode, and waits again. At 18-bit each conversion takes about 100 ms, and the
wait polls every 30 ms, so a full reading costs roughly 200 to 260 ms. `main.py`
then sleeps `REFRESH_MS` — 500 ms — before doing it again, which puts the screen
refresh at a little under once a second.

The two channels are therefore never sampled at the same instant. Under a steady
sky that does not matter. Waving the meter past a lamp will produce a UV reading
and a lux reading from different moments.

Reading the status register immediately after each mode switch is what makes this
work: the register's data-ready flag clears when read, so clearing it there forces
the wait to block for a conversion taken in the *new* mode. Without that, the flag
left over from the previous mode satisfies the wait instantly and the value
returned belongs to the other channel.

## How far to trust it

**A UVA measurement scaled to look like a UV index.** The published UV index is a
weighted integral across UVA and UVB, and UVB is the part that burns skin fastest.
This sensor cannot see UVB. Outdoors, UVA and UVB rise and fall together closely
enough that the scaled figure tracks the real index usefully. Under an artificial
source with a different spectrum — a UV LED, a fluorescent tube, a curing lamp —
the relationship no longer holds and the number should be read as "how much UVA",
not as a UV index.

**Nothing here is calibrated.** The 2300 counts-per-index figure is the part's
rated sensitivity, the same one Adafruit's driver uses, not a measurement of the
sensor in your hand. `_UV_SENSITIVITY` at the top of
[`src/ltr390.py`](../src/ltr390.py) is the one line to change once you have compared
the meter against a reference instrument. Beyond that, part-to-part spread, the angle
you hold it at and the state of the hole in the case all move the result.

**Comparisons are far better than absolutes.** Sun against shade, with sunglasses
against without, this lamp against that lamp — all of those are trustworthy,
because the unknown scale factor cancels. "It is exactly 6.34" is not.

## Sanity checks

- Indoors, away from a window, it should read `0.00 UVi`. Anything else means
  stray light or a wiring fault.
- Outdoors on a clear day it should land near the UV index your weather forecast
  gives, within an index point or so.
- Hold a pair of sunglasses over the hole in bright sun. The UV reading should
  collapse and the lux reading should fall by much less. If the UV figure barely
  moves, the sunglasses are not doing their job.
- A £2 UV torch from a banknote checker will send it well past 10 at close range.

## Related

- [hardware.md](hardware.md) — the sensor window and why nothing should cover it
- [troubleshooting.md](troubleshooting.md) — readings that look wrong
