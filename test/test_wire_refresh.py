"""Check synthetic notification behavior with a fake X11 interface only."""

from config import LIB, LAYER, PCELL_LIB, PCELL_CELL, artifact_path

import unittest
from wire_refresh import refresh


class FakeX11:
    def __init__(self, *, moved=False, left=False, state=0):
        self.events = []
        self.calls = 0
        self.moved, self.left, self.state = moved, left, state

    def target(self, pid, title):
        self.calls += 1
        if pid != 42 or title != 'LIB CELL layout' or (self.left and self.calls > 1):
            return None
        shift = 7 if self.moved and self.calls > 1 else 0
        return dict(window=10, root=1, x=30+shift, y=40,
                    root_x=130+shift, root_y=140, state=self.state,
                    width=200, height=100)

    def motion(self, point, dx=0):
        self.events.append((point['window'], point['x']+dx, point['y'],
                            point['root_x']+dx, point['root_y']))


class WireRefreshTests(unittest.TestCase):
    def test_offset_then_original_coordinates(self):
        x = FakeX11()
        result = refresh(x, 42, 'LIB CELL layout', pause=lambda _: None)
        self.assertEqual(x.events, [(10, 31, 40, 131, 140), (10, 30, 40, 130, 140)])
        self.assertTrue(result['pointer_unchanged'])

    def test_user_motion_is_not_overwritten(self):
        x = FakeX11(moved=True)
        result = refresh(x, 42, 'LIB CELL layout', pause=lambda _: None)
        self.assertEqual(x.events[-1], (10, 37, 40, 137, 140))
        self.assertFalse(result['pointer_unchanged'])

    def test_no_events_when_dry_run(self):
        x = FakeX11()
        self.assertEqual(refresh(x, 42, 'LIB CELL layout', True)['status'], 'dry-run')
        self.assertEqual(x.events, [])

    def test_wrong_target_or_held_button_is_rejected(self):
        for pid, title, state in [(43, 'LIB CELL layout', 0),
                                  (42, 'OTHER layout', 0), (42, 'LIB CELL layout', 0x100)]:
            with self.subTest(pid=pid, title=title, state=state):
                x = FakeX11(state=state)
                self.assertEqual(refresh(x, pid, title)['status'], 'skipped')
                self.assertEqual(x.events, [])

    def test_no_return_event_into_changed_target(self):
        x = FakeX11(left=True)
        self.assertEqual(refresh(x, 42, 'LIB CELL layout', pause=lambda _: None)['status'], 'interrupted')
        self.assertEqual(len(x.events), 1)


if __name__ == '__main__':
    unittest.main()
