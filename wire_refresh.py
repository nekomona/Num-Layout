"""Nudge the X11 pointer diagonally and return it to refresh native Wire tracking.

Invoked by Virtuoso's ipcBeginProcess, so DISPLAY/XAUTHORITY are inherited.
Uses XTest motion only: no focus, button, or keyboard changes. Return motion is
skipped if the user moves the pointer, holds a button, or leaves the layout.
"""

import argparse
import ctypes as C
import ctypes.util
import json
import time


NUDGE_X, NUDGE_Y = 32, 16  # Screen pixels; unequal components avoid 45-degree motion.


class Property(C.Structure):
    _fields_ = [('type', C.c_int), ('serial', C.c_ulong),
                ('send_event', C.c_int), ('display', C.c_void_p),
                ('window', C.c_ulong), ('atom', C.c_ulong),
                ('time', C.c_ulong), ('state', C.c_int)]


class Event(C.Union):
    _fields_ = [('property', Property), ('pad', C.c_long * 24)]


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
            'XCreateSimpleWindow': ([C.c_void_p, C.c_ulong, C.c_int, C.c_int,
                                    C.c_uint, C.c_uint, C.c_uint, C.c_ulong, C.c_ulong], C.c_ulong),
            'XSelectInput': ([C.c_void_p, C.c_ulong, C.c_long], C.c_int),
            'XChangeProperty': ([C.c_void_p, C.c_ulong, C.c_ulong, C.c_ulong,
                                 C.c_int, C.c_int, C.POINTER(C.c_ubyte), C.c_int], C.c_int),
            'XWindowEvent': ([C.c_void_p, C.c_ulong, C.c_long, C.POINTER(Event)], C.c_int),
            'XDestroyWindow': ([C.c_void_p, C.c_ulong], C.c_int),
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
        # An unmapped private window supplies diagnostic X-server timestamps.
        # XTest motion events receive their own timestamps from the server.
        self.clock_window = self.lib.XCreateSimpleWindow(self.display, self.root,
                                                         0, 0, 1, 1, 0, 0, 0)
        self.clock_atom = self.lib.XInternAtom(self.display, b'_VBN_REFRESH_CLOCK', 0)
        self.lib.XSelectInput(self.display, self.clock_window, 1 << 22)
        self.xtest = None

    def close(self):
        self.lib.XDestroyWindow(self.display, self.clock_window)
        self.lib.XCloseDisplay(self.display)

    def server_time(self):
        value, event = (C.c_ubyte * 1)(1), Event()
        self.lib.XChangeProperty(self.display, self.clock_window, self.clock_atom,
                                 19, 8, 0, value, 1)  # XA_INTEGER, PropModeReplace
        self.lib.XWindowEvent(self.display, self.clock_window, 1 << 22, C.byref(event))
        if event.property.type != 28 or not event.property.time:
            raise RuntimeError('X server did not supply a valid PropertyNotify timestamp')
        return event.property.time

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

    def enable_motion(self):
        if self.xtest is not None:
            return
        library = ctypes.util.find_library('Xtst')
        if not library:
            raise RuntimeError('libXtst is unavailable for Wire refresh')
        xtest = C.CDLL(library)
        xtest.XTestQueryExtension.argtypes = [C.c_void_p, *([C.POINTER(C.c_int)] * 4)]
        xtest.XTestQueryExtension.restype = C.c_int
        xtest.XTestFakeMotionEvent.argtypes = [C.c_void_p, C.c_int, C.c_int, C.c_int, C.c_ulong]
        xtest.XTestFakeMotionEvent.restype = C.c_int
        values = [C.c_int() for _ in range(4)]
        if not xtest.XTestQueryExtension(self.display, *(C.byref(v) for v in values)):
            raise RuntimeError('The Virtuoso X server does not support XTest')
        self.xtest = xtest

    def motion(self, point, dx=0, dy=0):
        self.enable_motion()
        # XSendEvent sets send_event=true, and native Wire ignores those events.
        # XTest generates ordinary server motion and supplies its own event time.
        if not self.xtest.XTestFakeMotionEvent(self.display, -1,
                point['root_x'] + dx, point['root_y'] + dy, 0):
            raise RuntimeError('XTest rejected the Wire pointer motion')
        self.lib.XSync(self.display, 0)
        return self.server_time()  # Diagnostic server time after the request.


def nudge_offset(point):
    """Keep the full diagonal inside the drawable; reverse either axis at borders."""
    offsets = []
    for coord, size, amount in ((point['x'], point['width'], NUDGE_X),
                                (point['y'], point['height'], NUDGE_Y)):
        if coord + amount < size:
            offsets.append(amount)
        elif coord - amount >= 0:
            offsets.append(-amount)
        else:
            return None
    return tuple(offsets)


def refresh(x11, pid, title, dry_run=False, pause=time.sleep):
    point = x11.target(pid, title)
    if not point or point['state'] & 0x1f00:
        return dict(status='skipped', reason='pointer/focus left the layout or a button is held')
    if point['width'] < 3 or not 0 <= point['x'] < point['width'] or not 0 <= point['y'] < point['height']:
        return dict(status='skipped', reason='pointer outside drawable target')
    offset = nudge_offset(point)
    if offset is None:
        return dict(status='skipped', reason='insufficient canvas room for diagonal nudge')
    dx, dy = offset
    x11.enable_motion()  # Extension availability check also runs without motion.
    if dry_run:
        return dict(status='dry-run', transport='xtest', target=point['window'], pointer=[point['root_x'], point['root_y']],
                    nudge_pixels=[dx, dy], server_time=x11.server_time())
    first_time = x11.motion(point, dx, dy)
    # Let Qt consume the first event instead of compressing both into one.
    pause(0.04)
    current = x11.target(pid, title)
    if not current or current['window'] != point['window']:
        return dict(status='interrupted', transport='xtest', reason='layout target changed')
    if current['state'] & 0x1f00 or (current['root_x'], current['root_y']) != (
            point['root_x'] + dx, point['root_y'] + dy):
        # Do not jump back over any intervening user movement or button action.
        return dict(status='interrupted', transport='xtest', reason='user input after nudge')
    return_time = x11.motion(point)
    final = x11.pointer(x11.root)
    return dict(status='moved-returned', transport='xtest', target=point['window'],
                nudge_pixels=[dx, dy],
                request_times=[first_time, return_time],
                pointer_restored=bool(final and (point['root_x'], point['root_y']) ==
                                     (final['root_x'], final['root_y'])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--check-clock', action='store_true',
                        help='Read X-server timestamps only; never send motion events')
    parser.add_argument('--check-xtest', action='store_true',
                        help='Query XTest availability only; never send motion events')
    args = parser.parse_args()
    x11 = X11()
    try:
        if args.check_xtest:
            before = x11.pointer(x11.root)
            x11.enable_motion()
            after = x11.pointer(x11.root)
            print(json.dumps(dict(status='xtest-check', motion_sent=False,
                pointer_before=[before['root_x'], before['root_y']] if before else None,
                pointer_after=[after['root_x'], after['root_y']] if after else None)))
        elif args.check_clock:
            first = x11.server_time()
            time.sleep(0.04)
            print(json.dumps(dict(status='clock-check', event_times=[first, x11.server_time()])))
        else:
            print(json.dumps(refresh(x11, args.pid, args.title, args.dry_run)))
    finally:
        x11.close()


if __name__ == '__main__':
    main()
