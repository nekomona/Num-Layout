"""Build the deterministic Num-Layout runtime archive and SHA1 checksum."""

import argparse
import gzip
from hashlib import sha1
from pathlib import Path
import re
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "nlayout"


def release_slug(tag: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", tag).strip(".-")
    return slug or "tag"


def package(source: Path, tag: str, output_dir: Path) -> tuple[Path, Path]:
    source = source.resolve()
    output_dir = output_dir.resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"Runtime directory not found: {source}")
    if any(path.is_symlink() for path in source.rglob("*")):
        raise RuntimeError("Release runtime must not contain symbolic links")

    output_dir.mkdir(parents=True, exist_ok=True)
    slug = release_slug(tag)
    archive = output_dir / f"nlayout-{slug}.tar.gz"
    checksum = output_dir / f"{archive.name}.sha1"

    entries = [source]
    entries.extend(
        path
        for path in sorted(source.rglob("*"), key=lambda item: item.relative_to(source).as_posix())
        if "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as bundle:
                for path in entries:
                    relative = path.relative_to(source).as_posix()
                    name = "nlayout" if relative == "." else f"nlayout/{relative}"
                    info = tarfile.TarInfo(name.rstrip("/") + ("/" if path.is_dir() else ""))
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    if path.is_dir():
                        info.type = tarfile.DIRTYPE
                        info.mode = 0o755
                        bundle.addfile(info)
                    else:
                        info.type = tarfile.REGTYPE
                        info.mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
                        info.size = path.stat().st_size
                        with path.open("rb") as handle:
                            bundle.addfile(info, handle)

    digest = sha1(archive.read_bytes()).hexdigest()
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    environment = output_dir / "release.env"
    environment.write_text(
        "\n".join(
            (
                f"ARCHIVE_FILE={archive.name}",
                f"CHECKSUM_FILE={checksum.name}",
                f"ARCHIVE_PATH={archive.relative_to(ROOT).as_posix() if archive.is_relative_to(ROOT) else archive}",
                f"CHECKSUM_PATH={checksum.relative_to(ROOT).as_posix() if checksum.is_relative_to(ROOT) else checksum}",
            )
        )
        + "\n",
        encoding="ascii",
    )
    return archive, checksum


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Release tag used in the archive name")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Runtime directory to package")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts" / "release")
    args = parser.parse_args()
    archive, checksum = package(args.source, args.tag, args.output_dir)
    print(archive)
    print(checksum)


if __name__ == "__main__":
    main()
