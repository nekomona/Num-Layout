"""Native group Copy and rotated EIP ruler regression; no mouse/key events."""

from config import LIB, LAYER, PCELL_LIB, PCELL_CELL, artifact_path

from datetime import datetime
import json
from pathlib import Path

from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.layout import layout_create_rect


def main():
    c = VirtuosoClient.from_env()
    lib = LIB
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    top, leaf = 'VB_NUMERIC_GROUP_TOP_' + stamp, 'VB_NUMERIC_GROUP_LEAF_' + stamp
    checks = []

    def check(name, code, expected=None):
        r = c.execute_skill(code)
        row = dict(name=name, output=r.output, errors=r.errors, warnings=r.warnings)
        checks.append(row)
        print(name, r)
        if not r.ok or r.warnings or (expected is not None and r.output != expected):
            raise AssertionError(row)
        return r.output

    check('idle caller', 'list(vbnActive hiGetCurrentCmd(hiGetCurrentWindow()))', '(nil nil)')
    for cell in (top, leaf):
        check('fresh ' + cell, f'ddGetObj("{lib}" "{cell}" "layout")', 'nil')
    check('save state', 'progn(vbnGroupTestOriginalWin=hiGetCurrentWindow() '
          'vbnGroupTestMemory=vbnRememberedNumber vbnGroupTestEnabled=vbnEnabled '
          'vbnGroupTestWin=nil vbnEnabled=t t)', 't')
    try:
        with c.layout.create(lib, leaf) as lay:
            lay.add(layout_create_rect(LAYER, 'drawing', 0, 0, 8, 3))
        with c.layout.create(lib, top) as lay:
            lay.add(layout_create_rect(LAYER, 'drawing', 100, 50, 108, 53))
            lay.add('let((fg) fg=dbCreateFigGroup(cv "copy_group" nil 100:50 "R0") '
                    'dbAddFigToFigGroup(fg car(cv~>shapes)))')
            lay.add('let((fg inst) '
                    f'inst=dbCreateInstByMasterName(cv "{lib}" "{leaf}" "layout" '
                    '"rotated_child" 200:100 "R90") '
                    'fg=dbCreateFigGroup(cv "nested_group" nil 200:100 "R0") '
                    'dbAddFigToFigGroup(fg inst))')
        opened = c.open_window(lib, top, view='layout')
        if not opened.ok:
            raise RuntimeError(opened)
        check('test references', 'progn(vbnGroupTestWin=hiGetCurrentWindow() '
              'vbnGroupTestCv=geGetEditCellView(vbnGroupTestWin) '
              'vbnGroupTestSource=car(vbnGroupTestCv~>shapes) '
              'vbnGroupTestCopyGroup=car(setof(g vbnGroupTestCv~>figGroups g~>name == "copy_group")) '
              'vbnGroupTestNestedGroup=car(setof(g vbnGroupTestCv~>figGroups g~>name == "nested_group")) '
              'vbnGroupTestInst=car(vbnGroupTestCv~>instances) t)', 't')
        check('source layer visible', f'leIsLayerVisible(list("{LAYER}" "drawing") '
              'techGetTechFile(vbnGroupTestCv))', 't')
        check('enter group edit', 'leSetEditFigGroup(vbnGroupTestCopyGroup vbnGroupTestWin)', 't')
        check('start group Copy', 'progn(geSelectFig(vbnGroupTestSource) '
              'hiEnqueueCmd("leHiCopy(vbnGroupTestWin)"))', 't')
        check('group context active', 'list(hiGetCurrentCmd(vbnGroupTestWin) '
              'equal(leGetEditFigGroup(vbnGroupTestWin) vbnGroupTestCopyGroup))', '("Copy" t)')
        check('native X/Y callbacks work with nil UI windowId',
              'let((windowId) vbnSetFormField(hiGetCurrentForm()~>copyXField 12.0) '
              'vbnSetFormField(hiGetCurrentForm()~>copyYField 0.0) t)', 't')
        check('pending N to J works in group edit with nil UI context',
              'let((windowId) vbnCountHotkey() vbnDigit("3") vbnHotkey(nil) '
              'list(vbnActive vbnKind vbnCopyCount() length(vbnGroupTestCv~>shapes)))',
              '(t distance 3 1)')
        check('group J confirmation with nil UI windowId',
              'let((savedDirection windowId) savedDirection=getd(quote(vbnDirection)) '
              'unwindProtect(progn(putd(quote(vbnDirection) lambda(() 1:0)) '
              'vbnDigits="12" vbnConfirm()) putd(quote(vbnDirection) savedDirection)))', 't')
        check('group copies and original box', 'list(length(vbnGroupTestCv~>shapes) '
              'vbnGroupTestSource~>bBox)', '(4 ((100.0 50.0) (108.0 53.0)))')
        check('leave temporary Copy and enter nested group',
              'progn(when(hiGetCurrentCmd(vbnGroupTestWin) cancelEnterFun(hiGetCurrentForm())) '
              'leReturnToTop(vbnGroupTestWin) '
              'leSetEditFigGroup(vbnGroupTestNestedGroup vbnGroupTestWin) '
              'geDeselectAllFig(vbnGroupTestCv) geSelectFig(vbnGroupTestInst) '
              'hiEnqueueCmd("leHiEditInPlace(vbnGroupTestWin)"))', 't')
        check('rotated group child edit context',
              f'equal(geGetEditCellView(vbnGroupTestWin)~>cellName "{leaf}")', 't')
        check('window and edit frames differ',
              'list(geWindowToEditPoint(vbnGroupTestWin 200:100) '
              'geWindowToEditPoint(vbnGroupTestWin 200:120) '
              'geEditToWindowPoint(vbnGroupTestWin 20:0))',
              '((0.0 0.0) (20.0 0.0) (200.0 120.0))')
        check('start native ruler in descended child',
              'progn(vbnGroupTestLeaf=geGetEditCellView(vbnGroupTestWin) '
              'hiEnqueueCmd(hiGetBindKey("Layout" "<Key>k")))', 't')
        check('native first point is in window frame',
              'progn(addPoint(200:100) '
              'list(hiGetCurrentCmd(vbnGroupTestWin) hiGetCurrentEnterFunPoints()))',
              '("Ruler" (((200.0 100.0) nil)))')
        check('J ruler confirmation uses edited-cell endpoints',
              'let((savedCursor) savedCursor=getd(quote(vbnContourCursorPoint)) '
              'unwindProtect(progn(putd(quote(vbnContourCursorPoint) lambda(() 200:110)) '
              'vbnHotkey(nil) vbnDigits="20" vbnConfirm()) '
              'putd(quote(vbnContourCursorPoint) savedCursor)))', 't')
        check('stored ruler local position and length',
              'mapcar(lambda((m) m~>points) '
              'setof(m vbnGroupTestLeaf~>markers m~>objType == "ruler"))',
              '(((0.0 0.0) (20.0 0.0)))')
        check('stored ruler renders at requested window points',
              'mapcar(lambda((p) geEditToWindowPoint(vbnGroupTestWin p)) '
              'car(setof(m vbnGroupTestLeaf~>markers m~>objType == "ruler"))~>points)',
              '((200.0 100.0) (200.0 120.0))')
        check('leaf source unchanged', 'list(length(vbnGroupTestLeaf~>shapes) '
              'car(vbnGroupTestLeaf~>shapes)~>bBox)', '(1 ((0.0 0.0) (8.0 3.0)))')
        check('save only fresh cells', 'progn(dbSave(vbnGroupTestLeaf) dbSave(vbnGroupTestCv) t)', 't')
    finally:
        check('restore caller', 'progn(when(vbnActive vbnStop()) '
              'when(vbnGroupTestWin && member(vbnGroupTestWin hiGetWindowList()) '
              'hiSetCurrentWindow(vbnGroupTestWin) '
              'when(hiGetCurrentCmd(vbnGroupTestWin) cancelEnterFun(hiGetCurrentForm())) '
              'leReturnToTop(vbnGroupTestWin)) '
              'vbnRememberedNumber=vbnGroupTestMemory vbnEnabled=vbnGroupTestEnabled '
              'hiSetActionChecked(vbnAction vbnEnabled nil) '
              'when(member(vbnGroupTestOriginalWin hiGetWindowList()) '
              'hiSetCurrentWindow(vbnGroupTestOriginalWin)) t)', 't')
    artifact_path('group-edit-verification.json').write_text(
        json.dumps(dict(cells=[f'{lib}/{top}/layout', f'{lib}/{leaf}/layout'], checks=checks,
                        limitation='No mouse/key events. Real group-descend cursor picking remains in test/README.md.'),
                   indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
