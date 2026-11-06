# Contributing to Num-Layout

Thanks for helping make Num-Layout better. Bug reports, focused fixes,
tests, documentation, and new examples are all welcome.

## Start a discussion first

Open an issue before starting a large behavior change, a new command integration,
or a change to the deployment layout. Small fixes and documentation corrections
can go straight to a pull request.

Please do not include production cell names, private library or PDK paths,
hostnames, usernames, screenshots of private layouts, or credentials in issues,
commits, tests, or documentation. Use synthetic geometry in a disposable test
library.

## Project layout

| Path | Purpose |
| --- | --- |
| `nlayout/` | Runtime files deployed to Virtuoso; keep their relative paths intact |
| `docs/` | Public README, user guides, publishing notes, and demo media |
| `test/` | Offline tests, live-verification scripts, and manual checks |
| `tools/` | Documentation and icon generators |
| `.local/` | Ignored local agent instructions and private working notes |
| `artifacts/` | Ignored screenshots, reports, captures, and build output |

## Development setup

The native plugin has no Python runtime dependency. For documentation and
offline checks, use Python 3.12 with a virtual environment:

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r test/demo-requirements.txt
uv pip install --python .venv/bin/python -r test/pages-requirements.txt
```

On Windows, replace `.venv/bin/python` with `.venv/Scripts/python.exe`. Live
checks additionally need `virtuoso-bridge`, a configured Virtuoso session, and
a dedicated writable test library. Follow [test/README.md](test/README.md)
before running those checks.

## Making a change

- Keep changes focused and preserve existing user key bindings unless the issue
  explicitly calls for a behavior change.
- Follow the native command lifecycle: preview first, then apply only after the
  user confirms. Restore temporary bindings and form state on cancellation.
- Add or update offline tests when changing the Wire refresh helper or other
  logic that can be tested without Virtuoso.
- Verify native SKILL behavior manually with synthetic geometry. Do not modify
  an existing user layout or use a production library.
- Update both English and Chinese README/user-guide material when changing
  setup steps, key behavior, screenshots, or public links. Keep matching
  headings so the language links remain easy to verify.
- Regenerate tracked documentation output whenever its source changes.

## Validation

Run the checks relevant to your change from the repository root:

```sh
python -m unittest discover -s test -t . -p "test_*.py" -v
python tools/build_guide.py
python tools/build_pages.py
python test/check_pages.py
```

For demo or interface changes, also run:

```sh
python test/check_demo.py
python test/check_demo_media.py
```

Use `--channel msedge` for the browser checks when Microsoft Edge is preferred.
Generated pages and GIFs are committed only after visual review. Keep raw
captures, reports, and screenshots under `artifacts/`.

## Pull requests

Describe the user-visible problem and the resulting behavior, list the commands
you ran, and call out anything that still needs a live Virtuoso check. Keep
unrelated cleanup out of the pull request. By contributing, you agree that your
changes are provided under the repository's [MIT license](LICENSE).
