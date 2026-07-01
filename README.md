# XuanTie C-SKY GCC Toolchains

[简体中文](README.zh-CN.md)

Prebuilt XuanTie / C-SKY GCC cross-toolchains from [XRVM](https://www.xrvm.cn/).

This repository stores binary release archives for building bare-metal C-SKY ELF ABI v2 firmware with the bundled minilibc runtime. It includes host packages for Linux x86_64 and Windows MinGW.

## Repository Contents

| Archive | Host system | Target | Notes | SHA256 |
| --- | --- | --- | --- | --- |
| `csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz` | Linux x86_64 | `csky-elfabiv2` / `csky-abiv2-elf` | GCC command/version paths use `6.3.0`; includes binutils, GDB, minilibc, multilibs | `AD5C8564ADA7FBF77ACB952448B03A394D7AAFB56C945B2F8698D598076A69F9` |
| `csky-elfabiv2-tools-mingw-minilibc-20250328.tar.gz` | Windows MinGW | `csky-elfabiv2` / `csky-abiv2-elf` | GCC command/version paths use `6.3.0`; includes binutils, GDB, minilibc, multilibs | `3EB0FA8681F0996136902171855DB974659674ED3D6EBE7DDC6A601DDC0F27F2` |

The archive date is `20250328`, taken from the upstream package filenames.

## Supported Target Variants

The packaged multilib directories include:

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
csky-elfabiv2-gdb
```

The archives also include `csky-abiv2-elf-*` command names. Use the prefix expected by your build system or SDK.

Example compile command:

```sh
csky-elfabiv2-gcc -mcpu=ck803 -Os -g -o app.elf main.c
```

Real firmware projects usually also need a board-specific startup file, linker script, CPU option, ABI option, and library selection.

## Notes

- These are prebuilt binary toolchains, not source packages.
- Do not extract the Linux and Windows archives into the same directory unless you intentionally want to mix host files.
- Some bundled text strings may refer to component versions that differ from the GCC command name. Run `--version` after extraction if you need exact component provenance.
- No standalone license file was found in these package archives. Check the upstream XRVM package page and the licenses of GCC, binutils, GDB, minilibc, and other bundled components before redistributing.
- The archive files are below GitHub's normal 100 MB per-file limit at the time this README was written. Future larger releases may need Git LFS or GitHub Releases.
