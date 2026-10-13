"""Wire width/state checks in a fresh cell, with motion sending disabled."""

from config import LIB, LAYER, PCELL_LIB, PCELL_CELL, artifact_path

from datetime import datetime
import json
from pathlib import Path

from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.layout import layout_create_rect


def main():
    c = VirtuosoClient.from_env()
    lib = LIB
    cell = 'VB_NUMERIC_WIRE_REFRESH_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    results = []

    def check(name, code, expected=None):
        result = c.execute_skill(code)
        row = dict(name=name, output=result.output, errors=result.errors, warnings=result.warnings)
        results.append(row)
        print(name, result)
        if not result.ok or result.warnings or (expected is not None and result.output != expected):
            raise AssertionError(row)

    check('fresh cell', f'ddGetObj("{lib}" "{cell}" "layout")', 'nil')
    with c.layout.create(lib, cell) as lay:
        lay.add(layout_create_rect(LAYER, 'drawing', 0, 0, 8, 3))
    opened = c.open_window(lib, cell, view='layout')
    if not opened.ok:
        raise RuntimeError(opened)
    check('save state; disable all motion sends', 'progn(vbnWireTestWin=hiGetCurrentWindow() '
          'vbnWireTestCv=geGetEditCellView(vbnWireTestWin) '
          'vbnWireTestMemory=vbnRememberedNumber vbnWireTestDryRun=vbnWireRefreshDryRun '
          'vbnWireRefreshDryRun=t vbnWireTestView=hiGetViewBBox(vbnWireTestWin) t)', 't')
    try:
        check('start own wire', 'hiEnqueueCmd("leHiCreateWire(vbnWireTestWin)")', 't')
        check('wire first point', 'progn(addPoint(2:5) '
              'vbnWireTestView=hiGetViewBBox(vbnWireTestWin) '
              'vbnWireTestPoints=hiGetCurrentEnterFunPoints() '
              'hiGetCurrentCmd(vbnWireTestWin))', '"Wire"')
        for value in ('1.0', '0.5'):
            check('confirm ' + value, f'progn(vbnHotkey(nil) vbnDigits="{value}" vbnConfirm())', 't')
            check('preserve wire ' + value, 'list(hiGetCurrentCmd(vbnWireTestWin) '
                  'hiGetCurrentForm()~>wireWidth~>value '
                  'equal(hiGetViewBBox(vbnWireTestWin) vbnWireTestView) '
                  'equal(hiGetCurrentEnterFunPoints() vbnWireTestPoints) '
                  'vbnTrackingRefreshQueue)', f'("Wire" {value} t t nil)')
    finally:
        check('cancel own wire; restore state', 'progn(hiSetCurrentWindow(vbnWireTestWin) '
              'when(vbnActive vbnStop()) '
              'when(hiGetCurrentCmd(vbnWireTestWin) cancelEnterFun(hiGetCurrentForm())) '
              'vbnRememberedNumber=vbnWireTestMemory vbnWireRefreshDryRun=vbnWireTestDryRun t)', 't')
    check('original rectangle preserved', 'list(length(vbnWireTestCv~>shapes) '
          'car(vbnWireTestCv~>shapes)~>bBox)', '(1 ((0.0 0.0) (8.0 3.0)))')
    artifact_path('wire-refresh-verification.json').write_text(
        json.dumps(dict(cell=f'{lib}/{cell}/layout', results=results,
                        limitation='No real motion events sent; native visible rubberband needs human retest.'),
                   indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
