# Auto-generated from xDOS_devices.yaml — do not edit manually.
from __future__ import annotations
import enum
from dataclasses import dataclass
from typing import Optional

class DeviceType(enum.IntEnum):
    UNKNOWN = 0
    AIRDOS = 1
    GEODOS = 2
    LABDOS = 3
    SPACEDOS = 4
    BATDATUNIT = 100

@dataclass(frozen=True)
class KnownDevice:
    full_name: str
    device_type: DeviceType
    device_version: int
    hardware_revision: Optional[str]

KNOWN_DEVICES: list[KnownDevice] = [
    KnownDevice("AIRDOS01", DeviceType.AIRDOS, 1, None),
    KnownDevice("AIRDOS02", DeviceType.AIRDOS, 2, None),
    KnownDevice("AIRDOS03A", DeviceType.AIRDOS, 3, "A"),
    KnownDevice("AIRDOS03B", DeviceType.AIRDOS, 3, "B"),
    KnownDevice("AIRDOS04A", DeviceType.AIRDOS, 4, "A"),
    KnownDevice("AIRDOS04B", DeviceType.AIRDOS, 4, "B"),
    KnownDevice("AIRDOS04C", DeviceType.AIRDOS, 4, "C"),
    KnownDevice("GEODOS01", DeviceType.GEODOS, 1, None),
    KnownDevice("GEODOS02", DeviceType.GEODOS, 2, None),
    KnownDevice("LABDOS01", DeviceType.LABDOS, 1, None),
    KnownDevice("SPACEDOS01B", DeviceType.SPACEDOS, 1, "B"),
    KnownDevice("SPACEDOS02", DeviceType.SPACEDOS, 2, None),
    KnownDevice("SPACEDOS04", DeviceType.SPACEDOS, 4, None),
    KnownDevice("BATDATUNIT01A", DeviceType.BATDATUNIT, 1, "A"),
    KnownDevice("BATDATUNIT01B", DeviceType.BATDATUNIT, 1, "B"),
    KnownDevice("BATDATUNIT01C", DeviceType.BATDATUNIT, 1, "C"),
]

KNOWN_DEVICES_BY_NAME: dict[str, KnownDevice] = {
    d.full_name: d for d in KNOWN_DEVICES
}
