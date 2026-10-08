#!/usr/bin/env python3
"""Generate C/C++ headers and Python modules from YAML device definitions."""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pyyaml is required: pip install pyyaml")

REPO_ROOT = Path(__file__).parent.parent
GENERATED_DIR = REPO_ROOT / "generated"

C_TYPES = {
    "uint8": "uint8_t",
    "uint16": "uint16_t",
    "uint32": "uint32_t",
    "int8": "int8_t",
    "int16": "int16_t",
    "int32": "int32_t",
    "float": "float",
    "double": "double",
    "char": "char",
}

PY_TYPES = {
    "uint8": "ctypes.c_uint8",
    "uint16": "ctypes.c_uint16",
    "uint32": "ctypes.c_uint32",
    "int8": "ctypes.c_int8",
    "int16": "ctypes.c_int16",
    "int32": "ctypes.c_int32",
    "float": "ctypes.c_float",
    "double": "ctypes.c_double",
    "char": "ctypes.c_char",
}


def pascal(name: str) -> str:
    return "".join(w.capitalize() for w in name.split("_"))


def parse_type(type_str: str):
    """'float[3]' -> ('float', 3),  'uint8' -> ('uint8', None)"""
    m = re.fullmatch(r"(\w+)\[(\d+)\]", type_str)
    if m:
        return m.group(1), int(m.group(2))
    return type_str, None


# ---------------------------------------------------------------------------
# eeprom_layout.yaml → C header
# ---------------------------------------------------------------------------

def _c_fields(fields: dict, indent: int = 1) -> list[str]:
    pad = "    " * indent
    lines = []
    for fname, fdef in fields.items():
        t = fdef.get("type", "")
        base, count = parse_type(t)

        if t == "struct":
            lines.append(f"{pad}struct __attribute__((packed)) {{")
            lines.extend(_c_fields(fdef.get("fields", {}), indent + 1))
            lines.append(f"{pad}}} {fname};")

        elif t == "array":
            length = fdef.get("length", 1)
            lines.append(f"{pad}struct __attribute__((packed)) {{")
            lines.extend(_c_fields(fdef.get("item_fields", {}), indent + 1))
            lines.append(f"{pad}}} {fname}[{length}];")

        elif base == "char" and count:
            lines.append(f"{pad}char {fname}[{count}];")

        elif count:
            lines.append(f"{pad}{C_TYPES.get(base, base)} {fname}[{count}];")

        else:
            lines.append(f"{pad}{C_TYPES.get(t, t)} {fname};")

    return lines


SCALAR_SIZES = {
    "uint8": 1, "uint16": 2, "uint32": 4,
    "int8": 1, "int16": 2, "int32": 4,
    "float": 4, "double": 8, "char": 1,
}


def _field_size(fdef: dict) -> int:
    """Size of one field in bytes (the layout is packed)."""
    t = fdef["type"]
    if t == "struct":
        return sum(_field_size(f) for f in fdef["fields"].values())
    if t == "array":
        return fdef["length"] * sum(_field_size(f) for f in fdef["item_fields"].values())
    base, count = parse_type(t)
    return SCALAR_SIZES[base] * (count or 1)


def record_sizes(layout: dict) -> list:
    """[(version, size, aliases), ...] from layout["format_versions"]."""
    ends = {}
    offset = 0
    for fname, fdef in layout["fields"].items():
        offset += _field_size(fdef)
        ends[fname] = offset
    return [(v["version"], ends[v["last_field"]], v.get("aliases", []))
            for v in layout.get("format_versions", [])]


def eeprom_h(layout: dict) -> str:
    struct_name = pascal(layout["name"])
    fields = layout["fields"]
    out = [
        "/* Auto-generated from eeprom_layout.yaml — do not edit manually. */",
        "#pragma once",
        '#include "xdos_devices.h"',
        "",
        f"typedef struct __attribute__((packed)) {{",
    ]
    out.extend(_c_fields(fields))
    out.append(f"}} {struct_name};")
    out.append("")

    for fname, fdef in fields.items():
        bm = fdef.get("bit_mapping")
        if bm:
            out.append(f"/* Bit flags for field '{fname}' */")
            for bit_key, bit_name in bm.items():
                if "reserved" in bit_name:
                    continue
                bit_num = int(bit_key.split("_")[1])
                out.append(f"#define EEPROM_{bit_name.upper()} (1u << {bit_num})")
            out.append("")
        ev = fdef.get("enum_values")
        if ev:
            out.append(f"/* Values of field '{fname}' */")
            for value, name in ev.items():
                out.append(f"#define EEPROM_{fname.upper()}_{name.upper()} {int(value)}u")
            out.append("")

    sizes = record_sizes(layout)
    if sizes:
        out.append("/* Record size of each format_version; the CRC covers exactly these bytes. */")
        out.append(f"#define EEPROM_FORMAT_VERSION_LATEST {sizes[-1][0]}")
        for version, size, _ in sizes:
            out.append(f"#define EEPROM_RECORD_SIZE_V{version} {size}")
        out.append("")
        out.append("/* Record size for a format_version, 0 = unknown version. */")
        out.append("static inline uint16_t eeprom_record_size(uint16_t format_version)")
        out.append("{")
        out.append("    switch (format_version) {")
        for version, size, aliases in sizes:
            for v in list(aliases) + [version]:
                out.append(f"    case {v}:")
            out.append(f"        return {size};")
        out.append("    default:")
        out.append("        return 0;")
        out.append("    }")
        out.append("}")
        out.append("")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# eeprom_layout.yaml → Python module
# ---------------------------------------------------------------------------

def _py_nested(fname: str, fdef: dict, out_pre: list[str]) -> str:
    """Recursively emit nested ctypes classes and return the field type string."""
    t = fdef.get("type", "")
    base, count = parse_type(t)

    if t == "struct":
        class_name = pascal(fname)
        sub_fields = fdef.get("fields", {})
        entries = []
        for sf, sd in sub_fields.items():
            entries.append((sf, _py_nested(sf, sd, out_pre)))
        out_pre.append(f"class {class_name}(ctypes.LittleEndianStructure):")
        out_pre.append("    _pack_ = 1")
        out_pre.append("    _fields_ = [")
        for sf, st in entries:
            out_pre.append(f'        ("{sf}", {st}),')
        out_pre.append("    ]")
        out_pre.append("")
        return class_name

    if t == "array":
        length = fdef.get("length", 1)
        class_name = pascal(fname + "_entry")
        item_fields = fdef.get("item_fields", {})
        entries = []
        for sf, sd in item_fields.items():
            entries.append((sf, _py_nested(sf, sd, out_pre)))
        out_pre.append(f"class {class_name}(ctypes.LittleEndianStructure):")
        out_pre.append("    _pack_ = 1")
        out_pre.append("    _fields_ = [")
        for sf, st in entries:
            out_pre.append(f'        ("{sf}", {st}),')
        out_pre.append("    ]")
        out_pre.append("")
        return f"{class_name} * {length}"

    if base == "char" and count:
        return f"ctypes.c_char * {count}"
    if count:
        return f"{PY_TYPES.get(base, f'ctypes.c_{base}')} * {count}"
    return PY_TYPES.get(t, f"ctypes.c_{t}")


def eeprom_py(layout: dict) -> str:
    struct_name = pascal(layout["name"])
    fields = layout["fields"]

    pre: list[str] = []
    field_entries = []
    flags_classes: list[str] = []

    for fname, fdef in fields.items():
        bm = fdef.get("bit_mapping")
        if bm:
            cls = pascal(fname) + "Flags"
            flags_classes.append(f"class {cls}(enum.IntFlag):")
            for bit_key, bit_name in bm.items():
                if "reserved" in bit_name:
                    continue
                bit_num = int(bit_key.split("_")[1])
                flags_classes.append(f"    {bit_name.upper()} = 1 << {bit_num}")
            flags_classes.append("")
        ev = fdef.get("enum_values")
        if ev:
            cls = pascal(fname)
            flags_classes.append(f"class {cls}(enum.IntEnum):")
            for value, name in ev.items():
                flags_classes.append(f"    {name.upper()} = {int(value)}")
            flags_classes.append("")

        py_type = _py_nested(fname, fdef, pre)
        field_entries.append((fname, py_type))

    out = [
        "# Auto-generated from eeprom_layout.yaml — do not edit manually.",
        "import ctypes",
        "import enum",
        "from .xdos_devices import DeviceType  # noqa: F401",
        "",
    ]
    out.extend(flags_classes)
    out.extend(pre)
    out.append(f"class {struct_name}(ctypes.LittleEndianStructure):")
    out.append("    _pack_ = 1")
    out.append("    _fields_ = [")
    for fn, ft in field_entries:
        out.append(f'        ("{fn}", {ft}),')
    out.append("    ]")
    out.append("")

    sizes = record_sizes(layout)
    if sizes:
        out.append("# Record size of each format_version; the CRC covers exactly these bytes.")
        out.append(f"FORMAT_VERSION_LATEST = {sizes[-1][0]}")
        out.append("RECORD_SIZE_BY_VERSION = {")
        for version, size, aliases in sizes:
            for v in list(aliases) + [version]:
                out.append(f"    {v}: {size},")
        out.append("}")
        out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# xDOS_devices.yaml → C header
# ---------------------------------------------------------------------------

def devices_h(data: dict) -> str:
    enum_def = data["device_type"]
    enum_name = enum_def["enum_name"]
    known = data["known_devices"]

    out = [
        "/* Auto-generated from xDOS_devices.yaml — do not edit manually. */",
        "#pragma once",
        "#include <stdint.h>",
        "",
        f"typedef enum {{",
    ]
    for v in enum_def["values"]:
        out.append(f"    {v['name']} = {v['value']},")
    out.append(f"}} {enum_name};")
    out.append("")
    out.append("typedef struct {")
    out.append("    const char *full_name;")
    out.append(f"    {enum_name} device_type;")
    out.append("    uint8_t device_version;")
    out.append("    char hardware_revision;  /* '\\0' = no revision letter */")
    out.append("} KnownDevice;")
    out.append("")
    out.append("static const KnownDevice KNOWN_DEVICES[] = {")
    for d in known:
        dt = d["device_type"]
        dv = d["hardware_version"]["device_version"]
        hr = d["hardware_version"]["hardware_revision"]
        hr_c = r"'\0'" if hr is None else f"'{hr}'"
        out.append(f'    {{"{d["full_name"]}", DEVICE_TYPE_{dt}, {dv}, {hr_c}}},')
    out.append("};")
    out.append("")
    out.append("static const int KNOWN_DEVICE_COUNT =")
    out.append("    (int)(sizeof(KNOWN_DEVICES) / sizeof(KNOWN_DEVICES[0]));")
    out.append("")
    # Family names for text output (e.g. the device name in a log header).
    # On AVR they stay in flash; only the names a firmware actually uses are
    # linked in.
    out.append("/* Family name of a device_type for text output, e.g. \"AIRDOS\". */")
    out.append("#ifdef __AVR__")
    out.append("#include <avr/pgmspace.h>")
    out.append("#define XDOS_NAME_STORAGE PROGMEM")
    out.append("#else")
    out.append("#define XDOS_NAME_STORAGE")
    out.append("#endif")
    for v in enum_def["values"]:
        out.append(f'static const char {v["name"]}_NAME[] XDOS_NAME_STORAGE = "{v["device_type"]}";')
    out.append("")
    out.append("/* Name of a device_type, NULL for an unknown value. On AVR the string is")
    out.append(" * in flash (PROGMEM) - read it with strcpy_P() and friends. */")
    out.append(f"static inline const char *device_type_name(uint16_t device_type)")
    out.append("{")
    out.append("    switch (device_type) {")
    for v in enum_def["values"]:
        out.append(f"    case {v['value']}:")
        out.append(f"        return {v['name']}_NAME;")
    out.append("    default:")
    out.append("        return 0;")
    out.append("    }")
    out.append("}")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# xDOS_devices.yaml → Python module
# ---------------------------------------------------------------------------

def devices_py(data: dict) -> str:
    enum_def = data["device_type"]
    enum_name = enum_def["enum_name"]
    known = data["known_devices"]

    out = [
        "# Auto-generated from xDOS_devices.yaml — do not edit manually.",
        "from __future__ import annotations",
        "import enum",
        "from dataclasses import dataclass",
        "from typing import Optional",
        "",
        f"class {enum_name}(enum.IntEnum):",
    ]
    for v in enum_def["values"]:
        out.append(f"    {v['device_type']} = {v['value']}")
    out.append("")
    out.append("@dataclass(frozen=True)")
    out.append("class KnownDevice:")
    out.append("    full_name: str")
    out.append(f"    device_type: {enum_name}")
    out.append("    device_version: int")
    out.append("    hardware_revision: Optional[str]")
    out.append("")
    out.append("KNOWN_DEVICES: list[KnownDevice] = [")
    for d in known:
        dt = d["device_type"]
        dv = d["hardware_version"]["device_version"]
        hr = d["hardware_version"]["hardware_revision"]
        hr_py = "None" if hr is None else f'"{hr}"'
        out.append(f'    KnownDevice("{d["full_name"]}", {enum_name}.{dt}, {dv}, {hr_py}),')
    out.append("]")
    out.append("")
    out.append("KNOWN_DEVICES_BY_NAME: dict[str, KnownDevice] = {")
    out.append("    d.full_name: d for d in KNOWN_DEVICES")
    out.append("}")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# __init__.py for the generated package
# ---------------------------------------------------------------------------

def init_py(layout: dict) -> str:
    # Flag and enum classes of the layout are exported too.
    classes = []
    for fname, fdef in layout["fields"].items():
        if fdef.get("bit_mapping"):
            classes.append(pascal(fname) + "Flags")
        if fdef.get("enum_values"):
            classes.append(pascal(fname))
    names = ", ".join(["DosimeterEeprom"] + classes)
    return (
        "# Auto-generated — do not edit manually.\n"
        "from .xdos_devices import DeviceType, KnownDevice, KNOWN_DEVICES, KNOWN_DEVICES_BY_NAME\n"
        f"from .eeprom_layout import ({names},\n"
        "                            FORMAT_VERSION_LATEST, RECORD_SIZE_BY_VERSION)\n"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    GENERATED_DIR.mkdir(exist_ok=True)

    with open(REPO_ROOT / "eeprom_layout.yaml") as f:
        eeprom_data = yaml.safe_load(f)
    layout = eeprom_data["eeprom_layout"]

    with open(REPO_ROOT / "xDOS_devices.yaml") as f:
        dev_data = yaml.safe_load(f)

    files = {
        "eeprom_layout.h": eeprom_h(layout),
        "eeprom_layout.py": eeprom_py(layout),
        "xdos_devices.h": devices_h(dev_data),
        "xdos_devices.py": devices_py(dev_data),
        "__init__.py": init_py(layout),
    }

    for name, content in files.items():
        path = GENERATED_DIR / name
        path.write_text(content)
        print(f"  wrote {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
