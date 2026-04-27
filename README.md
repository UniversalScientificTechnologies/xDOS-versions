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

## RTC history semantics

`rtc_history[]` stores timing data for RTC chips that run as an elapsed-time
counter, for example PCF85263A in stopwatch mode. Each entry is a triplet:

| Field | Meaning |
|-------|---------|
| `rtc_initialization_timestamp` | Unix UTC timestamp when the RTC counter was reset or initialized. This is mainly historical/context information. |
| `reference_timestamp` | Unix UTC timestamp of RTC counter value 0. This is the derived stopwatch-start timestamp, kept directly for simple firmware time reconstruction. |
| `rtc_value_at_reference_timestamp` | RTC elapsed counter value, in seconds, at the moment when `reference_timestamp` was updated. |

The canonical interpretation is therefore:

```text
absolute_time = reference_timestamp + current_rtc_counter
```

The age of the last RTC synchronization/update is:

```text
sync_age = current_rtc_counter - rtc_value_at_reference_timestamp
```

The actual UTC time when the last synchronization/update was made can be derived
as:

```text
last_update_time = reference_timestamp + rtc_value_at_reference_timestamp
```

When initializing a freshly reset RTC, use:

```text
rtc_initialization_timestamp = now_utc
reference_timestamp = now_utc
rtc_value_at_reference_timestamp = 0
```

When synchronizing an already running RTC without resetting the chip, update the
zero-time estimate as:

```text
rtc_initialization_timestamp = previous rtc_initialization_timestamp
reference_timestamp = now_utc - current_rtc_counter
rtc_value_at_reference_timestamp = current_rtc_counter
```

This layout is mathematically equivalent to storing the literal reference
measurement pair `(now_utc, current_rtc_counter)`, because
`now_utc = reference_timestamp + rtc_value_at_reference_timestamp`. The chosen
form stores the value most useful to firmware directly: the current absolute
time can be computed as `reference_timestamp + current_rtc_counter`, while the
third field still records how old the synchronization point is.
