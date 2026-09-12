# ltr390.py - MicroPython driver for the LTR-390UV-01 UV and ambient light sensor.
#
# The sensor has one ADC shared between a UVA photodiode and a visible-light
# photodiode, so UV and lux are read by switching modes rather than at once.

import time

_LTR390_ADDRESS = 0x53
_LTR390_MAIN_CTRL, _LTR390_MEAS_RATE, _LTR390_GAIN = 0x00, 0x04, 0x05
_LTR390_PART_ID, _LTR390_MAIN_STATUS = 0x06, 0x07
_LTR390_ALSDATA_LSB, _LTR390_UVSDATA_LSB = 0x0D, 0x10

# Counts per UV index at 18x gain and 20-bit resolution, from the datasheet.
_UV_SENSITIVITY = 1400


class LTR390:

    ALS_MODE, UVS_MODE = 0, 1
    GAIN_1, GAIN_3, GAIN_6, GAIN_9, GAIN_18 = 0, 1, 2, 3, 4
    RESOLUTION_20BIT, RESOLUTION_19BIT, RESOLUTION_18BIT = 0, 1, 2
    RESOLUTION_17BIT, RESOLUTION_16BIT, RESOLUTION_13BIT = 3, 4, 5

    _gain_factor = (1, 3, 6, 9, 18)
    _res_factor = (4, 2, 1, 0.5, 0.25, 0.03125)

    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = _LTR390_ADDRESS

        part_id = self._read_register(_LTR390_PART_ID)[0]
        if (part_id >> 4) != 0x0B:
            raise RuntimeError("Failed to find LTR390 sensor")

        self.reset()
        self.enable(True)
        if not self.enabled():
            raise RuntimeError("Failed to enable LTR390 sensor")

        self.set_gain(self.GAIN_3)
        self.set_resolution(self.RESOLUTION_18BIT)

    def _read_register(self, reg_addr, bytes_to_read=1):
        return self.i2c.readfrom_mem(self.addr, reg_addr, bytes_to_read)

    def _write_register(self, reg_addr, value):
        self.i2c.writeto_mem(self.addr, reg_addr, bytearray([value]))

    def reset(self):
        reg = self._read_register(_LTR390_MAIN_CTRL)[0] | 0b00010000
        self._write_register(_LTR390_MAIN_CTRL, reg)
        time.sleep_ms(30)
        return self._read_register(_LTR390_MAIN_CTRL)[0] == 0

    def enable(self, en):
        reg = self._read_register(_LTR390_MAIN_CTRL)[0]
        reg = (reg | 0b00000010) if en else (reg & ~0b00000010)
        self._write_register(_LTR390_MAIN_CTRL, reg)

    def enabled(self):
        return (self._read_register(_LTR390_MAIN_CTRL)[0] >> 1) & 1

    def set_mode(self, mode):
        reg = self._read_register(_LTR390_MAIN_CTRL)[0] & ~0b00001000
        if mode == self.UVS_MODE:
            reg |= 0b00001000
        self._write_register(_LTR390_MAIN_CTRL, reg)

    def get_mode(self):
        return (self._read_register(_LTR390_MAIN_CTRL)[0] >> 3) & 1

    def set_gain(self, gain):
        self._write_register(_LTR390_GAIN, gain)

    def get_gain(self):
        return self._read_register(_LTR390_GAIN)[0] & 0x07

    def set_resolution(self, resolution):
        self._write_register(_LTR390_MEAS_RATE, resolution << 4)

    def get_resolution(self):
        return (self._read_register(_LTR390_MEAS_RATE)[0] >> 4) & 0x07

    def new_data_available(self):
        return (self._read_register(_LTR390_MAIN_STATUS)[0] >> 3) & 1

    def _read_20bit_data(self, lsb_reg):
        data = self._read_register(lsb_reg, 3)
        return data[0] | (data[1] << 8) | ((data[2] & 0x0F) << 16)

    def read_all_channels(self):
        """Return (uv_index, lux, raw_uvs, raw_als)."""
        gain = self.get_gain()
        res = self.get_resolution()
        gain_val = self._gain_factor[gain]
        res_val = self._res_factor[res]

        self.set_mode(self.UVS_MODE)

        # Reading the status register clears the data-ready flag. Doing it here,
        # immediately after the mode switch, is what makes the wait below block
        # for a reading taken in the new mode. Without it the flag left over from
        # the previous mode satisfies the wait instantly and the value returned
        # is the other channel's.
        self._read_register(_LTR390_MAIN_STATUS)

        while not self.new_data_available():
            time.sleep_ms(30)
        raw_uvs = self._read_20bit_data(_LTR390_UVSDATA_LSB)

        gain_scale = gain_val / self._gain_factor[self.GAIN_18]
        res_scale = res_val / self._res_factor[self.RESOLUTION_20BIT]
        denominator = gain_scale * res_scale * _UV_SENSITIVITY
        uvi = raw_uvs / denominator if denominator > 0 else 0

        self.set_mode(self.ALS_MODE)
        self._read_register(_LTR390_MAIN_STATUS)

        while not self.new_data_available():
            time.sleep_ms(30)
        raw_als = self._read_20bit_data(_LTR390_ALSDATA_LSB)

        denominator = gain_val * res_val
        lux = (0.6 * raw_als) / denominator if denominator > 0 else 0

        return uvi, lux, raw_uvs, raw_als
