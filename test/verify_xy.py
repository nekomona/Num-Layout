"""Native Cartesian edits in fresh cells; no mouse or keyboard events."""

from config import LIB, LAYER, PCELL_LIB, PCELL_CELL, artifact_path

from datetime import datetime
import json
from pathlib import Path

from virtuoso_bridge import SSHClient, VirtuosoClient
from virtuoso_bridge.virtuoso.layout import layout_create_rect


def main():
    c = VirtuosoClient.from_tunnel(SSHClient.from_env())
    lib = LIB
    cell = 'VB_NUMERIC_XY_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    rows = []

    def check(name, code, expected=None):
        r = c.execute_skill(code)
        rows.append(dict(name=name, output=r.output, errors=r.errors, warnings=r.warnings))
        print(name, r)
        if not r.ok or r.warnings or (expected is not None and r.output != expected):
            raise AssertionError(rows[-1])
        return r.output

    def cursor(code, point):
        return ('let((savedCursor) savedCursor=getd(quote(vbnContourCursorPoint)) '
                'unwindProtect(progn(putd(quote(vbnContourCursorPoint) lambda(() '
                + point + ')) ' + code + ') putd(quote(vbnContourCursorPoint) savedCursor)))')

    def stop():
        check('finish own command', 'progn(when(vbnActive vbnStop()) '
              'when(hiGetCurrentCmd(vbnXYWin) cancelEnterFun(hiGetCurrentForm())) t)', 't')

    def move(text, expected, *, absolute=False, point='100:100', native_absolute=False):
        stop()
        check('start native Move', 'progn(geDeselectAllFig(vbnXYCv) geSelectFig(vbnXYSource) '
              'hiEnqueueCmd("leHiMove(vbnXYWin)"))', 't')
        if native_absolute:
            check('native absolute checkbox initially on',
                  'progn(vbnSetFormField(hiGetCurrentForm()~>moveCoordinates t) t)', 't')
        code = f'vbnHotkey({"t" if absolute else "nil"}) vbnDigits="{text}" vbnConfirm()'
        check(('absolute ' if absolute else 'relative ') + text, cursor(code, point), 't')
        check('Move result ' + text, 'vbnXYSource~>bBox', expected)

    check('idle caller', 'list(vbnActive when(hiGetCurrentWindow() '
          'hiGetCurrentCmd(hiGetCurrentWindow())))', '(nil nil)')
    check('fresh cell', f'ddGetObj("{lib}" "{cell}" "layout")', 'nil')
    check('save state', 'progn(vbnXYOriginalWin=hiGetCurrentWindow() '
          'vbnXYMemory=vbnRememberedNumber vbnXYMemoryPair=vbnRememberedXY '
          'vbnXYEnabledSaved=vbnEnabled vbnEnabled=t vbnRememberedXY=nil '
          'vbnXYWin=nil vbnXYRectForm=nil '
          'vbnXYKeys=mapcar(lambda((k) list(k hiGetBindKey("Layout" k))) '
          'list("<Key>comma" "<Key>comma EF" "<Key>minus" "<Key>minus EF")) t)', 't')
    try:
        with c.layout.create(lib, cell) as lay:
            lay.add(layout_create_rect(LAYER, 'drawing', 0, 0, 8, 3))
        opened = c.open_window(lib, cell, view='layout')
        if not opened.ok:
            raise RuntimeError(opened)
        check('fixture', 'progn(vbnXYWin=hiGetCurrentWindow() vbnXYCv=geGetEditCellView(vbnXYWin) '
              'vbnXYSource=car(vbnXYCv~>shapes) t)', 't')
        check('parser preserves blank components and rejects malformed input',
              'let((vbnKind) vbnKind=quote(distance) '
              'list(vbnParseInput("1.25,-2.5") vbnParseInput(",4") '
              'vbnParseInput("3,") vbnParseInput(",") vbnParseInput("1,.") '
              'vbnParseInput("1,2,3") vbnParseInput("1.2.3")))',
              '((1.25 -2.5) (nil 4.0) (3.0 nil) nil nil nil nil)')
        check('open Move for input checks',
              'progn(geSelectFig(vbnXYSource) hiEnqueueCmd("leHiMove(vbnXYWin)"))', 't')
        check('per-component dot minus comma and backspace',
              'progn(vbnHotkey(nil) vbnDigits="" vbnPrefilled=nil '
              'foreach(char list("1" "." "5" "," "-" "2" "." "5" "." ",") vbnDigit(char)) '
              'vbnBackspace() vbnDigit("5") list(vbnDigits vbnCurrentValue()))',
              '("1.5,-2.5" (1.5 -2.5))')
        check('picked length fills Y without losing X',
              'progn(vbnDigits="5," vbnSelectEdge(list(0:0 0:8)) '
              'list(vbnDigits vbnCurrentValue()))', '("5,8" (5.0 8.0))')
        check('typing replaces picked Y only',
              'progn(vbnDigit("2") list(vbnDigits vbnCurrentValue()))', '("5,2" (5.0 2.0))')
        check('comma promotes picked scalar to X',
              'progn(vbnDigits="" vbnSelectEdge(list(0:0 0:8)) vbnDigit(",") vbnDigit("4") '
              'list(vbnDigits vbnCurrentValue()))', '("8,4" (8.0 4.0))')
        move('10,20', '((10.0 20.0) (18.0 23.0))')
        move(',5', '((10.0 25.0) (18.0 28.0))')
        move('-2,', '((8.0 25.0) (16.0 28.0))')
        move('30,40', '((26.0 38.5) (34.0 41.5))', absolute=True, native_absolute=True)
        move(',50', '((26.0 48.5) (34.0 51.5))', absolute=True)
        move('20,', '((16.0 48.5) (24.0 51.5))', absolute=True)
        move('-10', '((-14.0 48.5) (-6.0 51.5))', absolute=True, point='100:50')
        move('60', '((-14.0 58.5) (-6.0 61.5))', absolute=True, point='-10:100')

        stop()
        check('native Copy', 'progn(geDeselectAllFig(vbnXYCv) geSelectFig(vbnXYSource) '
              'hiEnqueueCmd("leHiCopy(vbnXYWin)"))', 't')
        check('N to Shift-J preserves pending count in absolute mode',
              'progn(vbnCountHotkey() vbnDigit("2") vbnHotkey(t) vbnDigits="30,70" '
              'list(vbnKind vbnCopyCount() vbnMotionDelta(vbnCurrentValue()) '
              'vbnDistancePreviewBoxes(vbnCurrentValue() nil)))',
              '(position 2 (40.0 10.0) (((26.0 68.5) (34.0 71.5)) ((66.0 78.5) (74.0 81.5))))')
        check('J/Shift-J switching keeps XY and copy count',
              'progn(vbnHotkey(nil) vbnHotkey(t) list(vbnDigits vbnCopyCount() vbnKind))',
              '("30,70" 2 position)')
        check('absolute Copy confirmation', 'vbnConfirm()', 't')
        check('all absolute Copy targets match preview',
              'list(length(vbnXYCv~>shapes) '
              'length(setof(f vbnXYCv~>shapes member(f~>bBox '
              'list(list(26:68.5 34:71.5) list(66:78.5 74:81.5))))))', '(3 2)')

        stop()
        check('native Rectangle', 'hiEnqueueCmd("leHiCreateRect(vbnXYWin)")', 't')
        check('save Rectangle defaults', 'progn(vbnXYRectForm=hiGetCurrentForm() '
              'vbnXYRectDefaults=list(vbnXYRectForm~>width~>value vbnXYRectForm~>height~>value '
              'vbnXYRectForm~>leRectSpecifySize~>value vbnXYRectForm~>Justification~>value) t)', 't')
        check('set native Rectangle size before first point',
              'progn(vbnHotkey(nil) vbnDigits="20,10" vbnConfirm() '
              'list(vbnXYRectForm~>width~>value vbnXYRectForm~>height~>value '
              'vbnXYRectForm~>leRectSpecifySize~>value length(vbnXYCv~>shapes)))', '(20.0 10.0 t 3)')
        check('native placement of specified rectangle', 'progn(addPoint(100:100) t)', 't')
        check('placed rectangle has requested size',
              'length(setof(f vbnXYCv~>shapes equal(f~>bBox list(100:100 120:110))))', '1')
        stop()
        check('new two-corner Rectangle', 'hiEnqueueCmd("leHiCreateRect(vbnXYWin)")', 't')
        check('first corner', 'progn(vbnSetFormField(hiGetCurrentForm()~>leRectSpecifySize nil) '
              'addPoint(200:200) t)', 't')
        check('J rectangle preview and finish after first corner',
              cursor('vbnHotkey(nil) vbnDigits="8,5" '
                     'vbnXYRectPreview=vbnRectDrawBox(vbnCurrentValue()) vbnConfirm()', '210:210'), 't')
        check('native rectangle matches J preview',
              'list(vbnXYRectPreview length(setof(f vbnXYCv~>shapes equal(f~>bBox vbnXYRectPreview))))',
              '(((200.0 200.0) (208.0 205.0)) 1)')
        stop()
        check('new Rectangle with blank X', 'hiEnqueueCmd("leHiCreateRect(vbnXYWin)")', 't')
        check('first corner for blank X', 'progn(addPoint(250:250) t)', 't')
        check('blank X retains current provisional width',
              cursor('vbnHotkey(nil) vbnDigits=",12" vbnConfirm()', '260:256'), 't')
        check('find stretch rectangle',
              'progn(vbnXYResize=car(setof(f vbnXYCv~>shapes equal(f~>bBox list(250:250 260:262)))) '
              'vbnXYResize~>bBox)', '((250.0 250.0) (260.0 262.0))')

        for text, corner, expected in [('30,20', '260:262', '((250.0 250.0) (280.0 270.0))'),
                                        (',25', '280:270', '((250.0 250.0) (280.0 275.0))'),
                                        ('40,', '280:275', '((250.0 250.0) (290.0 275.0))')]:
            stop()
            check('start partial native Stretch',
                  'progn(geDeselectAllFig(vbnXYCv) geSelectFigPoint(vbnXYResize list(nil nil t nil)) '
                  'hiEnqueueCmd("leHiStretch(vbnXYWin)"))', 't')
            check('Stretch reference point', f'progn(addPoint({corner}) t)', 't')
            check('Stretch absolute size ' + text,
                  cursor(f'vbnHotkey(nil) vbnDigits="{text}" vbnConfirm()', '310:310'), 't')
            check('Stretch size result ' + text, 'vbnXYResize~>bBox', expected)
        stop()
        check('native Measurement', 'hiEnqueueCmd(hiGetBindKey("Layout" "<Key>k"))', 't')
        check('measurement first point', 'progn(addPoint(500:500) t)', 't')
        check('measurement XY displacement',
              cursor('vbnHotkey(nil) vbnDigits="-5,12" vbnConfirm()', '510:510'), 't')
        check('stored measurement XY endpoints',
              'length(setof(m vbnXYCv~>markers m~>objType == "ruler" && '
              'equal(m~>points list(500:500 495:512))))', '1')
        check('save fresh testbench', 'progn(dbSave(vbnXYCv) t)', 't')
    finally:
        check('restore state', 'progn(when(vbnActive vbnStop()) '
              'when(vbnXYWin && member(vbnXYWin hiGetWindowList()) '
              'hiSetCurrentWindow(vbnXYWin) '
              'when(hiGetCurrentCmd(vbnXYWin) cancelEnterFun(hiGetCurrentForm()))) '
              'when(vbnXYRectForm '
              'vbnXYRectForm~>width~>value=car(vbnXYRectDefaults) '
              'vbnXYRectForm~>height~>value=cadr(vbnXYRectDefaults) '
              'vbnXYRectForm~>leRectSpecifySize~>value=caddr(vbnXYRectDefaults) '
              'vbnXYRectForm~>Justification~>value=cadddr(vbnXYRectDefaults)) '
              'vbnRememberedNumber=vbnXYMemory vbnRememberedXY=vbnXYMemoryPair '
              'vbnEnabled=vbnXYEnabledSaved hiSetActionChecked(vbnAction vbnEnabled nil) '
              'when(vbnXYOriginalWin && member(vbnXYOriginalWin hiGetWindowList()) '
              'hiSetCurrentWindow(vbnXYOriginalWin)) t)', 't')
        check('comma and minus bindings restored',
              'equal(vbnXYKeys mapcar(lambda((p) list(car(p) hiGetBindKey("Layout" car(p)))) vbnXYKeys))', 't')
    artifact_path('xy-verification.json').write_text(
        json.dumps(dict(cell=f'{lib}/{cell}/layout', checks=rows,
                        limitation='No live mouse/key events. Cursor values supplied through protected temporary overrides.'),
                   indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
