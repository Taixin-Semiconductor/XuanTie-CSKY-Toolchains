#!/usr/bin/env python3
"""Build a macOS elfuse vendor archive with the guest GDB runtime."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import stat
import tarfile
import tempfile


BASE_NAME = "csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz"
BASE_SHA256 = "6fde30003fe1f9f2a4de296a04c372c698c1a45f60c442aeacc5e312bdec9ab6"
VENDOR_NAME = "csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz"
VENDOR_SHA256 = "ad5c8564ada7fbf77acb952448b03a394d7aafb56c945b2f8698d598076a69f9"
NCURSES_NAME = "libncurses5_6.4-4_amd64.deb"
NCURSES_SHA256 = "02f4f7f52c4ce2fc4021793a931bfd85f7870554b8e4d56576d73a4ed0bdb390"
TINFO_NAME = "libtinfo5_6.4-4_amd64.deb"
TINFO_SHA256 = "dd347f794e651039e7b4c391f86c674fed7f415b3dca6b0937beb0d470f09c1a"
TOP = "csky-elfabiv2-macos-arm64-elfuse"
PREFIX = "csky-elfabiv2"
PACKAGE_NAME = "csky-elfabiv2-macos-arm64-elfuse-gdb-20261009"
MANIFEST_NAME = "manifest.json"
SUMS_NAME = "SHA256SUMS"


class PackageError(Exception):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_hash(path: Path, expected: str, description: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise PackageError(f"{description} SHA-256 mismatch: {actual}")


def normalized_member(name: str) -> str:
    if not name or "\\" in name or "\x00" in name or "\n" in name or "\r" in name:
        raise PackageError(f"unsafe archive path: {name!r}")
    clean = posixpath.normpath(name.rstrip("/"))
    if clean in ("", ".", "..") or clean.startswith("../") or clean.startswith("/"):
        raise PackageError(f"unsafe archive path: {name!r}")
    return clean


def safe_symlink_target(relative: str, target: str) -> None:
    if not target or "\x00" in target or "\\" in target:
        raise PackageError(f"unsafe symlink target at {relative}: {target!r}")
    if relative.startswith(TOP + "/sysroot/"):
        sysroot_prefix = TOP + "/sysroot/"
        if target.startswith("/"):
            resolved = posixpath.normpath(sysroot_prefix + target.lstrip("/"))
        else:
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(relative), target))
        if resolved != TOP + "/sysroot" and not resolved.startswith(sysroot_prefix):
            raise PackageError(f"guest symlink escapes sysroot: {relative} -> {target}")
        return
    if target.startswith("/"):
        raise PackageError(f"host symlink is absolute: {relative} -> {target}")
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(relative), target))
    if resolved != TOP and not resolved.startswith(TOP + "/"):
        raise PackageError(f"bundle symlink escapes root: {relative} -> {target}")


def ensure_real_parents(root: Path, destination: Path) -> None:
    relative = destination.relative_to(root)
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise PackageError(f"archive path traverses a symlink parent: {current}")
        if current.exists() and not current.is_dir():
            raise PackageError(f"archive parent is not a directory: {current}")
        current.mkdir(exist_ok=True)


def safe_extract_vendor_archive(archive_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=False)
    seen: set[str] = set()
    with tarfile.open(archive_path, "r:xz") as archive:
        members = archive.getmembers()
        if len(members) > 100_000:
            raise PackageError("vendor bundle contains too many entries")
        for member in members:
            relative = normalized_member(member.name)
            if relative in seen:
                raise PackageError(f"duplicate archive entry: {relative}")
            seen.add(relative)
            if relative != TOP and not relative.startswith(TOP + "/"):
                raise PackageError(f"unexpected archive root: {relative}")
            target = destination.joinpath(*PurePosixPath(relative).parts)
            ensure_real_parents(destination, target)
            if member.isdir():
                if target.is_symlink():
                    raise PackageError(f"directory would replace a symlink: {relative}")
                target.mkdir(exist_ok=True)
                os.chmod(target, member.mode & 0o7777)
            elif member.isreg():
                source = archive.extractfile(member)
                if source is None:
                    raise PackageError(f"cannot read archive file: {relative}")
                with source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                os.chmod(target, member.mode & 0o7777)
            elif member.issym():
                safe_symlink_target(relative, member.linkname)
                if target.exists() or target.is_symlink():
                    raise PackageError(f"symlink would replace an existing path: {relative}")
                os.symlink(member.linkname, target)
            else:
                raise PackageError(f"unsupported vendor bundle member: {relative}")
    root = destination / TOP
    if not root.is_dir() or root.is_symlink():
        raise PackageError("vendor archive did not contain its expected root directory")
    return root


def ar_members(data: bytes) -> dict[str, bytes]:
    if not data.startswith(b"!<arch>\n"):
        raise PackageError("input is not a Debian ar package")
    result: dict[str, bytes] = {}
    offset = 8
    while offset < len(data):
        header = data[offset : offset + 60]
        if len(header) != 60 or header[58:60] != b"`\n":
            raise PackageError("malformed Debian ar member header")
        try:
            name = header[:16].decode("ascii").strip().rstrip("/")
            size = int(header[48:58].decode("ascii").strip())
        except (UnicodeDecodeError, ValueError) as exc:
            raise PackageError("malformed Debian ar member metadata") from exc
        offset += 60
        payload = data[offset : offset + size]
        if len(payload) != size or name in result:
            raise PackageError(f"invalid or duplicate Debian ar member: {name}")
        result[name] = payload
        offset += size + (size & 1)
    return result


def package_control(data: bytes, package: str) -> None:
    members = ar_members(data)
    control_name = next((name for name in members if name.startswith("control.tar")), None)
    payload_name = next((name for name in members if name.startswith("data.tar")), None)
    if not control_name or not payload_name:
        raise PackageError(f"{package}: Debian control or data archive is missing")
    with tarfile.open(fileobj=io.BytesIO(members[control_name]), mode="r:*") as archive:
        control_member = next((m for m in archive.getmembers() if m.name.rstrip("/").lstrip("./") == "control"), None)
        if control_member is None:
            raise PackageError(f"{package}: Debian control metadata is missing")
        stream = archive.extractfile(control_member)
        if stream is None:
            raise PackageError(f"{package}: Debian control metadata is unreadable")
        fields: dict[str, str] = {}
        for line in stream.read().decode("utf-8", "strict").splitlines():
            if ": " in line:
                key, value = line.split(": ", 1)
                fields[key] = value
    if fields.get("Package") != package or fields.get("Version") != "6.4-4" or fields.get("Architecture") != "amd64":
        raise PackageError(f"{package}: unexpected Debian package identity {fields}")


def deb_payload(path: Path, package: str, expected_hash: str, wanted_paths: set[str]) -> dict[str, tuple[str, int, bytes | str]]:
    verify_hash(path, expected_hash, path.name)
    data = path.read_bytes()
    members = ar_members(data)
    data_name = next((name for name in members if name.startswith("data.tar")), None)
    if data_name is None:
        raise PackageError(f"{package}: Debian payload is missing")
    package_control(data, package)
    payload: dict[str, tuple[str, int, bytes | str]] = {}
    selected_names: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(members[data_name]), mode="r:*") as archive:
        for member in archive.getmembers():
            name = member.name
            while name.startswith("./"):
                name = name[2:]
            if name.rstrip("/") not in wanted_paths:
                continue
            name = normalized_member(name)
            destination_name = "usr/" + name if name.startswith("lib/") else name
            if name in selected_names:
                raise PackageError(f"{package}: duplicate selected payload: {name}")
            selected_names.add(name)
            if member.isreg():
                stream = archive.extractfile(member)
                if stream is None:
                    raise PackageError(f"{package}: cannot read {name}")
                payload[destination_name] = ("file", member.mode & 0o7777, stream.read())
            elif member.issym():
                target = member.linkname
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), target))
                if target.startswith("/") or not (resolved.startswith("usr/lib/x86_64-linux-gnu/") or resolved.startswith("lib/x86_64-linux-gnu/")):
                    raise PackageError(f"{package}: library symlink escapes package library directory: {name} -> {target}")
                payload[destination_name] = ("symlink", 0o777, target)
            else:
                raise PackageError(f"{package}: selected entry has unsupported type: {name}")
    missing = wanted_paths - selected_names
    if missing:
        raise PackageError(f"{package}: expected runtime entries are missing: {sorted(missing)}")
    return payload


def merge_payload(root: Path, packages: list[dict[str, tuple[str, int, bytes | str]]]) -> list[str]:
    added: list[str] = []
    sysroot = root / "sysroot"
    for package in packages:
        for relative, (kind, mode, value) in sorted(package.items()):
            target = sysroot.joinpath(*PurePosixPath(relative).parts)
            ensure_real_parents(root.parent, target)
            if kind == "file":
                content = value
                assert isinstance(content, bytes)
                if target.exists():
                    if target.is_symlink() or not target.is_file() or target.read_bytes() != content:
                        raise PackageError(f"refusing to replace existing sysroot file: {relative}")
                else:
                    with target.open("xb") as stream:
                        stream.write(content)
                    os.chmod(target, mode)
            else:
                link = value
                assert isinstance(link, str)
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(relative), link))
                if link.startswith("/") or not (resolved.startswith("usr/lib/x86_64-linux-gnu/") or resolved.startswith("lib/x86_64-linux-gnu/")):
                    raise PackageError(f"unsafe package library symlink: {relative} -> {link}")
                if target.exists() or target.is_symlink():
                    if not target.is_symlink() or os.readlink(target) != link:
                        raise PackageError(f"refusing to replace existing sysroot link: {relative}")
                else:
                    os.symlink(link, target)
            added.append("sysroot/" + relative)
    return added


def add_hosts_alias(root: Path) -> None:
    path = root / "sysroot" / "etc" / "hosts"
    text = path.read_text(encoding="utf-8")
    if re.search(r"(?m)^\s*[^#\n]+\s+[^#\n]*\belfuse\b(?:\s|$)", text):
        return
    if text and not text.endswith("\n"):
        text += "\n"
    text += "127.0.0.1 elfuse # SDKTools GDB runtime hostname lookup\n"
    path.write_text(text, encoding="utf-8")


def inventory(root: Path, exclude_metadata: bool) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        base = Path(current)
        dirs.sort()
        files.sort()
        entries = list(dirs) + list(files)
        for name in entries:
            path = base / name
            relative = path.relative_to(root).as_posix()
            if exclude_metadata and relative in (MANIFEST_NAME, SUMS_NAME):
                continue
            info = path.lstat()
            mode = stat.S_IMODE(info.st_mode)
            if stat.S_ISLNK(info.st_mode):
                dirs[:] = [entry for entry in dirs if entry != name]
                target = os.readlink(path)
                records.append({"path": relative, "type": "symlink", "mode": mode, "target": target,
                                "sha256": hashlib.sha256(os.fsencode(target)).hexdigest()})
            elif stat.S_ISDIR(info.st_mode):
                records.append({"path": relative, "type": "directory", "mode": mode})
            elif stat.S_ISREG(info.st_mode):
                records.append({"path": relative, "type": "file", "mode": mode, "sha256": sha256_file(path)})
            else:
                raise PackageError(f"unsupported special file in bundle: {relative}")
    records.sort(key=lambda item: str(item["path"]))
    return records


def write_integrity_metadata(root: Path) -> None:
    records = inventory(root, exclude_metadata=True)
    manifest = {"schema_version": 1, "package": PACKAGE_NAME, "entries": records}
    (root / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sums = [f"{entry['sha256']}  {entry['path']}" for entry in records if entry["type"] == "file"]
    (root / SUMS_NAME).write_text("\n".join(sums) + "\n", encoding="ascii")


def verify_integrity_metadata(root: Path) -> int:
    manifest = json.loads((root / MANIFEST_NAME).read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("package") != PACKAGE_NAME:
        raise PackageError("generated manifest identity mismatch")
    expected = manifest.get("entries")
    actual = inventory(root, exclude_metadata=True)
    if expected != actual:
        raise PackageError("generated manifest does not match bundle contents")
    sums: dict[str, str] = {}
    for line in (root / SUMS_NAME).read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match or match.group(2) in sums:
            raise PackageError(f"invalid checksum row: {line!r}")
        sums[match.group(2)] = match.group(1)
    wanted = {str(entry["path"]): str(entry["sha256"]) for entry in actual if entry["type"] == "file"}
    if sums != wanted:
        raise PackageError("generated SHA256SUMS does not match regular bundle files")
    return len(actual)


def update_bundle_description(root: Path, package_metadata: dict[str, object]) -> None:
    path = root / "BUNDLE.md"
    text = path.read_text(encoding="utf-8")
    omitted = re.compile(
        r"Mac-facing GDB wrappers are omitted because\s+the guest GDB does not start with this sysroot:\s*"
        r"`libncurses\.so\.5` is\s+missing\.\s*The guest vendor binary remains in `sysroot/opt/csky/bin/`\."
    )
    replacement = (
        "This refresh adds a relocatable host-facing GDB wrapper and the pinned Debian Bookworm guest runtime closure. "
        "The existing compiler and linker wrappers retain their original paths and runtime."
    )
    text, count = omitted.subn(replacement, text)
    if count != 1:
        raise PackageError("base BUNDLE.md does not match the expected pinned vendor description")
    note = (
        "\n## Debugger runtime refresh (2026-10-09)\n\n"
        "Prepared as `" + PACKAGE_NAME + "`. The guest GDB remains "
        "`sysroot/opt/csky/bin/csky-elfabiv2-gdb`; `bin/csky-elfabiv2-gdb` routes through "
        "the existing `bin/.elfuse-runner`. Only `libncurses5` and `libtinfo5` runtime "
        "files plus their Debian copyright notice were added from checksum-verified "
        "Bookworm amd64 packages. `sysroot/etc/hosts` maps the guest hostname `elfuse` "
        "to loopback for gethostname resolution. `GDB-RUNTIME.json`, `manifest.json`, "
        "and `SHA256SUMS` record package provenance and the refreshed tree.\n\n"
    )
    if "## Debugger runtime refresh" in text:
        raise PackageError("base BUNDLE.md already contains a debugger refresh section")
    text += note
    path.write_text(text, encoding="utf-8")


def create_archive(root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".sdktools-vendor-archive-", dir=output.parent) as temporary:
        staged = Path(temporary) / output.name
        with tarfile.open(staged, "w:xz", format=tarfile.GNU_FORMAT, preset=9) as archive:
            paths: list[Path] = []
            for current, dirs, files in os.walk(root.parent, topdown=True, followlinks=False):
                base = Path(current)
                dirs.sort()
                files.sort()
                for name in list(dirs):
                    item = base / name
                    paths.append(item)
                    if item.is_symlink():
                        dirs.remove(name)
                paths.extend(base / name for name in files)
            paths.sort(key=lambda item: item.relative_to(root.parent).as_posix())
            for path in paths:
                relative = path.relative_to(root.parent).as_posix()
                info = path.lstat()
                name = relative + ("/" if stat.S_ISDIR(info.st_mode) else "")
                header = tarfile.TarInfo(name)
                header.uid = header.gid = 0
                header.uname = header.gname = ""
                header.mtime = 0
                header.mode = stat.S_IMODE(info.st_mode)
                if stat.S_ISDIR(info.st_mode):
                    header.type = tarfile.DIRTYPE
                    archive.addfile(header)
                elif stat.S_ISLNK(info.st_mode):
                    header.type = tarfile.SYMTYPE
                    header.linkname = os.readlink(path)
                    archive.addfile(header)
                elif stat.S_ISREG(info.st_mode):
                    header.type = tarfile.REGTYPE
                    header.size = info.st_size
                    with path.open("rb") as stream:
                        archive.addfile(header, stream)
                else:
                    raise PackageError(f"unsupported special output path: {relative}")
        try:
            os.link(staged, output)
        except FileExistsError as exc:
            raise PackageError(f"output already exists: {output}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-archive", type=Path, required=True, help="current verified SDKTools macOS vendor archive")
    parser.add_argument("--vendor-archive", type=Path, required=True, help="pinned Taixin x86_64 vendor compiler archive")
    parser.add_argument("--libncurses5-deb", type=Path, required=True, help=f"{NCURSES_NAME}")
    parser.add_argument("--libtinfo5-deb", type=Path, required=True, help=f"{TINFO_NAME}")
    parser.add_argument("--output", type=Path, required=True, help="new local .tar.xz archive; must not already exist")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    verify_hash(args.bundle_archive, BASE_SHA256, "current vendor bundle")
    verify_hash(args.vendor_archive, VENDOR_SHA256, "Taixin vendor archive")
    ncurses = deb_payload(args.libncurses5_deb, "libncurses5", NCURSES_SHA256, {
        "lib/x86_64-linux-gnu/libncurses.so.5", "lib/x86_64-linux-gnu/libncurses.so.5.9",
    })
    tinfo = deb_payload(args.libtinfo5_deb, "libtinfo5", TINFO_SHA256, {
        "lib/x86_64-linux-gnu/libtinfo.so.5", "lib/x86_64-linux-gnu/libtinfo.so.5.9",
        "usr/share/doc/libtinfo5/copyright",
    })

    with tempfile.TemporaryDirectory(prefix="sdktools-elfuse-vendor-refresh-") as temporary:
        stage_parent = Path(temporary)
        root = safe_extract_vendor_archive(args.bundle_archive, stage_parent / "extract")
        expected_gdb = root / "sysroot/opt/csky/bin/csky-elfabiv2-gdb"
        if not expected_gdb.is_file() or expected_gdb.stat().st_mode & 0o111 == 0:
            raise PackageError("pinned vendor bundle does not contain executable guest GDB")
        runner = root / "bin/.elfuse-runner"
        if not runner.is_file() or not os.access(runner, os.X_OK):
            raise PackageError("pinned vendor bundle does not contain executable bin/.elfuse-runner")

        added = merge_payload(root, [ncurses, tinfo])
        wrapper = root / "bin" / f"{PREFIX}-gdb"
        if wrapper.exists() or wrapper.is_symlink():
            raise PackageError("base vendor bundle unexpectedly already contains the GDB wrapper")
        os.symlink(".elfuse-runner", wrapper)
        added.append("bin/" + wrapper.name)
        hosts = root / "sysroot/etc/hosts"
        before_hosts = sha256_file(hosts)
        add_hosts_alias(root)
        after_hosts = sha256_file(hosts)
        guest_gdb_hash = sha256_file(expected_gdb)
        metadata = {
            "schema_version": 1,
            "package": PACKAGE_NAME,
            "source_bundle": {"name": args.bundle_archive.name, "sha256": BASE_SHA256},
            "taixin_vendor_archive": {"name": args.vendor_archive.name, "sha256": VENDOR_SHA256},
            "guest_gdb": {"path": "sysroot/opt/csky/bin/csky-elfabiv2-gdb", "sha256": guest_gdb_hash},
            "wrapper": {"path": "bin/csky-elfabiv2-gdb", "target": ".elfuse-runner"},
            "debian_packages": [
                {"package": "libncurses5", "version": "6.4-4", "architecture": "amd64", "name": args.libncurses5_deb.name, "sha256": NCURSES_SHA256},
                {"package": "libtinfo5", "version": "6.4-4", "architecture": "amd64", "name": args.libtinfo5_deb.name, "sha256": TINFO_SHA256},
            ],
            "hosts_file": {"path": "sysroot/etc/hosts", "sha256_before": before_hosts, "sha256_after": after_hosts, "added_alias": "127.0.0.1 elfuse"},
            "added_entries": sorted(added),
            "preparation_scope": "checksum-verified inputs and fresh-extraction integrity; runtime and hardware validation are documented in README.md",
        }
        (root / "GDB-RUNTIME.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        update_bundle_description(root, metadata)
        write_integrity_metadata(root)
        entries = verify_integrity_metadata(root)

        output = args.output.resolve()
        created_output = False
        try:
            create_archive(root, output)
            created_output = True
            with tempfile.TemporaryDirectory(prefix="sdktools-elfuse-vendor-fresh-") as verify_dir:
                fresh_root = safe_extract_vendor_archive(output, Path(verify_dir) / "extract")
                fresh_entries = verify_integrity_metadata(fresh_root)
                if fresh_entries != entries:
                    raise PackageError("fresh archive extraction has a different manifest entry count")
        except Exception:
            if created_output:
                output.unlink(missing_ok=True)
            raise
        digest = sha256_file(output)
        print(f"archive: {output}")
        print(f"archive_sha256: {digest}")
        print(f"archive_bytes: {output.stat().st_size}")
        print(f"manifest_entries: {entries}")
        print(f"fresh_manifest_entries: {fresh_entries}")
        print(f"guest_gdb_sha256: {guest_gdb_hash}")
        print(f"manifest: {TOP}/manifest.json")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PackageError as exc:
        raise SystemExit(f"package error: {exc}")
