/* Auto-generated from eeprom_layout.yaml — do not edit manually. */
#pragma once
#include "xdos_devices.h"

typedef struct __attribute__((packed)) {
    uint16_t format_version;
    uint16_t device_type;
    uint32_t crc32;
    struct __attribute__((packed)) {
        uint8_t device_version;
        uint8_t hardware_revision;
    } hardware_version;
    char device_identifier[24];
    uint16_t operating_modes;
    uint8_t rtc_flags;
    struct __attribute__((packed)) {
        uint32_t rtc_initialization_timestamp;
        uint32_t reference_timestamp;
        uint32_t rtc_value_at_reference_timestamp;
    } rtc_history[5];
    float calibration_constants[3];
    uint32_t calibration_version;
} DosimeterEeprom;

/* Bit flags for field 'rtc_flags' */
#define EEPROM_HAS_RTC (1u << 0)
#define EEPROM_HAS_RTC_BACKUP_BATTERY (1u << 1)
#define EEPROM_RTC_INITIALIZED (1u << 2)
#define EEPROM_RTC_POWER_LOSS_DETECTED (1u << 3)
#define EEPROM_GEIGER_MODE_ENABLED (1u << 4)
#define EEPROM_LED_ENABLED (1u << 5)
