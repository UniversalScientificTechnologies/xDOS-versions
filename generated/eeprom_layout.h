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
    uint16_t num_noise_channels_default;
    float si_chip_area_cm2;
    float si_chip_thickness_cm;
    float energy_range_min_mev;
    float energy_range_max_mev;
    uint16_t calibration_type;
    float calibration_extra[4];
    uint8_t detector_id;
} DosimeterEeprom;

/* Bit flags for field 'rtc_flags' */
#define EEPROM_HAS_RTC (1u << 0)
#define EEPROM_HAS_RTC_BACKUP_BATTERY (1u << 1)
#define EEPROM_RTC_INITIALIZED (1u << 2)
#define EEPROM_RTC_POWER_LOSS_DETECTED (1u << 3)
#define EEPROM_GEIGER_MODE_ENABLED (1u << 4)
#define EEPROM_LED_ENABLED (1u << 5)

/* Values of field 'calibration_type' */
#define EEPROM_CALIBRATION_TYPE_LINEAR 1u
#define EEPROM_CALIBRATION_TYPE_LINEAR_WITH_NEUTRONS 2u

/* Record size of each format_version; the CRC covers exactly these bytes. */
#define EEPROM_FORMAT_VERSION_LATEST 3
#define EEPROM_RECORD_SIZE_V1 113
#define EEPROM_RECORD_SIZE_V2 131
#define EEPROM_RECORD_SIZE_V3 150

/* Record size for a format_version, 0 = unknown version. */
static inline uint16_t eeprom_record_size(uint16_t format_version)
{
    switch (format_version) {
    case 0:
    case 1:
        return 113;
    case 2:
        return 131;
    case 3:
        return 150;
    default:
        return 0;
    }
}
