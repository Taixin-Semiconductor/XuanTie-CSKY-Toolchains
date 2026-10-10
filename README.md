# XuanTie C-SKY GCC Toolchains

[简体中文](README.zh-CN.md)

Prebuilt XuanTie / C-SKY GCC cross-toolchains. The Linux and Windows
packages come from [XRVM](https://www.xrvm.cn/); the native macOS arm64
package is a source build from the pinned V3.10 GCC/binutils tree in
[c-sky/toolchain-build](https://github.com/c-sky/toolchain-build). A
separate macOS arm64 compatibility package runs the Linux vendor tools
through elfuse.

These packages build bare-metal C-SKY ELF ABI v2 firmware with minilibc.
Choose one host package; extract each into its own directory.

Git keeps the packaging sources, documentation, and [SHA256SUMS](SHA256SUMS). The toolchain
archives are distributed as assets on the pinned GitHub Release `untagged-714ed6e395fc96712ea8`. A
`git clone` does not download the binaries. Download the selected asset from the table and
check its SHA-256 against the matching row in [SHA256SUMS](SHA256SUMS) before extraction.

## Repository Contents

| Archive | Host system | Target | Notes | SHA256 |
| --- | --- | --- | --- | --- |
| [`csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz`](https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/untagged-714ed6e395fc96712ea8/csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz) | Linux x86_64 | `csky-elfabiv2` / `csky-abiv2-elf` | GCC command/version paths use `6.3.0`; includes binutils, GDB, minilibc, multilibs | `AD5C8564ADA7FBF77ACB952448B03A394D7AAFB56C945B2F8698D598076A69F9` |
| [`csky-elfabiv2-tools-mingw-minilibc-20250328.tar.gz`](https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/untagged-714ed6e395fc96712ea8/csky-elfabiv2-tools-mingw-minilibc-20250328.tar.gz) | Windows MinGW | `csky-elfabiv2` / `csky-abiv2-elf` | GCC command/version paths use `6.3.0`; includes binutils, GDB, minilibc, multilibs | `3EB0FA8681F0996136902171855DB974659674ED3D6EBE7DDC6A601DDC0F27F2` |
| [`csky-elfabiv2-tools-macos-arm64-native-ml40-20260930.tar.xz`](https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/untagged-714ed6e395fc96712ea8/csky-elfabiv2-tools-macos-arm64-native-ml40-20260930.tar.xz) | macOS arm64, native | `csky-elfabiv2` / `csky-abiv2-elf` | GCC 6.3.0, binutils 2.27, 40 multilibs; C/C++; no GDB; requires Homebrew GMP/MPFR/libmpc | `c22d4d2566f9a5b49d58c8bb048805a899de596d04a75f7cd615f507717bc973` |
| [`csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz`](https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/untagged-714ed6e395fc96712ea8/csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz) | macOS arm64, elfuse | `csky-elfabiv2` / `csky-abiv2-elf` | Pinned Linux x86_64 vendor GCC 6.3.0 through bundled elfuse and guest sysroot; GDB wrapper omitted | `6fde30003fe1f9f2a4de296a04c372c698c1a45f60c442aeacc5e312bdec9ab6` |
| [`csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz`](https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/untagged-714ed6e395fc96712ea8/csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz) | macOS arm64 elfuse | `csky-elfabiv2` / `csky-abiv2-elf` | Vendor GCC 6.3.0 and GDB 7.12 through elfuse; complete ncurses5/tinfo5 runtime; GDB/MI and bounded hardware debugging verified | `f6b5f7cc0998bf501f40688bd29e34b90cfc703763e89ce3775c7aa7c7aa0c45` |

The vendor archives retain their upstream `20250328` date. The two
`20260930` packages were assembled from the local, dated macOS build
and elfuse evidence.

## Native macOS source and patches

The native macOS arm64 archive was built from upstream
[`c-sky/toolchain-build`](https://github.com/c-sky/toolchain-build), release branch
`gcc-6_3-Release_V3_10`, with these pinned sources:

| Component | Upstream repository | Commit |
| --- | --- | --- |
| Build scripts and bundled minilibc | [c-sky/toolchain-build](https://github.com/c-sky/toolchain-build) | `54d18fdf0ce7f7f65663863424762c998fc14171` |
| GCC 6.3.0 | [c-sky/gcc](https://github.com/c-sky/gcc) | `86994d519c83c7a9e1785774014eeacb6ca17adb` |
| binutils 2.27 | [c-sky/binutils-gdb](https://github.com/c-sky/binutils-gdb) | `2409f5af709d5fef4f41cbeb30ef59bc1046b252` |

This repository includes the three applied GCC/binutils patches, unchanged from
the recorded build, in [patches/macos-arm64](patches/macos-arm64/README.md):
[`gcc-combined.patch`](patches/macos-arm64/gcc-combined.patch),
[`gcc-pushpop-ub.patch`](patches/macos-arm64/gcc-pushpop-ub.patch), and
[`binutils-combined.patch`](patches/macos-arm64/binutils-combined.patch).
It also includes a build-script patch captured from the preserved build source.
The patch notes record their purpose, SHA-256 checksums, application order, and
build command. The native archive retains its `source-info/` build notes and
source patches. These patches describe the native source build; the elfuse
packages run the vendor Linux binaries.

## Supported Target Variants

The vendor toolchain and native macOS package each report the same 40
multilib rows. The elfuse package runs the vendor list. Directories include:

- `ck801`
- `ck802`
- `ck803`
- `ck805`
- `ck807`
- `ck810v`
- `ck860`
- `ck860v`
- `big`
- `soft-fp`
- `hard-fp`

Select the CPU and floating-point ABI options required by your chip, board, SDK, or linker script.

## Install on Linux

```sh
mkdir -p "$HOME/opt/csky-elfabiv2"
tar -xzf csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz -C "$HOME/opt/csky-elfabiv2"
export PATH="$HOME/opt/csky-elfabiv2/bin:$PATH"
```

To make the `PATH` change persistent, add the `export PATH=...` line to your shell profile, such as `~/.bashrc` or `~/.profile`.

Verify the toolchain:

```sh
csky-elfabiv2-gcc --version
csky-elfabiv2-gdb --version
```

## Install on Windows

From PowerShell:

```powershell
mkdir C:\csky-elfabiv2
tar -xzf csky-elfabiv2-tools-mingw-minilibc-20250328.tar.gz -C C:\csky-elfabiv2
$env:Path = "C:\csky-elfabiv2\bin;$env:Path"
```

For a persistent setup, add `C:\csky-elfabiv2\bin` to the Windows user or system `Path` environment variable.

Verify the toolchain:

```powershell
csky-elfabiv2-gcc.exe --version
csky-elfabiv2-gdb.exe --version
```

## Install on Apple Silicon macOS

The native and elfuse packages use different top-level directories. The two
elfuse packages share a top-level directory; extract them into separate destinations. The native
Mach-O tools declare macOS 14.0 as their minimum deployment target; elfuse
declares macOS 14.4. These versions have not been tested on a second Mac.
For the
**native** source build:

```sh
tar -xJf csky-elfabiv2-tools-macos-arm64-native-ml40-20260930.tar.xz
export PATH="$PWD/csky-elfabiv2-macos-arm64-native/bin:$PATH"
csky-elfabiv2-gcc --version
csky-elfabiv2-g++ --version
csky-elfabiv2-gcc -print-multi-lib | wc -l  # 40
```

The native C/C++ frontends load GMP, MPFR, and libmpc from
`/opt/homebrew/opt`. Install those Homebrew libraries before using the
package on another Mac. This build has no `csky-elfabiv2-gdb`; it was
configured with `--disable-gdb` and `--without-isl`.

For the **vendor compiler through elfuse**, use a separate shell or replace
the `PATH` entry above:

```sh
tar -xJf csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz
export PATH="$PWD/csky-elfabiv2-macos-arm64-elfuse/bin:$PATH"
csky-elfabiv2-gcc --version
csky-elfabiv2-g++ --version
```

This second archive contains the Linux vendor toolchain, its guest sysroot,
and the signed macOS arm64 elfuse executable. Its wrappers resolve paths
relative to the extracted directory. The guest GDB binary is present but
its Mac-facing wrapper is omitted: it fails to start because the current
guest sysroot lacks `libncurses.so.5`. SDKTools is not included. elfuse
warns when the extracted sysroot is on a case-insensitive volume; the
CK803 smoke checks passed there, but guest files with case-colliding names
need a case-sensitive volume.

The native archive was relocated and passed CK803 C/C++ compile/link checks
after packaging. The elfuse archive passed the same relocated smoke checks;
the earlier workspace path also completed a TXW8301 SDKTools build and
package with 197 Ninja steps. The native package passed 120 C/C++/float
compile/link checks across its 40 multilib rows. These original compiler-package checks are host-side. Bounded hardware
debugger evidence for the 20261009 refresh is described below; full application
execution is not established. The native source-built `libgcc.a` and `libstdc++.a` are not
byte-identical to the vendor archives.

### macOS vendor GDB refresh (2026-10-09)

The new `csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz`
adds the Mac-facing `csky-elfabiv2-gdb` launcher to the existing vendor/elfuse
component. The guest runtime includes checksum-pinned Debian Bookworm amd64
`libncurses5` and `libtinfo5` 6.4-4, plus the guest `elfuse` hostname alias.
The package includes a relocatable GDB launcher and the complete guest
runtime required by the tested vendor GDB 7.12.

Compare the printed SHA-256 with the table above, then extract into a separate destination:

```sh
shasum -a 256 csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz
mkdir -p /path/to/new-csky-gdb
# Use an empty destination; the older elfuse archive has the same top-level directory.
tar -xJf csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz -C /path/to/new-csky-gdb
export PATH="/path/to/new-csky-gdb/csky-elfabiv2-macos-arm64-elfuse/bin:$PATH"
printf '1-gdb-version\n2-gdb-exit\n' | csky-elfabiv2-gdb -nx -nh --interpreter=mi2
```

Fresh extraction passed manifest/checksum checks, GDB 7.12 MI2 startup, and
local C-SKY ELF symbol loading. With the separately prepared XuanTie
DebugServer r2 bundle, SDKTools CLI/MCP attach and register/stack/global/memory
reads passed on the tested CK-Link Lite V2 app 2.32 and CK803SG board. One
instruction step from the previously RAM-loaded `main` at `0x20005B40` hit a
hardware breakpoint at `main+2`, `0x20005B42`; the breakpoint was removed and
all test processes/ports were released. No flash, RAM-load, PC-assignment or
explicit-reset command was issued. Full application execution, another Mac,
and general probe compatibility remain unproven. SDKTools and DebugServer are
separate packages; neither is bundled in this archive.

Rebuild from the pinned inputs with the standalone helper. Download the existing elfuse
bundle and Linux x86_64 vendor archive first, keeping their original filenames; the helper
verifies their pinned hashes:

```sh
curl -fL --retry 3 \
  -o csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz \
  https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/untagged-714ed6e395fc96712ea8/csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz
curl -fL --retry 3 \
  -o csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz \
  https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/untagged-714ed6e395fc96712ea8/csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz
shasum -a 256 csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz

python3 scripts/refresh-elfuse-vendor.py \
  --bundle-archive csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz \
  --vendor-archive csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz \
  --libncurses5-deb /path/to/libncurses5_6.4-4_amd64.deb \
  --libtinfo5-deb /path/to/libtinfo5_6.4-4_amd64.deb \
  --output /path/to/new/csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz
python3 scripts/test_refresh_vendor.py
```

The helper verifies all four input hashes, preserves the trusted elfuse
runtime, regenerates provenance and integrity manifests, and checks a fresh
extraction. It refuses existing outputs. The Debian input SHA-256 values are
`02f4f7f52c4ce2fc4021793a931bfd85f7870554b8e4d56576d73a4ed0bdb390`
(`libncurses5`) and
`dd347f794e651039e7b4c391f86c674fed7f415b3dca6b0937beb0d470f09c1a`
(`libtinfo5`). Package copyright notices are retained in the guest sysroot.

## Basic Usage

The primary command prefix is:

```sh
csky-elfabiv2-
```

Common tools:

```sh
csky-elfabiv2-gcc
csky-elfabiv2-g++
csky-elfabiv2-as
csky-elfabiv2-ld
csky-elfabiv2-objcopy
csky-elfabiv2-objdump
csky-elfabiv2-size
csky-elfabiv2-gdb  # Linux/Windows vendor packages and the 20261009 macOS GDB refresh
```

The archives also include `csky-abiv2-elf-*` command names. Use the prefix expected by your build system or SDK.

Example compile command:

```sh
csky-elfabiv2-gcc -mcpu=ck803 -Os -g -o app.elf main.c
```

Real firmware projects usually also need a board-specific startup file, linker script, CPU option, ABI option, and library selection.

## Notes

- These are binary toolchains, not complete source packages. The native
  archive includes the macOS patch copies and build instructions under
  `source-info/`; the elfuse archive includes its Apache-2.0 license.
- Keep the host packages in separate directories.
- Some bundled text strings may refer to component versions that differ from the GCC command name. Run `--version` after extraction if you need exact component provenance.
- No standalone license file was found in the original vendor archives.
  Check the upstream XRVM package page and the licenses of GCC, binutils,
  GDB, minilibc, and other bundled components before redistributing.
- The macOS toolchain is experimental, do not assume it will produce binary that is equivalent to the vendor toolchain. 
