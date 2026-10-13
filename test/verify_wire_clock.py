"""Check repeated helper IPC and real X-server clocks without mouse events."""

from config import LIB, LAYER, PCELL_LIB, PCELL_CELL, artifact_path

import json
from pathlib import Path
import time

from virtuoso_bridge import VirtuosoClient


def main():
    c = VirtuosoClient.from_env()
    rows = []
    for attempt in range(3):
        start = c.execute_skill('progn(vbnWireRefreshBusy=t vbnWireRefreshStatus="pending" '
            'ipcBeginProcess(sprintf(nil "python3 %s --pid %d --title clock --check-clock" '
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
            raise RuntimeError('Clock helper did not finish')
        if 'clock-check' not in result.output:
            raise RuntimeError(result)
        # The bridge prints the SKILL string with escaped quotes. Decode just
        # that string before parsing its JSON payload; no diagnostic escapes
        # are ever passed to the SKILL parser.
        encoded = result.output[len('(nil '):-1]
        status = json.loads(encoded)
        data = json.loads(status)
        first, second = data['event_times']
        if not first or not second or not 0 < ((second-first) & 0xffffffff) < 1000:
            raise RuntimeError(data)
        rows.append(data)
        print('repeat', attempt+1, data)
    artifact_path('wire-clock-verification.json').write_text(
        json.dumps(dict(checks=rows, limitation='No motion events sent; repeated native Wire repaint needs human retest.'),
                   indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
