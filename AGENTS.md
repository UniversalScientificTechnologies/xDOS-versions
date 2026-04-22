This file provides guidance to agents when working with code in this repository.

## What this repository does

Source-of-truth definitions for xDOS-family dosimeter device identification data (EEPROM layout and device type registry), stored as YAML. A code generator produces ready-to-include C/C++ headers and Python modules from those YAML files. The repo is intended to be consumed as a **git submodule** by firmware (C/C++) and host-software (Python) projects.

## Key commands

```bash
# Regenerate all files under generated/ from the YAML sources
pip install pyyaml
python scripts/generate.py

# Quick smoke-test: import the generated Python package and check struct size
python3 -c "
from generated.eeprom_layout import DosimeterEeprom
import ctypes; print(ctypes.sizeof(DosimeterEeprom))  # expect 113
"
```

## Architecture

```
eeprom_layout.yaml      # EEPROM binary layout (field names, types, bit flags, CRC)
xDOS_devices.yaml       # DeviceType enum + known device registry (full product codes)
scripts/generate.py     # Single-file generator — reads both YAMLs, writes generated/
generated/
    xdos_devices.h/.py  # DeviceType enum + KnownDevice table — no dependencies
    eeprom_layout.h/.py # DosimeterEeprom struct — #includes / imports xdos_devices
    __init__.py         # Python package re-export
.github/workflows/generate.yml  # Runs generator on YAML/script changes, commits result
```

The generator is intentionally self-contained in `scripts/generate.py` with no build system. Dependency order matters: `xdos_devices` must be generated before (and included by) `eeprom_layout`.

## YAML schema conventions

**`eeprom_layout.yaml`** — top-level key `eeprom_layout`. Fields use scalar types (`uint8`, `uint16`, `uint32`, `float`, `char[N]`), `type: struct` with nested `fields:`, or `type: array` with `length:` and `item_fields:`. Fields with `bit_mapping:` emit `#define EEPROM_<NAME>` macros in C and an `IntFlag` class in Python. The `encoding: enum` annotation on `device_type` is documentation only.

**`xDOS_devices.yaml`** — three top-level keys: `device_type` (enum definition with `enum_name` and `values` list), `hardware_version` (descriptor, not used by generator directly), and `known_devices` (list of full product codes with `device_type`, `device_version`, `hardware_revision` — `null` means no revision letter).

## Extending the generator

- New scalar types: add to both `C_TYPES` and `PY_TYPES` dicts in `generate.py`.
- New YAML structural constructs: add a branch in `_c_fields()` (C) and `_py_nested()` (Python).
- The Python output uses `ctypes.LittleEndianStructure` with `_pack_ = 1` to match the C `__attribute__((packed))` layout. Any new type must preserve this binary compatibility.

## Using as a submodule

```bash
# In a dependent project
git submodule add <url> xdos-versions
```

C/C++ firmware: add `xdos-versions/generated/` to include path, then `#include "eeprom_layout.h"`.

Python host software: add `xdos-versions/` to `sys.path` (or install as editable package), then `from generated import DosimeterEeprom, DeviceType`.
