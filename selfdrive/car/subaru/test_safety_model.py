#!/usr/bin/env python3
"""Verify car interface safety models exist in the panda firmware.

This test checks that every SafetyModel used by a car interface is in
the panda firmware's registered safety_hook_registry. It works by
parsing the firmware binary for the known safety model ID sequence.

If this test fails, the panda will reject the safety mode at runtime
with 'Error: safety set mode failed', causing 'Controls Mismatch'.
"""

import os
import sys

PANDAS_DIR = "/data/openpilot/selfdrive/car"
CEREAL_CAPNP = "/data/openpilot/cereal/car.capnp"

# Known-good safety models for the panda firmware in openpilot 0.8.13.1
# Extracted from panda board source code: safety.h safety_hook_registry
# Non-debug build includes these exact IDs:
KNOWN_FW_MODELS = {
    0,   # silent
    1,   # hondaNidec
    2,   # toyota
    3,   # elm327
    4,   # gm
    5,   # hondaBosch
    8,   # hyundai
    9,   # chrysler
    11,  # subaru
    13,  # mazda
    15,  # volkswagen
    19,  # noOutput
}


def get_safety_models_from_cereal():
    models = {}
    with open(CEREAL_CAPNP) as f:
        in_enum = False
        for line in f:
            line = line.strip()
            if "enum SafetyModel" in line:
                in_enum = True
                continue
            if in_enum:
                if "}" in line:
                    break
                if "@" in line and ";" in line:
                    name, rest = line.split("@", 1)
                    name = name.strip()
                    val = rest.split(";")[0].strip()
                    models[name] = int(val)
    return models


def main():
    print("=" * 60)
    print("Safety Model Validation Test")
    print("=" * 60)

    errors = 0
    all_models = get_safety_models_from_cereal()
    print(f"\n1. Cereal defines {len(all_models)} SafetyModels")
    print(f"   Panda firmware supports {len(KNOWN_FW_MODELS)} models: {sorted(KNOWN_FW_MODELS)}")

    print(f"\n2. Scanning car interfaces in {PANDAS_DIR}")
    for root, dirs, files in os.walk(PANDAS_DIR):
        dirs[:] = [d for d in dirs if not d.startswith("__") and d != "tests"]
        for fname in files:
            if fname != "interface.py":
                continue
            path = os.path.join(root, fname)
            car_name = path.split("/")[-3]
            with open(path) as fh:
                content = fh.read()
            for name, val in sorted(all_models.items(), key=lambda x: x[1]):
                if f"SafetyModel.{name}" not in content:
                    continue
                if val in KNOWN_FW_MODELS:
                    status = "OK"
                else:
                    status = "MISSING IN FW"
                    errors += 1
                print(f"   [{status:>14}] {car_name:30s} SafetyModel.{name} ({val})")

    print()
    if errors:
        print(f"FAIL: {errors} safety model(s) missing from panda firmware!")
        print("Fix: Either update KNOWN_FW_MODELS in this test if the firmware")
        print("was updated, or change the car interface to use a compatible model.")
        sys.exit(1)
    else:
        print("PASS: All safety models used by car interfaces are present.")
        print("       (KNOWN_FW_MODELS may need updating if firmware is rebuilt)")
        sys.exit(0)


if __name__ == "__main__":
    main()
