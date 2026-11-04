"""Deploy Numeric Assist and its icons together, then load the installed script."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import shlex

from virtuoso_bridge import SSHClient, VirtuosoClient

ROOT = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote-dir", help="Override the persistent installation directory")
    args = parser.parse_args()
    ssh = SSHClient.from_env()

    def shell(command):
        result = ssh.run_command(command)
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        return result.stdout

    remote_home = shell('printf "%s" "$HOME"').strip()
    destination = args.remote_dir or f"{remote_home}/.virtuoso-bridge/numeric-assist"
    if not destination.startswith("/"):
        raise ValueError("--remote-dir must be an absolute remote path")
    destination = destination.rstrip("/")
    shell(f"mkdir -p {shlex.quote(destination + '/icons')}")
    target = destination + "/numeric_assist.il"
    backup = target + ".bak." + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    shell(f"if test -f {shlex.quote(target)}; then cp -p {shlex.quote(target)} {shlex.quote(backup)}; fi")

    # Install icons first so an updated script always finds the assets it uses.
    files = ["icons/numeric_assist.png", "icons/remove_steiners.png",
             "numeric_assist.drf", "wire_refresh.py", "numeric_assist.il"]
    for relative in files:
        source = ROOT / relative
        final = destination + "/" + relative
        staged = final + ".new"
        uploaded = ssh.upload_file(source, staged)
        if uploaded.returncode:
            raise RuntimeError(uploaded.stderr)
        expected = sha256(source.read_bytes()).hexdigest()
        actual = shell(f"sha256sum -- {shlex.quote(staged)}").split()[0]
        if actual != expected:
            raise RuntimeError(f"Checksum mismatch for {relative}")
        shell(f"mv -- {shlex.quote(staged)} {shlex.quote(final)}")
        print(f"Installed {final}")

    escaped = target.replace("\\", "\\\\").replace('"', '\\"')
    result = VirtuosoClient.from_tunnel(ssh).execute_skill(f'load("{escaped}")')
    if not result.ok:
        raise RuntimeError(str(result.errors))
    print(f"Loaded Numeric Assist: {result.output}")
    if result.warnings:
        print(f"Warnings: {result.warnings}")


if __name__ == "__main__":
    main()
