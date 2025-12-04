#!/usr/bin/env python3
"""
Mini BDX Runtime - Self Test Script
- Verifies imports and versions for required dependencies
- Runs tiny functional checks (NumPy/SciPy math, pygame headless surface, OpenCV ops)
- Skips hardware-specific tests unless hardware/driver detected
Safe for Raspberry Pi Zero 2 W (aarch64, Python 3.13)
"""

from __future__ import annotations
import os, sys, platform, time, json, traceback
from typing import Dict, Any

REPORT: Dict[str, Any] = {"start": time.time(), "tests": []}

def add_result(name: str, ok: bool, info: str = "", details: str = ""):
    REPORT["tests"].append({
        "name": name, "ok": bool(ok), "info": info, "details": details
    })
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}: {info}")
    if details and not ok:
        print(details)

def section(title: str):
    print("\n" + "="*8 + " " + title + " " + "="*8)

def sys_info():
    section("System Info")
    print("Python:", sys.version.replace("\n"," "))
    print("Platform:", platform.platform())
    print("Machine:", platform.machine())
    print("Processor:", platform.processor())
    # Memory / Swap (Linux)
    try:
        meminfo = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k,v = line.split(":",1)
                meminfo[k.strip()] = v.strip()
        print("MemTotal:", meminfo.get("MemTotal"))
        print("SwapTotal:", meminfo.get("SwapTotal"))
    except Exception:
        pass

def test_import_version(module_name: str):
    try:
        mod = __import__(module_name)
        ver = getattr(mod, "__version__", "OK")
        add_result(f"import {module_name}", True, str(ver))
        return mod, ver
    except Exception as e:
        add_result(f"import {module_name}", False, f"{e.__class__.__name__}: {e}", traceback.format_exc())
        return None, None

def test_numpy_scipy():
    section("NumPy / SciPy quick checks")
    ok = True
    try:
        import numpy as np
        import scipy.fft as sfft
        a = np.arange(9, dtype=np.float64).reshape(3,3)
        b = np.eye(3)
        c = a @ b
        _ = sfft.fft([1.0, 0.0, -1.0, 0.0])
        ok = ok and (c[0,0] == 0.0 and c.shape == (3,3))
        add_result("numpy dot/shape", ok, "OK" if ok else "unexpected result")
    except Exception as e:
        add_result("numpy/scipy", False, f"{e.__class__.__name__}: {e}", traceback.format_exc())

def test_onnxruntime():
    section("ONNX Runtime quick checks")
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        info = "providers=" + ",".join(providers)
        add_result("onnxruntime providers", True, info)
        # We only validate provider availability here (model exec requires bundling an ONNX file).
    except Exception as e:
        add_result("onnxruntime import/providers", False, f"{e.__class__.__name__}: {e}", traceback.format_exc())

def test_pygame_headless():
    section("pygame headless check")
    try:
        import os
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        import pygame
        pygame.init()
        surf = pygame.Surface((32, 32))
        surf.fill((120, 200, 80))
        pygame.quit()
        add_result("pygame surface create", True, "OK (dummy drivers)")
    except Exception as e:
        add_result("pygame surface create", False, f"{e.__class__.__name__}: {e}", traceback.format_exc())

def test_cv2_ops():
    section("OpenCV basic ops")
    try:
        import cv2, numpy as np
        img = (np.zeros((32,32), dtype=np.uint8))
        img[8:24, 8:24] = 255
        edges = cv2.Canny(img, 50, 150)
        ok = edges is not None and edges.shape == img.shape
        info = f"cv2={cv2.__version__}, SIFT={'yes' if hasattr(cv2,'SIFT_create') else 'no'}"
        add_result("opencv canny", ok, info)
    except Exception as e:
        add_result("opencv basic", False, f"{e.__class__.__name__}: {e}", traceback.format_exc())

def test_pypot_import():
    section("pypot import")
    try:
        import pypot
        add_result("pypot import", True, getattr(pypot, "__version__", "OK"))
    except Exception as e:
        add_result("pypot import", False, f"{e.__class__.__name__}: {e}", traceback.format_exc())

def test_bno055_optional():
    section("BNO055 optional test")
    # Only try to fully init if I2C device exists and backend likely present.
    try:
        import importlib, os
        have_i2c = any(os.path.exists(p) for p in ("/dev/i2c-1","/dev/i2c-0"))
        have_dio = False
        try:
            import digitalio  # provided by Blinka
            from digitalio import DigitalInOut  # noqa: F401
            have_dio = True
        except Exception:
            pass

        # Always test import of module itself:
        try:
            from adafruit_bno055 import BNO055_I2C  # noqa: F401
            import_ok = True
        except Exception as e:
            add_result("adafruit_bno055 import", False, f"{e.__class__.__name__}: {e}", traceback.format_exc())
            return

        add_result("adafruit_bno055 import", True, "OK")

        # Only try to talk to hardware if i2c node exists and backend present
        if have_i2c and have_dio and os.environ.get("BNO_SELFTEST","0") == "1":
            import board, busio
            from adafruit_bno055 import BNO055_I2C
            i2c = busio.I2C(board.SCL, board.SDA)
            sensor = BNO055_I2C(i2c)
            temp = sensor.temperature
            add_result("BNO055 temperature read", temp is not None, f"value={temp}")
        else:
            msg = "skipped (no /dev/i2c-* or digitalio backend, or BNO_SELFTEST!=1)"
            add_result("BNO055 hardware test", True, msg)
    except Exception as e:
        add_result("BNO055 block", False, f"{e.__class__.__name__}: {e}", traceback.format_exc())

def test_rustypot_import():
    section("rustypot import")
    try:
        import rustypot  # noqa: F401
        add_result("rustypot import", True, "OK")
    except Exception as e:
        add_result("rustypot import", False, f"{e.__class__.__name__}: {e}", traceback.format_exc())

def test_openai_import():
    section("openai import (no network)")
    try:
        import openai  # noqa: F401
        key = os.environ.get("OPENAI_API_KEY")
        info = "API key set" if key else "API key not set"
        add_result("openai import", True, info)
    except Exception as e:
        add_result("openai import", False, f"{e.__class__.__name__}: {e}", traceback.format_exc())

def main():
    sys_info()
    section("Import / version checks")
    for mod in ["numpy","scipy","onnxruntime","pygame","pypot","wget","cv2","rustypot","adafruit_bno055","openai"]:
        test_import_version(mod)

    test_numpy_scipy()
    test_onnxruntime()
    test_pygame_headless()
    test_cv2_ops()
    test_pypot_import()
    test_bno055_optional()
    test_rustypot_import()
    test_openai_import()

    REPORT["end"] = time.time()
    REPORT["duration_sec"] = round(REPORT["end"] - REPORT["start"], 2)

    print("\n======== SUMMARY ========")
    passed = sum(1 for t in REPORT["tests"] if t["ok"])
    total = len(REPORT["tests"])
    print(f"Passed {passed}/{total} tests in {REPORT['duration_sec']}s.")

    # Save JSON report next to this script
    try:
        import pathlib, json
        out = pathlib.Path("mini_bdx_selftest_report.json")
        out.write_text(json.dumps(REPORT, indent=2))
        print(f"Report saved to {out.resolve()}")
    except Exception:
        pass

if __name__ == "__main__":
    main()
