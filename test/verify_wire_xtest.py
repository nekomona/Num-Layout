"""Check installed helper/XTest and IPC completion without sending live input."""

from config import artifact_path

import json
import time

from virtuoso_bridge import VirtuosoClient


def main():
    c = VirtuosoClient.from_env()
    rows = []
    idle = c.execute_skill('list(vbnWireRefreshBusy vbnActive)')
    if not idle.ok or idle.warnings or idle.output != '(nil nil)':
        raise RuntimeError(f'Run only while NLayout and its helper are idle: {idle}')
    for attempt in range(3):
        start = c.execute_skill('progn(vbnWireRefreshBusy=t vbnWireRefreshStatus="pending" '
            'ipcBeginProcess(sprintf(nil "python3 %s --pid %d --title check --check-xtest" '
            'vbnShellQuote(simplifyFilename(strcat(vbnIconDirectory "../wire_refresh.py"))) '
            'ipcGetPid()) "" quote(vbnWireRefreshData) quote(vbnWireRefreshError) '
            'quote(vbnWireRefreshDone)) t)')
        if not start.ok or start.warnings:
            raise RuntimeError(start)
        for _ in range(20):
            result = c.execute_skill('list(vbnWireRefreshBusy vbnWireRefreshStatus)')
            if not result.ok or result.warnings:
                raise RuntimeError(result)
            if result.output.startswith('(nil '):
                break
            time.sleep(0.1)
        else:
            raise RuntimeError('XTest capability helper did not finish')
        encoded = result.output[len('(nil '):-1]
        data = json.loads(json.loads(encoded))
        if data['status'] != 'xtest-check' or data['motion_sent']:
            raise RuntimeError(data)
        rows.append(data)
        print('repeat', attempt+1, data)
    artifact_path('wire-xtest-verification.json').write_text(
        json.dumps(dict(checks=rows, limitation='XTest extension query only. No live motion sent; visible Wire repaint needs human retest.'),
                   indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
