#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""IO board abstraction: all low-level communication with the FPGA / chamber board."""

import time
import serial
import serial.tools.list_ports

from config import (
    BAUD_RATE,
    CMD_HEATER_ON,
    CMD_HEATER_OFF,
    CMD_LED_ON,
    CMD_LED_OFF,
    CMD_SET_FAN,
    CMD_SET_AIR,
    CMD_READ_TEMP,
    CMD_READ_RPM,
    CMD_READ_INTERLOCK,
    CMD_ENABLE_WD,
    ntc_to_temp_c,
)


class IOBoard:
    def __init__(self, port: str | None = None, baud: int = BAUD_RATE, debug: bool = False):
        self.debug = debug
        self.port = port or self._detect_port()
        self.ser = None
        if self.port:
            try:
                self.ser = serial.Serial(self.port, baud, timeout=1)
                if self.debug:
                    print(f"[IOBoard] Opened serial port: {self.port}")
            except Exception as e:
                print(f"[IOBoard] Failed to open serial port {self.port}: {e}")
        else:
            print("[IOBoard] No serial port detected!")

    # ------------- Port detect -------------

    def _detect_port(self) -> str | None:
        ports = serial.tools.list_ports.comports()
        for p in ports:
            name = p.device.lower()
            if "usb" in name or "ttyusb" in name or "ttyacm" in name:
                return p.device
        return None

    # ------------- Low-level HEX send -------------

    def send_hex(self, cmd: str) -> str:
        if self.ser is None:
            if self.debug:
                print(f"[IOBoard] (NO SERIAL) Would send: {cmd}")
            return ""
        try:
            if self.debug:
                print(f"[IOBoard] >> {cmd}")
            self.ser.write(bytes.fromhex(cmd))
            time.sleep(0.05)
            resp = self.ser.read_all().hex()
            if self.debug:
                print(f"[IOBoard] << {resp}")
            return resp
        except Exception as e:
            print(f"[IOBoard] Error sending '{cmd}': {e}")
            return ""

    # ------------- High-level operations -------------

    # Heater
    def heater_on(self):
        self.send_hex(CMD_HEATER_ON)

    def heater_off(self):
        self.send_hex(CMD_HEATER_OFF)

    # LED cooling
    def led_on(self):
        self.send_hex(CMD_LED_ON)

    def led_off(self):
        self.send_hex(CMD_LED_OFF)

    # Fan
    def set_fan(self, percent: int):
        percent = max(0, min(100, int(percent)))
        self.send_hex(CMD_SET_FAN.format(value=percent))

    # Air intake
    def set_air_intake(self, percent: int):
        percent = max(0, min(100, int(percent)))
        self.send_hex(CMD_SET_AIR.format(value=percent))

    # Watchdog
    def enable_watchdog(self):
        self.send_hex(CMD_ENABLE_WD)

    # ------------- Measurements -------------

    def read_temp_raw(self) -> int | None:
        resp = self.send_hex(CMD_READ_TEMP)
        if not resp:
            return None
        try:
            return int(resp, 16)
        except Exception:
            return None

    def read_temp_c(self) -> float | None:
        raw = self.read_temp_raw()
        if raw is None:
            return None
        return float(ntc_to_temp_c(raw))

    def read_rpm(self) -> int | None:
        resp = self.send_hex(CMD_READ_RPM)
        if not resp:
            return None
        try:
            return int(resp, 16) * 30
        except Exception:
            return None

    def read_interlock_raw(self) -> int | None:
        resp = self.send_hex(CMD_READ_INTERLOCK)
        if not resp:
            return None
        try:
            return int(resp, 16)
        except Exception:
            return None

    # ------------- Simple debug / self test -------------

    def self_test(self):
        print("[IOBoard] Self test starting...")
        print(f"  Port: {self.port}")
        if self.ser is None:
            print("  Serial not open – check connections.")
            return

        print("  Reading temperature...")
        t = self.read_temp_c()
        print(f"    Temp: {t} °C")

        print("  Reading RPM...")
        rpm = self.read_rpm()
        print(f"    RPM: {rpm}")

        print("  Toggling heater ON/OFF quickly...")
        self.heater_on()
        time.sleep(0.5)
        self.heater_off()
        print("[IOBoard] Self test done.")


if __name__ == "__main__":
    board = IOBoard(debug=True)
    board.self_test()
