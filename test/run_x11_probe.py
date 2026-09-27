"""Send XTest actions to the isolated layout testbench through the bridge SSH role."""

from pathlib import Path
import shlex
import sys

from virtuoso_bridge import SSHClient


SCRIPT = Path(__file__).with_name("x11_probe.py")
REMOTE = "/tmp/vbn_numeric_x11_probe.py"


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: run_x11_probe.py WINDOW_ID ACTION...")
    ssh = SSHClient.from_env()
    uploaded = ssh.upload_file(SCRIPT, REMOTE)
    if uploaded.returncode != 0:
        raise RuntimeError(uploaded.stderr)
    command = shlex.join(["python3", REMOTE, *sys.argv[1:]])
    result = ssh.run_command(command)
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


if __name__ == "__main__":
    main()
