"""Capture Play Store screenshots from a connected Android device.

    python tools/capture_screenshots.py [out_dir]

The phone has to be plugged in with USB debugging on and the app has to be
installed. Each screen is opened with a tap, given a moment to settle, then
grabbed with `adb exec-out screencap -p`.

Screens are captured at the phone's own resolution (the Galaxy A15 is
1080 x 2340). Play accepts that directly as long as the long edge is at
least 1920 and the aspect ratio is 16:9 or 9:16.
"""
import subprocess
import sys
import time
from pathlib import Path

ADB = r"C:\Users\Universe\AppData\Local\Android\platform-tools\adb.exe"
PACKAGE = "com.hivepulse.akane"
ACTIVITY = "com.hivepulse.akane/org.kivy.android.PythonActivity"

# Home screen button rows on the Galaxy A15 (1080 x 2340). The buttons are a
# single full-width column, so only the y coordinate matters.
HOME_BUTTONS = [
    ("today", 409),
    ("flashcards", 549),
    ("voice", 691),
    ("workbook", 832),
    ("reading", 979),
    ("listening", 1121),
    ("speaking", 1265),
    ("news", 1408),
    ("shadowing", 1550),
    ("model", 1692),
    ("progress", 1836),
    ("settings", 1978),
    ("about", 2120),
]

# The store shots we actually want, in order.
WANTED = ["today", "flashcards", "speaking", "reading", "progress", "about"]


def adb(*args, binary=False):
    cmd = [ADB] + list(args)
    if binary:
        return subprocess.run(cmd, capture_output=True, check=True).stdout
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def shell(cmd):
    return adb("shell", cmd)


def size():
    out = shell("wm size")
    for line in out.splitlines():
        if "x" in line:
            w, h = line.strip().split(":")[-1].strip().split("x")
            return int(w), int(h)
    return 1080, 2340


def tap(x, y):
    shell("input tap %d %d" % (x, y))
    time.sleep(1.2)


def back():
    shell("input keyevent 4")
    time.sleep(1.0)


def grab(name, out_dir):
    data = adb("exec-out", "screencap", "-p", binary=True)
    path = out_dir / ("%s.png" % name)
    path.write_bytes(data)
    print("captured", path.name, len(data), "bytes")


def launch():
    """Start the app fresh. The Android back key exits the app rather than
    popping the Kivy screen stack, so every screen is reached from a fresh
    launch instead of navigating back."""
    shell("am force-stop %s" % PACKAGE)
    time.sleep(0.5)
    shell("am start -n %s" % ACTIVITY)
    time.sleep(9.0)


def main():
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/store_screenshots")
    out_dir.mkdir(parents=True, exist_ok=True)

    w, h = size()
    print("device screen:", w, "x", h)

    index = 0
    for name, y in HOME_BUTTONS:
        if name not in WANTED:
            continue
        index += 1
        launch()
        tap(540, y)
        time.sleep(2.0)
        grab("%02d_%s" % (index, name), out_dir)

    print("done ->", out_dir)


if __name__ == "__main__":
    main()
