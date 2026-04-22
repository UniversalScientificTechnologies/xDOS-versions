/* Auto-generated from xDOS_devices.yaml — do not edit manually. */
#pragma once
#include <stdint.h>

typedef enum {
    DEVICE_TYPE_UNKNOWN = 0,
    DEVICE_TYPE_AIRDOS = 1,
    DEVICE_TYPE_GEODOS = 2,
    DEVICE_TYPE_LABDOS = 3,
    DEVICE_TYPE_SPACEDOS = 4,
    DEVICE_TYPE_BATDATUNIT = 100,
} DeviceType;

typedef struct {
    const char *full_name;
    DeviceType device_type;
    uint8_t device_version;
    char hardware_revision;  /* '\0' = no revision letter */
} KnownDevice;

static const KnownDevice KNOWN_DEVICES[] = {
    {"AIRDOS01", DEVICE_TYPE_AIRDOS, 1, '\0'},
    {"AIRDOS02", DEVICE_TYPE_AIRDOS, 2, '\0'},
    {"AIRDOS03A", DEVICE_TYPE_AIRDOS, 3, 'A'},
    {"AIRDOS03B", DEVICE_TYPE_AIRDOS, 3, 'B'},
    {"AIRDOS04A", DEVICE_TYPE_AIRDOS, 4, 'A'},
    {"AIRDOS04B", DEVICE_TYPE_AIRDOS, 4, 'B'},
    {"AIRDOS04C", DEVICE_TYPE_AIRDOS, 4, 'C'},
    {"GEODOS01", DEVICE_TYPE_GEODOS, 1, '\0'},
    {"GEODOS02", DEVICE_TYPE_GEODOS, 2, '\0'},
    {"LABDOS01", DEVICE_TYPE_LABDOS, 1, '\0'},
    {"SPACEDOS01B", DEVICE_TYPE_SPACEDOS, 1, 'B'},
    {"SPACEDOS02", DEVICE_TYPE_SPACEDOS, 2, '\0'},
    {"SPACEDOS04", DEVICE_TYPE_SPACEDOS, 4, '\0'},
    {"BATDATUNIT01A", DEVICE_TYPE_BATDATUNIT, 1, 'A'},
    {"BATDATUNIT01B", DEVICE_TYPE_BATDATUNIT, 1, 'B'},
    {"BATDATUNIT01C", DEVICE_TYPE_BATDATUNIT, 1, 'C'},
};

static const int KNOWN_DEVICE_COUNT =
    (int)(sizeof(KNOWN_DEVICES) / sizeof(KNOWN_DEVICES[0]));
