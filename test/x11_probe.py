"""Small XTest driver for manual smoke checks in the isolated testbench.

Run on the remote GUI host with: python3 x11_probe.py WINDOW_ID ACTION...
Actions are key:KEYSYM, chord:MODIFIER:KEYSYM, move:X:Y, click:X:Y,
where, or wait:MILLISECONDS.
This sends UI events only; it does not evaluate SKILL.
"""

import ctypes
import ctypes.util
import os
import subprocess
import sys
import time


def x11_env():
    pids = subprocess.check_output(["pgrep", "-u", os.environ["USER"], "-x", "virtuoso"], text=True).split()
    for pid in pids:
        data = open(f"/proc/{pid}/environ", "rb").read().split(b"\0")
        values = dict(item.split(b"=", 1) for item in data if b"=" in item)
        if b"DISPLAY" in values:
            os.environ["DISPLAY"] = values[b"DISPLAY"].decode()
            if b"XAUTHORITY" in values:
                os.environ["XAUTHORITY"] = values[b"XAUTHORITY"].decode()
            return
    raise RuntimeError("No Virtuoso X11 environment found")


def main():
    x11_env()
    win = int(sys.argv[1], 0)
    xlib = ctypes.CDLL(ctypes.util.find_library("X11"))
    xtst = ctypes.CDLL(ctypes.util.find_library("Xtst"))
    xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
    xlib.XOpenDisplay.restype = ctypes.c_void_p
    xlib.XSetInputFocus.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    xlib.XStringToKeysym.argtypes = [ctypes.c_char_p]
    xlib.XStringToKeysym.restype = ctypes.c_ulong
    xlib.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    xlib.XKeysymToKeycode.restype = ctypes.c_uint
    xlib.XFlush.argtypes = [ctypes.c_void_p]
    xlib.XQueryPointer.argtypes = [
        ctypes.c_void_p, ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong),
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_uint),
    ]
    xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    xtst.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    xtst.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
    display = xlib.XOpenDisplay(None)
    if not display:
        raise RuntimeError("XOpenDisplay failed")
    xlib.XSetInputFocus(display, win, 1, 0)
    xlib.XFlush(display)
    time.sleep(0.1)
    def keycode(name):
        sym = xlib.XStringToKeysym(name.encode())
        code = xlib.XKeysymToKeycode(display, sym)
        if not code:
            raise RuntimeError(f"Unknown keysym {name}")
        return code

    for action in sys.argv[2:]:
        parts = action.split(":")
        if parts[0] == "key":
            code = keycode(parts[1])
            xtst.XTestFakeKeyEvent(display, code, 1, 0)
            xtst.XTestFakeKeyEvent(display, code, 0, 0)
        elif parts[0] == "chord":
            modifier = keycode(parts[1])
            code = keycode(parts[2])
            xtst.XTestFakeKeyEvent(display, modifier, 1, 0)
            xtst.XTestFakeKeyEvent(display, code, 1, 0)
            xtst.XTestFakeKeyEvent(display, code, 0, 0)
            xtst.XTestFakeKeyEvent(display, modifier, 0, 0)
        elif parts[0] in ("move", "click"):
            x, y = map(int, parts[1:3])
            xtst.XTestFakeMotionEvent(display, -1, x, y, 0)
            xlib.XFlush(display)
            time.sleep(0.08)
            if parts[0] == "click":
                xtst.XTestFakeButtonEvent(display, 1, 1, 0)
                xtst.XTestFakeButtonEvent(display, 1, 0, 0)
        elif parts[0] == "wait":
            time.sleep(int(parts[1]) / 1000)
        elif parts[0] == "where":
            root = ctypes.c_ulong()
            child = ctypes.c_ulong()
            root_x = ctypes.c_int()
            root_y = ctypes.c_int()
            win_x = ctypes.c_int()
            win_y = ctypes.c_int()
            mask = ctypes.c_uint()
            xlib.XQueryPointer(
                display, win, ctypes.byref(root), ctypes.byref(child),
                ctypes.byref(root_x), ctypes.byref(root_y),
                ctypes.byref(win_x), ctypes.byref(win_y), ctypes.byref(mask),
            )
            print("pointer", root_x.value, root_y.value, win_x.value, win_y.value)
        else:
            raise ValueError(action)
        xlib.XFlush(display)
        time.sleep(0.12)
    print("sent", sys.argv[2:])


if __name__ == "__main__":
    main()
