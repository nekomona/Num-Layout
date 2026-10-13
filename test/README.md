# Tests for this revision

Use a configured virtual environment with `virtuoso-bridge` installed.
Live checks require a running Virtuoso session and the plugin loaded.
Use only a dedicated test library attached to your technology.
Set `VBN_TEST_LIB` and `VBN_TEST_LAYER` for your installation; generic
defaults are `NUMERIC_ASSIST_TESTS` and `M1`. Optional PCell coverage
uses `VBN_TEST_PCELL_LIB` and `VBN_TEST_PCELL_CELL`. Run scripts one
at a time from the repository root. X11 probes send real input.

Run live helpers as `python test/SCRIPT.py` with any required arguments.
Run offline `test_*.py` checks with
`python -m unittest discover -s test -t . -p "test_*.py"`.

Available scripts:

- `test/create_hierarchy_testbench.py`
- `test/create_testbench.py`
- `test/run_x11_probe.py`
- `test/test_wire_refresh.py`
- `test/verify_feedback.py`
- `test/verify_wire_refresh.py`
- `test/x11_probe.py`

Keep reports and screenshots under Git-ignored `artifacts/`.
Keep local agent instructions under Git-ignored `.local/agent/`.
