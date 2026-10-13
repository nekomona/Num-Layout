"""Bridge-only regression checks; creates fresh cells and sends no mouse events."""

from config import LIB, LAYER, PCELL_LIB, PCELL_CELL, artifact_path

from datetime import datetime
import json
from pathlib import Path

from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.layout import layout_create_rect


def main():
    c = VirtuosoClient.from_env()
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    lib = LIB
    leaf = 'VB_NUMERIC_VIS_LEAF_' + stamp
    top = 'VB_NUMERIC_FEEDBACK_' + stamp
    checks = []

    def run(name, code, expected=None):
        result = c.execute_skill(code)
        record = dict(name=name, output=result.output, errors=result.errors,
                      warnings=result.warnings)
        checks.append(record)
        print(name, result)
        if not result.ok or result.warnings or (expected is not None and result.output != expected):
            raise AssertionError(record)
        return result.output

    for cell in (leaf, top):
        run('fresh ' + cell, f'ddGetObj("{lib}" "{cell}" "layout")', 'nil')
    with c.layout.create(lib, leaf) as lay:
        lay.add(layout_create_rect(LAYER, 'drawing', 0, 0, 4, 2))
    with c.layout.create(lib, top) as lay:
        lay.add(layout_create_rect(LAYER, 'drawing', 0, 0, 8, 3))
        lay.add(layout_create_rect(LAYER, 'drawing', 12, 8, 20, 11))
        lay.add(f'dbCreateInstByMasterName(cv "{lib}" "{leaf}" "layout" '
                '"child" 30:0 "R0")')
        lay.add(f'dbCreateSimpleMosaic(cv dbOpenCellViewByType("{lib}" "{leaf}" "layout") '
                '"array" 40:0 "R0" 2 2 5 5)')
    opened = c.open_window(lib, top, view='layout')
    if not opened.ok:
        raise RuntimeError(opened)
    # open_window makes the newly created window current.
    run('test window', 'progn(vbnTestWin=hiGetCurrentWindow() '
        'vbnTestCv=geGetEditCellView(vbnTestWin) '
        'vbnTestRemembered=vbnRememberedNumber '
        f'equal(vbnTestCv~>cellName "{top}"))', 't')
    run('visible M4', f'leSetLayerVisible(list("{LAYER}" "drawing") t '
        'techGetTechFile(ddGetObj(vbnTestCv~>libName)))', 't')
    run('source', 'progn(vbnTestSource=car(setof(fig vbnTestCv~>shapes '
        'equal(fig~>bBox list(0:0 8:3)))) geDeselectAllFig(vbnTestCv) '
        'vbnTestChild=car(setof(i vbnTestCv~>instances i~>name == "child")) '
        'geSelectFig(vbnTestSource))', 't')
    run('contour start', 'progn(vbnHotkey(t) vbnDigits="0.5" '
        'vbnConfirm() list(vbnActive vbnKind vbnPhase))', '(t contour 2)')
    run('source rect pivot', 'progn(vbnHotkey(t) vbnContourSelectPivot(4:1) '
        'list(vbnContourPivot vbnContourEdges))', '(((0.0 0.0) (8.0 3.0)) nil)')
    run('rect advance', 'progn(vbnConfirm() vbnPhase)', '3')
    run('escape to pivot', 'progn(vbnEscape() vbnPhase)', '2')
    run('four source edges', 'progn(vbnHotkey(nil) '
        'foreach(p list(4:0 8:1 4:3 0:1) vbnContourSelectPivot(p)) '
        'list(length(vbnContourEdges) vbnContourPivot))', '(4 ((0.0 0.0) (8.0 3.0)))')
    run('switch preserves edges', 'progn(vbnHotkey(t) vbnHotkey(nil) '
        'length(vbnContourEdges))', '4')
    run('edge advance', 'progn(vbnConfirm() vbnPhase)', '3')
    run('escape for separate pivot', 'progn(vbnEscape() vbnPhase)', '2')
    run('separate rect pivot', 'progn(vbnHotkey(t) vbnContourSelectPivot(16:9) '
        'vbnContourPivot)', '((12.0 8.0) (20.0 11.0))')
    run('separate rect advance', 'progn(vbnConfirm() vbnPhase)', '3')
    run('escape for separate edges', 'progn(vbnEscape() vbnPhase)', '2')
    run('four separate edges', 'progn(vbnHotkey(nil) '
        'foreach(p list(16:8 20:9 16:11 12:9) vbnContourSelectPivot(p)) '
        'list(length(vbnContourEdges) vbnContourPivot))', '(4 ((12.0 8.0) (20.0 11.0)))')
    run('recompute pivot on confirm', 'progn(vbnContourPivot=nil '
        'vbnConfirm() list(vbnPhase vbnContourPivot))', '(3 ((12.0 8.0) (20.0 11.0)))')
    run('stop preserves source', 'progn(vbnStop() vbnTestSource~>bBox)',
        '((0.0 0.0) (8.0 3.0))')

    def pick_checks(label, expected):
        run(label, 'let((vbnWindow vbnKind) vbnWindow=vbnTestWin '
            'list(when(vbnPickCandidate(vbnTestWin 32:0) t) '
            'when(vbnContourRectAtPoint(vbnTestWin 32:1) t) '
            'when(vbnPickCandidate(vbnTestWin 42:0) t)))', expected)

    run('display hierarchy on', 'progn(vbnTestWin~>startLevel=0 '
        'vbnTestWin~>stopLevel=32 t)', 't')
    pick_checks('expanded child and mosaic', '(t t t)')
    run('display hierarchy off', 'progn(vbnTestWin~>stopLevel=0 t)', 't')
    pick_checks('collapsed child and mosaic', '(nil nil nil)')
    run('child override on', 'geSetInstViewLevel(vbnTestWin vbnTestChild 0 1)', 't')
    pick_checks('expanded instance override', '(t t nil)')
    run('child override off', 'geSetInstViewLevel(vbnTestWin vbnTestChild 0 0)', 't')
    pick_checks('collapsed instance override', '(nil nil nil)')
    run('restore view levels', 'progn(vbnTestWin~>stopLevel=32 '
        'geDeleteAllInstViewLevel(vbnTestWin) t)', 't')

    run('native path start', 'hiEnqueueCmd("leHiCreatePath(vbnTestWin)")', 't')
    try:
        run('path point', 'progn(addPoint(2:5) '
            'vbnTestView=hiGetViewBBox(vbnTestWin) '
            'vbnTestPoints=hiGetCurrentEnterFunPoints() '
            'vbnHotkey(nil) vbnDigits="1.0" vbnConfirm())', 't')
        # This bridge call runs after the queued refresh.
        run('path preserved after refresh', 'list(hiGetCurrentCmd(vbnTestWin) '
            'hiGetCurrentForm()~>pathWidth~>value '
            'equal(hiGetViewBBox(vbnTestWin) vbnTestView) '
            'equal(hiGetCurrentEnterFunPoints() vbnTestPoints) '
            'vbnTrackingRefreshQueue)', '("Path" 1.0 t t nil)')
        run('second width', 'progn(vbnHotkey(nil) vbnDigits="0.5" vbnConfirm())', 't')
        run('second refresh preserves path', 'list(hiGetCurrentCmd(vbnTestWin) '
            'hiGetCurrentForm()~>pathWidth~>value '
            'equal(hiGetViewBBox(vbnTestWin) vbnTestView) '
            'equal(hiGetCurrentEnterFunPoints() vbnTestPoints) '
            'vbnTrackingRefreshQueue)', '("Path" 0.5 t t nil)')
    finally:
        run('cancel own path', 'progn(when(vbnActive vbnStop()) '
            'when(hiGetCurrentCmd(vbnTestWin) cancelEnterFun(hiGetCurrentForm())) t)', 't')
        run('restore numeric memory', 'progn(vbnRememberedNumber=vbnTestRemembered t)', 't')
    run('source unchanged', 'vbnTestSource~>bBox', '((0.0 0.0) (8.0 3.0))')
    report = dict(cell=f'{lib}/{top}/layout', checks=checks,
                  limitation='No mouse events; native rubberband visibility needs human retest.')
    artifact_path('feedback-verification.json').write_text(
        json.dumps(report, indent=2), encoding='utf-8')
    print(report['cell'])


if __name__ == '__main__':
    main()
