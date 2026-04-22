# xDOS versions and EEPROM structures definitions

Source-of-truth definitions for identification data of xDOS-family dosimeters (AIRDOS, LABDOS, SPACEDOS, GEODOS). The repository is intended to be used as a **git submodule** in firmware (C/C++) and host-software (Python) projects.

Input data is maintained as YAML files. GitHub Actions automatically regenerates C/C++ headers and Python modules whenever the YAML sources change.

## Contents

| File | Description |
|------|-------------|
| [`eeprom_layout.yaml`](eeprom_layout.yaml) | Binary EEPROM structure layout — field types, bit flags, CRC |
| [`xDOS_devices.yaml`](xDOS_devices.yaml) | `DeviceType` enum + known device registry (AIRDOS04B, …) |
| [`generated/`](generated/) | Generated files — **do not edit manually** |

## Using the generated files

### C / C++

```c
#include "xdos_devices.h"   // DeviceType enum, KnownDevice struct, KNOWN_DEVICES[]
#include "eeprom_layout.h"  // DosimeterEeprom struct, EEPROM_* bit-flag macros
```

`eeprom_layout.h` pulls in `xdos_devices.h` automatically.

`DosimeterEeprom` is `__attribute__((packed))`, little-endian, **113 bytes**.

```c
DosimeterEeprom eeprom;
memcpy(&eeprom, raw_bytes, sizeof(eeprom));

if (eeprom.rtc_flags & EEPROM_RTC_INITIALIZED) { ... }
if (eeprom.device_type == DEVICE_TYPE_AIRDOS)   { ... }
```

### Python

```python
from generated import DosimeterEeprom, DeviceType, KNOWN_DEVICES_BY_NAME

eeprom = DosimeterEeprom.from_buffer_copy(raw_bytes)
print(DeviceType(eeprom.device_type).name)   # "AIRDOS"
print(eeprom.device_identifier.decode())
```

## Using as a submodule

```bash
git submodule add https://github.com/UST/xDOS-versions.git xdos-versions
git submodule update --init
```

**Firmware (CMake / Arduino):** add `xdos-versions/generated/` to the include path.

**Python project:** add `xdos-versions/` to `sys.path` or install as `pip install -e xdos-versions/`.

## Adding a new device

Edit [`xDOS_devices.yaml`](xDOS_devices.yaml) and append an entry to `known_devices`:

```yaml
  - full_name: AIRDOS05
    device_type: AIRDOS
    hardware_version:
      device_version: 5
      hardware_revision: null
```

After pushing to `main`, GitHub Actions will regenerate and commit `generated/` automatically.

## Manual regeneration

```bash
pip install pyyaml
python scripts/generate.py
```

## EEPROM field reference

| Field | Type | Description |
|-------|------|-------------|
| `format_version` | `uint16` | Format version for backward compatibility |
| `device_type` | `uint16` (enum) | Device family (AIRDOS, LABDOS, …) |
| `crc32` | `uint32` | CRC32 of the full structure |
| `hardware_version` | struct | `device_version` (uint8) + `hardware_revision` (uint8, ASCII, 0 = none) |
| `device_identifier` | `char[24]` | Human-readable identifier (animal name printed on enclosure) |
| `operating_modes` | `uint16` | Configuration flags |
| `rtc_flags` | `uint8` | RTC status — see `EEPROM_HAS_RTC`, `EEPROM_RTC_INITIALIZED`, … |
| `rtc_history[5]` | struct[5] | RTC initialisation history (timestamp triplets) |
| `calibration_constants[3]` | `float[3]` | Calibration parameters |
| `calibration_version` | `uint32` | Calibration timestamp |
