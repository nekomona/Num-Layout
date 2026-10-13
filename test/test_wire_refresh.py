"""Check XTest refresh and input-interruption behavior without live input."""

from config import LIB, LAYER, PCELL_LIB, PCELL_CELL, artifact_path

import unittest
from wire_refresh import X11, refresh


class FakeX11:
    root = 1

    def __init__(self, *, moved=False, left=False, state=0, button_after=False, x=30, width=200):
        self.events = []
        self.calls = 0
        self.moved, self.left, self.state = moved, left, state
        self.button_after = button_after
        self.x, self.width = x, width
        self.position = (100+x, 140)
        self.clock = 1000
        self.enabled = False

    def enable_motion(self):
        self.enabled = True

    def server_time(self):
        self.clock += 40
        return self.clock

    def target(self, pid, title):
        self.calls += 1
        if pid != 42 or title != 'LIB CELL layout' or (self.left and self.calls > 1):
            return None
        if self.moved and self.calls > 1:
            self.position = (137, 140)
        state = 0x100 if self.button_after and self.calls > 1 else self.state
        return dict(window=10, root=1, x=self.position[0]-100, y=40,
                    root_x=self.position[0], root_y=self.position[1], state=state,
                    width=self.width, height=100)

    def motion(self, point, dx=0):
        self.position = (point['root_x']+dx, point['root_y'])
        self.events.append(self.position)
        return self.server_time()

    def pointer(self, window):
        return dict(root_x=self.position[0], root_y=self.position[1])


class WireRefreshTests(unittest.TestCase):
    def test_nudge_and_exact_return(self):
        x = FakeX11()
        result = refresh(x, 42, 'LIB CELL layout', pause=lambda _: None)
        self.assertEqual(x.events, [(131, 140), (130, 140)])
        self.assertEqual(result['status'], 'moved-returned')
        self.assertTrue(result['pointer_restored'])

    def test_repeated_refresh_returns_each_time(self):
        x = FakeX11()
        first = refresh(x, 42, 'LIB CELL layout', pause=lambda _: None)
        second = refresh(x, 42, 'LIB CELL layout', pause=lambda _: None)
        self.assertEqual(first['request_times'], [1040, 1080])
        self.assertEqual(second['request_times'], [1120, 1160])
        self.assertEqual(x.events[:2], x.events[2:])
        self.assertEqual(x.position, (130, 140))

    def test_xtest_uses_absolute_root_coordinates_without_buttons_or_keys(self):
        class FakeLib:
            def XSync(self, display, discard):
                pass

        class FakeXTest:
            def __init__(self):
                self.calls = []

            def XTestFakeMotionEvent(self, display, screen, x, y, delay):
                self.calls.append((screen, x, y, delay))
                return 1

        x = X11.__new__(X11)
        x.lib, x.display, x.xtest = FakeLib(), None, FakeXTest()
        x.server_time = lambda: 1234
        point = FakeX11().target(42, 'LIB CELL layout')
        x.motion(point, 1)
        x.motion(point)
        self.assertEqual(x.xtest.calls, [(-1, 131, 140, 0), (-1, 130, 140, 0)])

    def test_user_motion_is_not_overwritten(self):
        x = FakeX11(moved=True)
        result = refresh(x, 42, 'LIB CELL layout', pause=lambda _: None)
        self.assertEqual(result['status'], 'interrupted')
        self.assertEqual(x.events, [(131, 140)])
        self.assertEqual(x.position, (137, 140))

    def test_button_press_after_nudge_prevents_return(self):
        x = FakeX11(button_after=True)
        result = refresh(x, 42, 'LIB CELL layout', pause=lambda _: None)
        self.assertEqual(result['status'], 'interrupted')
        self.assertEqual(len(x.events), 1)

    def test_no_events_when_dry_run(self):
        x = FakeX11()
        result = refresh(x, 42, 'LIB CELL layout', True)
        self.assertEqual(result['status'], 'dry-run')
        self.assertEqual(result['transport'], 'xtest')
        self.assertTrue(x.enabled)
        self.assertEqual(x.events, [])

    def test_wrong_target_or_held_button_is_rejected(self):
        for pid, title, state in [(43, 'LIB CELL layout', 0),
                                  (42, 'OTHER layout', 0), (42, 'LIB CELL layout', 0x100)]:
            with self.subTest(pid=pid, title=title, state=state):
                x = FakeX11(state=state)
                self.assertEqual(refresh(x, pid, title)['status'], 'skipped')
                self.assertEqual(x.events, [])

    def test_no_return_into_changed_target(self):
        x = FakeX11(left=True)
        self.assertEqual(refresh(x, 42, 'LIB CELL layout', pause=lambda _: None)['status'], 'interrupted')
        self.assertEqual(len(x.events), 1)

    def test_right_border_nudges_inward(self):
        x = FakeX11(x=199)
        result = refresh(x, 42, 'LIB CELL layout', pause=lambda _: None)
        self.assertEqual(x.events, [(298, 140), (299, 140)])
        self.assertTrue(result['pointer_restored'])

    def test_invalid_drawable_is_rejected(self):
        for x, width in [(30, 2), (-1, 200), (200, 200)]:
            fake = FakeX11(x=x, width=width)
            self.assertEqual(refresh(fake, 42, 'LIB CELL layout')['status'], 'skipped')
            self.assertEqual(fake.events, [])


if __name__ == '__main__':
    unittest.main()
