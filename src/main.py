# main.py - UV index and illuminance meter on a Seeed XIAO ESP32-C3.
#
# Reads the LTR390 twice a second and draws both values on a 128x64 SSD1306
# OLED at double size. There is no power management: the battery is switched
# by hand.

import time
from machine import Pin, SoftI2C, I2C
import framebuf

from ltr390 import LTR390
from ssd1306 import SSD1306_I2C

# Two separate I2C buses. The sensor would not respond on the hardware
# controller that drives the display, so it gets a software bus of its own.
# Wiring them together and dropping SoftI2C looks tidier and does not work.
PIN_LTR_SCL = 4
PIN_LTR_SDA = 3
PIN_OLED_SCL = 7
PIN_OLED_SDA = 6

OLED_WIDTH = 128
OLED_HEIGHT = 64
REFRESH_MS = 500

i2c_sensor = SoftI2C(scl=Pin(PIN_LTR_SCL), sda=Pin(PIN_LTR_SDA), freq=100000)
i2c_display = I2C(0, scl=Pin(PIN_OLED_SCL), sda=Pin(PIN_OLED_SDA), freq=400000)

_char_buf = bytearray(8)
_char_fb = framebuf.FrameBuffer(_char_buf, 8, 8, framebuf.MONO_VLSB)


def text_large(oled, text, x, y, scale=2):
    for index, char in enumerate(text):
        _char_fb.fill(0)
        _char_fb.text(char, 0, 0, 1)
        for cx in range(8):
            for cy in range(8):
                if _char_fb.pixel(cx, cy):
                    px = x + index * 8 * scale + cx * scale
                    py = y + cy * scale
                    oled.fill_rect(px, py, scale, scale, 1)


sensor = None
oled = None

try:
    sensor = LTR390(i2c_sensor)
    oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c_display)
    oled.fill(0)
    oled.text("Init: OK", 0, 0)
    oled.show()

except (OSError, RuntimeError) as e:
    print("Initialisation failed:", e)
    if oled:
        oled.fill(0)
        oled.text("Init: FAIL", 0, 0)
        oled.text(str(e), 0, 16)
        oled.show()
    raise SystemExit

while True:
    try:
        uvi, lux, _, _ = sensor.read_all_channels()

        oled.fill(0)
        text_large(oled, f"{uvi:.2f} UVi", 0, 8)
        text_large(oled, f"{lux:.0f} Lx", 0, 40)
        oled.show()

        time.sleep_ms(REFRESH_MS)

    except (OSError, RuntimeError) as e:
        print("Read failed:", e)
        try:
            oled.fill(0)
            oled.text("Runtime Error:", 0, 0)
            oled.text(str(e), 0, 16)
            oled.show()
        except Exception:
            pass

        time.sleep_ms(1000)
