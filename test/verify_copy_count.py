"""Exercise N with native Copy in a fresh cell; sends no mouse/key events."""

from config import artifact_path, LIB, LAYER

import argparse
from datetime import datetime
import json

from virtuoso_bridge import VirtuosoClient, SSHClient
from virtuoso_bridge.virtuoso.layout import layout_create_rect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lib', default=LIB)
    parser.add_argument('--layer', default=LAYER)
    args = parser.parse_args()
    c = VirtuosoClient.from_tunnel(SSHClient.from_env())
    cell = 'VB_NUMERIC_COPY_N_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    checks = []

    def check(name, code, expected=None, warning=None):
        r = c.execute_skill(code)
        row = dict(name=name, output=r.output, warnings=r.warnings, errors=r.errors)
        checks.append(row)
        print(name, r)
        if not r.ok or (expected is not None and r.output != expected):
            raise AssertionError(row)
        if warning:
            # This bridge version may leave warn() text in CIW only.
            if r.warnings and warning not in str(r.warnings):
                raise AssertionError(row)
        elif r.warnings:
            raise AssertionError(row)
        return r.output

    check('idle caller', 'list(vbnActive when(hiGetCurrentWindow() hiGetCurrentCmd(hiGetCurrentWindow())))', '(nil nil)')
    check('fresh cell', f'ddGetObj("{args.lib}" "{cell}" "layout")', 'nil')
    check('save caller state', 'progn(vbnCopyVerifyOriginalWin=hiGetCurrentWindow() '
          'vbnCopyVerifyMemory=vbnRememberedNumber vbnCopyVerifyEnabled=vbnEnabled '
          'vbnCopyVerifyXY=vbnRememberedXY vbnRememberedXY=nil '
          'vbnCopyVerifyNumber=leGetEnv("copyNumber") '
          'vbnCopyVerifyOrder=leGetEnv("copyOrder") '
          'vbnCopyVerifyWin=nil vbnCopyVerifyForm=nil '
          'vbnCopyVerifyKeys=mapcar(lambda((key) list(key hiGetBindKey("Layout" key))) '
          'list("<Key>n" "<Key>n EF" "<Key>j" "<Key>j EF" "<Key>2" '
          '"<Key>2 EF" "<Key>period" "<Key>period EF" "<Key>Return EF" '
          '"<Key>space EF" "<Key>BackSpace EF" "<Key>Escape EF" "None<Btn1Down> EF")) '
          'vbnRememberedNumber=123.5 vbnEnabled=t t)', 't')
    try:
        with c.layout.create(args.lib, cell) as lay:
            lay.add(layout_create_rect(args.layer, 'drawing', 0, 0, 8, 3))
        r = c.open_window(args.lib, cell, view='layout')
        if not r.ok:
            raise RuntimeError(r)
        check('start isolated Copy', 'progn(vbnCopyVerifyWin=hiGetCurrentWindow() '
              'vbnCopyVerifyCv=geGetEditCellView(vbnCopyVerifyWin) '
              'vbnCopyVerifySource=car(vbnCopyVerifyCv~>shapes) '
              'geSelectFig(vbnCopyVerifySource) '
              'hiEnqueueCmd("leHiCopy(vbnCopyVerifyWin)"))', 't')
        check('native Copy form', 'list(hiGetCurrentCmd(vbnCopyVerifyWin) '
              'hiGetCurrentForm()~>_formName)', '("Copy" "Copy")')
        check('save native form defaults', 'progn(vbnCopyVerifyForm=hiGetCurrentForm() '
              'vbnCopyVerifySnapOriginal=vbnCopyVerifyForm~>segSnapMode~>value '
              'vbnCopyVerifyRecursive=vbnCopyVerifyForm~>copyRecursive~>value t)', 't')
        check('N entry resets stale count and Single type',
              'progn(vbnSetFormField(hiGetCurrentForm()~>copyType "Single") '
              'vbnSetFormField(hiGetCurrentForm()~>number 7) vbnCountHotkey() '
              'list(vbnActive vbnKind vbnDigits vbnModeText() '
              'hiGetCurrentForm()~>copyType~>value hiGetCurrentForm()~>number~>value))',
              '(t copyCount "1" "COPY COUNT" "Step" 1)')
        check('integer-only typing and Backspace',
              'progn(vbnDigit(".") vbnDigit("2") vbnDigit("5") vbnBackspace() '
              'vbnDigit(".") list(vbnDigits vbnCurrentValue()))', '("2" 2)')
        check('Enter callback sets count without placement or J memory change',
              'progn(evalstring(hiGetBindKey("Layout" "<Key>Return EF")) '
              'list(vbnActive hiGetCurrentForm()~>number~>value '
              'hiGetCurrentCmd(vbnCopyVerifyWin) length(vbnCopyVerifyCv~>shapes) '
              'vbnRememberedNumber))', '(nil 2 "Copy" 1 123.5)')
        check('J entry preserves N count and adds hint', 'progn(vbnHotkey(nil) '
              'list(vbnKind vbnDigits hiGetCurrentForm()~>number~>value vbnModeText()))',
              '(distance "123.5" 2 "COPY DISTANCE [2 copies]")')
        check('J exit resets edited native count',
              'progn(vbnSetFormField(hiGetCurrentForm()~>number 5) vbnStop() '
              'hiGetCurrentForm()~>number~>value)', '1')
        check('N cancellation resets count; Copy survives',
              'progn(vbnCountHotkey() vbnDigit("8") '
              'vbnSetFormField(hiGetCurrentForm()~>number 6) '
              'vbnEscape() vbnEscape() '
              'list(vbnActive hiGetCurrentForm()~>number~>value '
              'hiGetCurrentCmd(vbnCopyVerifyWin)))', '(nil 1 "Copy")')
        check('Array type resets to Step',
              'progn(vbnSetFormField(hiGetCurrentForm()~>copyType "Array") '
              'vbnCountHotkey() list(hiGetCurrentForm()~>copyType~>value '
              'hiGetCurrentForm()~>number~>value))', '("Step" 1)')
        check('zero is rejected', 'progn(vbnDigit("0") vbnConfirm())', 'nil',
              warning='positive integer copy count')
        check('fraction is rejected without closing',
              'progn(vbnDigits="2.5" vbnConfirm())', 'nil',
              warning='positive integer copy count')
        check('invalid entries created no copies',
              'list(vbnActive hiGetCurrentForm()~>number~>value '
              'length(vbnCopyVerifyCv~>shapes))', '(t 1 1)')
        check('N again confirms count only',
              'progn(vbnDigits="4" vbnCountHotkey() '
              'list(vbnActive hiGetCurrentForm()~>number~>value '
              'length(vbnCopyVerifyCv~>shapes)))', '(nil 4 1)')
        check('Space confirmation',
              'progn(vbnCountHotkey() vbnDigit("3") '
              'evalstring(hiGetBindKey("Layout" "<Key>space EF")) '
              'list(vbnActive hiGetCurrentForm()~>number~>value '
              'length(vbnCopyVerifyCv~>shapes)))', '(nil 3 1)')
        check('N to J to N switches reset count',
              'progn(vbnCountHotkey() vbnDigit("9") vbnHotkey(nil) '
              'vbnCountHotkey() list(vbnKind vbnDigits hiGetCurrentForm()~>number~>value))',
              '(copyCount "1" 1)')
        check('J commits pending N digits without placing copies',
              'progn(vbnDigit("9") vbnHotkey(nil) '
              'list(vbnKind hiGetCurrentForm()~>number~>value '
              'length(vbnCopyVerifyCv~>shapes) vbnRememberedNumber))',
              '(distance 9 1 123.5)')
        check('Shift-J commits pending N digits',
              'progn(vbnCountHotkey() vbnDigit("2") vbnHotkey(t) '
              'list(vbnKind hiGetCurrentForm()~>number~>value '
              'length(vbnCopyVerifyCv~>shapes)))', '(position 2 1)')
        check('invalid N does not switch into J',
              'progn(vbnCountHotkey() vbnDigit("0") vbnHotkey(nil))', 'nil',
              warning='positive integer copy count')
        check('invalid switch retains N and native Copy',
              'list(vbnActive vbnKind hiGetCurrentForm()~>number~>value '
              'hiGetCurrentCmd(vbnCopyVerifyWin))', '(t copyCount 1 "Copy")')
        check('disabling cancels N and resets count',
              'progn(vbnSetFormField(hiGetCurrentForm()~>number 5) vbnToggle() '
              'list(vbnActive vbnEnabled hiGetCurrentForm()~>number~>value))', '(nil nil 1)')
        check('disabled N delegates saved EF and normal bindings',
              'progn(vbnCopyVerifyFallbackHits=0 '
              'vbnCopyVerifySavedN=vbnCountOld vbnCopyVerifySavedNormalN=vbnCountNormalOld '
              'vbnCountOld="vbnCopyVerifyFallbackHits=vbnCopyVerifyFallbackHits+1" '
              'vbnCountHotkey() vbnCountOld=nil '
              'vbnCountNormalOld="vbnCopyVerifyFallbackHits=vbnCopyVerifyFallbackHits+10" '
              'vbnCountHotkey() vbnCountOld=vbnCopyVerifySavedN '
              'vbnCountNormalOld=vbnCopyVerifySavedNormalN '
              'list(vbnActive vbnCopyVerifyFallbackHits))', '(nil 11)')
        check('reenable and preserve reference point',
              'progn(vbnToggle() vbnSetFormField(hiGetCurrentForm()~>segSnapMode "orthogonal") '
              'vbnSetFormField(hiGetCurrentForm()~>copyRecursive nil) '
              'addPoint(0:0) vbnCopyVerifyPoints=hiGetCurrentEnterFunPoints() '
              'vbnCountHotkey() vbnDigit("3") vbnConfirm() '
              'list(equal(hiGetCurrentEnterFunPoints() vbnCopyVerifyPoints) '
              'hiGetCurrentCmd(vbnCopyVerifyWin) length(vbnCopyVerifyCv~>shapes)))',
              '(t "Copy" 1)')
        check('J previews all three targets and count hint',
              'progn(vbnHotkey(nil) vbnDigits="12" '
              'vbnCopyVerifyPreviewBoxes=vbnDistancePreviewBoxes(12.0 1:0) '
              'list(vbnCopyCount() vbnDisplayText(nil) vbnCopyVerifyPreviewBoxes))',
              '(3 "12  |  COPY DISTANCE [3 copies]" '
              '(((12.0 0.0) (20.0 3.0)) ((24.0 0.0) (32.0 3.0)) ((36.0 0.0) (44.0 3.0))))')
        check('negative Y preview repeats in requested direction',
              'vbnDistancePreviewBoxes(4.0 0:-1)',
              '(((0.0 -4.0) (8.0 -1.0)) ((0.0 -8.0) (8.0 -5.0)) ((0.0 -12.0) (8.0 -9.0)))')
        check('preview and hint follow native count changes',
              'progn(vbnSetCopyCount(vbnForm 4) '
              'list(vbnModeText() length(vbnDistancePreviewBoxes(12.0 1:0))))',
              '("COPY DISTANCE [4 copies]" 4)')
        check('Single type has one preview even with stale number',
              'progn(vbnSetFormField(vbnForm~>copyType "Single") '
              'list(vbnModeText() length(vbnDistancePreviewBoxes(12.0 1:0))))',
              '("COPY DISTANCE" 1)')
        check('draws four highlight edges for each of three targets',
              'progn(vbnSetCopyCount(vbnForm 3) vbnClearObjects(vbnPreviewObjects) '
              'vbnPreviewObjects=nil '
              'let((savedDirection) savedDirection=getd(quote(vbnDirection)) '
              'unwindProtect(progn(putd(quote(vbnDirection) lambda(() 1:0)) '
              'vbnDrawPreview(12:0 12.0) length(vbnPreviewObjects)) '
              'putd(quote(vbnDirection) savedDirection))))', '12')
        check('J confirms all copies before resetting count on exit',
              'let((savedDirection) savedDirection=getd(quote(vbnDirection)) '
              'unwindProtect(progn(putd(quote(vbnDirection) lambda(() 1:0)) '
              'vbnConfirm()) putd(quote(vbnDirection) savedDirection)))', 't')
        check('native placement uses confirmed count', 'length(vbnCopyVerifyCv~>shapes)', '4')
        check('native copies match all preview targets',
              'list(vbnActive length(setof(fig vbnCopyVerifyCv~>shapes '
              'member(fig~>bBox vbnCopyVerifyPreviewBoxes))) leGetEnv("copyNumber"))',
              '(nil 3 1)')
        check('copies have expected step spacing',
              'list(length(setof(fig vbnCopyVerifyCv~>shapes '
              'member(fig~>bBox list(list(12:0 20:3) list(24:0 32:3) list(36:0 44:3))))) '
              'vbnCopyVerifySource~>bBox)', '(3 ((0.0 0.0) (8.0 3.0)))')
        check('save isolated result', 'progn(dbSave(vbnCopyVerifyCv) t)', 't')
        check('restart isolated Copy after J exit',
              'progn(geDeselectAllFig(vbnCopyVerifyCv) geSelectFig(vbnCopyVerifySource) '
              'hiEnqueueCmd("leHiCopy(vbnCopyVerifyWin)"))', 't')
        check('next native Copy starts at one', 'hiGetCurrentForm()~>number~>value', '1')
    finally:
        check('restore state', 'progn(when(vbnActive vbnStop()) '
              'when(vbnCopyVerifyWin && member(vbnCopyVerifyWin hiGetWindowList()) '
              'hiSetCurrentWindow(vbnCopyVerifyWin) '
              'when(vbnCopyVerifyForm '
              'vbnSetFormField(vbnCopyVerifyForm~>segSnapMode vbnCopyVerifySnapOriginal) '
              'vbnSetFormField(vbnCopyVerifyForm~>copyRecursive vbnCopyVerifyRecursive)) '
              'when(hiGetCurrentCmd(vbnCopyVerifyWin) cancelEnterFun(hiGetCurrentForm()))) '
              'vbnRememberedNumber=vbnCopyVerifyMemory vbnRememberedXY=vbnCopyVerifyXY '
              'vbnEnabled=vbnCopyVerifyEnabled '
              'hiSetActionChecked(vbnAction vbnEnabled nil) '
              'leSetEnv("copyNumber" vbnCopyVerifyNumber) '
              'leSetEnv("copyOrder" vbnCopyVerifyOrder) '
              'when(member(vbnCopyVerifyOriginalWin hiGetWindowList()) '
              'hiSetCurrentWindow(vbnCopyVerifyOriginalWin)) t)', 't')
        check('captured keys restored',
              'equal(vbnCopyVerifyKeys mapcar(lambda((entry) '
              'list(car(entry) hiGetBindKey("Layout" car(entry)))) vbnCopyVerifyKeys))', 't')
    artifact_path('copy-count-verification.json').write_text(
        json.dumps(dict(cell=f'{args.lib}/{cell}/layout', checks=checks,
                        limitation='Bridge calls only; physical N key, cursor label, and canvas clicks need human retest.'),
                   indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
