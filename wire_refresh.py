"""Send two X11 motion notifications without moving the physical pointer.

Invoked by Virtuoso's ipcBeginProcess, so DISPLAY/XAUTHORITY are inherited.
There are no pointer-warp, XTest, button, or keyboard calls in this helper.
"""

import argparse
import ctypes as C
import ctypes.util
import json
import time


class Motion(C.Structure):
    _fields_ = [('type', C.c_int), ('serial', C.c_ulong),
                ('send_event', C.c_int), ('display', C.c_void_p),
                ('window', C.c_ulong), ('root', C.c_ulong),
                ('subwindow', C.c_ulong), ('time', C.c_ulong),
                ('x', C.c_int), ('y', C.c_int),
                ('x_root', C.c_int), ('y_root', C.c_int),
                ('state', C.c_uint), ('is_hint', C.c_char),
                ('same_screen', C.c_int)]


class Event(C.Union):
    _fields_ = [('motion', Motion), ('pad', C.c_long * 24)]


class X11:
    def __init__(self):
        self.lib = C.CDLL(ctypes.util.find_library('X11'))
        signatures = {
            'XOpenDisplay': ([C.c_char_p], C.c_void_p),
            'XDefaultRootWindow': ([C.c_void_p], C.c_ulong),
            'XQueryPointer': ([C.c_void_p, C.c_ulong,
                              C.POINTER(C.c_ulong), C.POINTER(C.c_ulong),
                              *([C.POINTER(C.c_int)] * 4),
                              C.POINTER(C.c_uint)], C.c_int),
            'XInternAtom': ([C.c_void_p, C.c_char_p, C.c_int], C.c_ulong),
            'XGetWindowProperty': ([C.c_void_p, C.c_ulong, C.c_ulong,
                                    C.c_long, C.c_long, C.c_int, C.c_ulong,
                                    C.POINTER(C.c_ulong), C.POINTER(C.c_int),
                                    C.POINTER(C.c_ulong), C.POINTER(C.c_ulong),
                                    C.POINTER(C.c_void_p)], C.c_int),
            'XFetchName': ([C.c_void_p, C.c_ulong, C.POINTER(C.c_void_p)], C.c_int),
            'XGetGeometry': ([C.c_void_p, C.c_ulong, C.POINTER(C.c_ulong),
                             C.POINTER(C.c_int), C.POINTER(C.c_int),
                             *([C.POINTER(C.c_uint)] * 4)], C.c_int),
            'XGetInputFocus': ([C.c_void_p, C.POINTER(C.c_ulong), C.POINTER(C.c_int)], C.c_int),
            'XSendEvent': ([C.c_void_p, C.c_ulong, C.c_int, C.c_long, C.POINTER(Event)], C.c_int),
            'XSync': ([C.c_void_p, C.c_int], C.c_int),
            'XFree': ([C.c_void_p], C.c_int),
            'XCloseDisplay': ([C.c_void_p], C.c_int),
        }
        for name, (args, result) in signatures.items():
            fn = getattr(self.lib, name)
            fn.argtypes, fn.restype = args, result
        self.display = self.lib.XOpenDisplay(None)
        if not self.display:
            raise RuntimeError('Cannot open the inherited Virtuoso X11 display')
        self.root = self.lib.XDefaultRootWindow(self.display)

    def close(self):
        self.lib.XCloseDisplay(self.display)

    def pointer(self, window):
        root, child = C.c_ulong(), C.c_ulong()
        rx, ry, x, y = (C.c_int() for _ in range(4))
        state = C.c_uint()
        if not self.lib.XQueryPointer(self.display, window, C.byref(root), C.byref(child),
                                     C.byref(rx), C.byref(ry), C.byref(x), C.byref(y), C.byref(state)):
            return None
        return dict(window=window, root=root.value, child=child.value,
                    root_x=rx.value, root_y=ry.value, x=x.value, y=y.value, state=state.value)

    def owner(self, window):
        atom = self.lib.XInternAtom(self.display, b'_NET_WM_PID', 1)
        if not atom:
            return None
        actual, count, remaining = C.c_ulong(), C.c_ulong(), C.c_ulong()
        fmt, data = C.c_int(), C.c_void_p()
        self.lib.XGetWindowProperty(self.display, window, atom, 0, 1, 0, 6,
                                   C.byref(actual), C.byref(fmt), C.byref(count),
                                   C.byref(remaining), C.byref(data))
        try:
            if data.value and fmt.value == 32 and count.value:
                return C.cast(data, C.POINTER(C.c_ulong))[0]
        finally:
            if data.value:
                self.lib.XFree(data)

    def name(self, window):
        data = C.c_void_p()
        self.lib.XFetchName(self.display, window, C.byref(data))
        try:
            return C.string_at(data).decode('utf-8', 'replace') if data.value else ''
        finally:
            if data.value:
                self.lib.XFree(data)

    def target(self, pid, title):
        path, window = [], self.root
        for _ in range(32):
            point = self.pointer(window)
            if not point:
                return None
            path.append((point, self.owner(window), self.name(window)))
            if not point['child']:
                break
            window = point['child']
        else:
            return None
        # Match ownership and layout title on the SAME ancestor, not a popup.
        if not any(owner == pid and title in name for _, owner, name in path):
            return None
        focus, revert = C.c_ulong(), C.c_int()
        self.lib.XGetInputFocus(self.display, C.byref(focus), C.byref(revert))
        if focus.value not in [p['window'] for p, _, _ in path]:
            return None
        point = path[-1][0]
        root, x, y = C.c_ulong(), C.c_int(), C.c_int()
        width, height, border, depth = (C.c_uint() for _ in range(4))
        self.lib.XGetGeometry(self.display, point['window'], C.byref(root), C.byref(x), C.byref(y),
                             C.byref(width), C.byref(height), C.byref(border), C.byref(depth))
        return dict(point, width=width.value, height=height.value)

    def motion(self, point, dx=0):
        event = Event()
        event.motion = Motion(6, 0, 1, self.display, point['window'], point['root'],
                              0, 0, point['x'] + dx, point['y'],
                              point['root_x'] + dx, point['root_y'],
                              point['state'], b'\0', 1)
        if not self.lib.XSendEvent(self.display, point['window'], 0, 1 << 6, C.byref(event)):
            raise RuntimeError('XSendEvent rejected the Wire motion notification')
        self.lib.XSync(self.display, 0)


def refresh(x11, pid, title, dry_run=False, pause=time.sleep):
    point = x11.target(pid, title)
    if not point or point['state'] & 0x1f00:
        return dict(status='skipped', reason='pointer/focus left the layout or a button is held')
    if point['width'] < 3 or not 0 <= point['x'] < point['width'] or not 0 <= point['y'] < point['height']:
        return dict(status='skipped', reason='pointer outside drawable target')
    if dry_run:
        return dict(status='dry-run', target=point['window'], pointer=[point['root_x'], point['root_y']])
    dx = 1 if point['x'] < point['width'] - 1 else -1
    x11.motion(point, dx)
    # Let Qt consume the first event instead of compressing both into one.
    pause(0.04)
    current = x11.target(pid, title)
    if not current or current['window'] != point['window']:
        return dict(status='interrupted', reason='layout target changed')
    # If the user moved meanwhile, restore tracking to their NEW position.
    x11.motion(current)
    return dict(status='sent', target=point['window'],
                pointer_unchanged=(point['root_x'], point['root_y']) ==
                                  (current['root_x'], current['root_y']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    x11 = X11()
    try:
        print(json.dumps(refresh(x11, args.pid, args.title, args.dry_run)))
    finally:
        x11.close()


if __name__ == '__main__':
    main()
