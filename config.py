#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Configuration and command constants for the chamber controller."""

BAUD_RATE = 115200

# Commands (HEX strings) for the FPGA / IO board
CMD_HEATER_ON   = "01 04 00 02"
CMD_HEATER_OFF  = "01 04 00 00"

CMD_LED_ON      = "01 03 00 02"
CMD_LED_OFF     = "01 03 00 00"

# Fan PWM: 0–100% mapped directly to last byte (HEX)
CMD_SET_FAN     = "01 40 00 {value:02X}"

# Air intake / throttle: 0–100% mapped directly to last byte (HEX)
CMD_SET_AIR     = "01 42 00 {value:02X}"

# Read commands
CMD_READ_TEMP       = "00 11"
CMD_READ_RPM        = "00 41"
CMD_READ_INTERLOCK  = "00 31"

# Watchdog enable: write 0xFF to FPGA PHY-ADDR 0x33, REG 0x26
CMD_ENABLE_WD       = "33 26 FF"

# NTC configuration (10K, Beta 3950)
R_REF = 10000.0
R0    = 10000.0
BETA  = 3950.0
T0_K  = 25.0 + 273.15
VREF  = 5.0

def adc_to_voltage(raw: int) -> float:
    """Convert raw ADC code to voltage, based on your original formula."""
    return (2.5 / 2047.0 * raw) / 0.5

def ntc_to_temp_c(raw: int) -> float:
    import math
    V = adc_to_voltage(raw)
    if V <= 0 or V >= VREF:
        return 0.0
    R_ntc = R_REF * (V / (VREF - V))
    ln_ratio = math.log(R_ntc / R0)
    temp_k = 1.0 / ((1.0 / T0_K) + (ln_ratio / BETA))
    return temp_k - 273.15
