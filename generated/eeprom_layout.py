# Auto-generated from eeprom_layout.yaml — do not edit manually.
import ctypes
import enum
from .xdos_devices import DeviceType  # noqa: F401

class RtcFlagsFlags(enum.IntFlag):
    HAS_RTC = 1 << 0
    HAS_RTC_BACKUP_BATTERY = 1 << 1
    RTC_INITIALIZED = 1 << 2
    RTC_POWER_LOSS_DETECTED = 1 << 3
    GEIGER_MODE_ENABLED = 1 << 4
    LED_ENABLED = 1 << 5

class CalibrationType(enum.IntEnum):
    LINEAR = 1
    LINEAR_WITH_NEUTRONS = 2

class HardwareVersion(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("device_version", ctypes.c_uint8),
        ("hardware_revision", ctypes.c_uint8),
    ]

class RtcHistoryEntry(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("rtc_initialization_timestamp", ctypes.c_uint32),
        ("reference_timestamp", ctypes.c_uint32),
        ("rtc_value_at_reference_timestamp", ctypes.c_uint32),
    ]

class DosimeterEeprom(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("format_version", ctypes.c_uint16),
        ("device_type", ctypes.c_uint16),
        ("crc32", ctypes.c_uint32),
        ("hardware_version", HardwareVersion),
        ("device_identifier", ctypes.c_char * 24),
        ("operating_modes", ctypes.c_uint16),
        ("rtc_flags", ctypes.c_uint8),
        ("rtc_history", RtcHistoryEntry * 5),
        ("calibration_constants", ctypes.c_float * 3),
        ("calibration_version", ctypes.c_uint32),
        ("num_noise_channels_default", ctypes.c_uint16),
        ("si_chip_area_cm2", ctypes.c_float),
        ("si_chip_thickness_cm", ctypes.c_float),
        ("energy_range_min_mev", ctypes.c_float),
        ("energy_range_max_mev", ctypes.c_float),
        ("calibration_type", ctypes.c_uint16),
        ("calibration_extra", ctypes.c_float * 4),
        ("detector_id", ctypes.c_uint8),
    ]

# Record size of each format_version; the CRC covers exactly these bytes.
FORMAT_VERSION_LATEST = 3
RECORD_SIZE_BY_VERSION = {
    0: 113,
    1: 113,
    2: 131,
    3: 150,
}
