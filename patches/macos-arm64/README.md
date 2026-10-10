# Native macOS arm64 build patches

These patches describe the source used for
`csky-elfabiv2-tools-macos-arm64-native-ml40-20260930.tar.xz`, with package label
`V3.10-gcc6.3-src54d18fdf0ce7-macos-arm64-ml40-pushpop1`.
The original build repository is [c-sky/toolchain-build](https://github.com/c-sky/toolchain-build),
branch `gcc-6_3-Release_V3_10`.

| Source | Pinned commit |
| --- | --- |
| [toolchain-build](https://github.com/c-sky/toolchain-build) | `54d18fdf0ce7f7f65663863424762c998fc14171` |
| [GCC](https://github.com/c-sky/gcc) | `86994d519c83c7a9e1785774014eeacb6ca17adb` |
| [binutils](https://github.com/c-sky/binutils-gdb) | `2409f5af709d5fef4f41cbeb30ef59bc1046b252` |

| Patch | Apply in | Purpose |
| --- | --- | --- |
| [toolchain-build-macos-arm64.patch](toolchain-build-macos-arm64.patch) | toolchain-build root | Native ARM64 host/version labels and logging; disable incompatible ISL/Graphite; CK803 runtime selection for single-lib builds |
| [gcc-combined.patch](gcc-combined.patch) | `gcc/` | C-SKY required-printf support, Darwin ARM host hooks, and 16 KiB PCH alignment |
| [gcc-pushpop-ub.patch](gcc-pushpop-ub.patch) | `gcc/`, after the combined patch | Bound the 32-register push/pop scan and use unsigned masks |
| [binutils-combined.patch](binutils-combined.patch) | `binutils/` | C-SKY printf/archive selection and archive rescanning, Darwin readline headers, and BFD callback correction |

The three GCC/binutils patch files are exact copies of the saved build patches;
their hashes match the full-multilib build's manifest. The build-script patch
was exported from the preserved isolated build source against the pinned parent
commit. It includes the host/version work committed separately as
`ed75e979c7aa317ee48baad16ae09512dacaf26c`, plus the Mac driver changes.
Apply this exported patch directly to the pinned upstream base, rather than on
top of that separate commit. The CK803-only runtime selection is inactive for
the full multilib build.

All four patch hashes are in [SHA256SUMS](SHA256SUMS). From this directory:

```sh
shasum -a 256 -c SHA256SUMS
```

The push/pop patch retains its original comment for hash traceability. The
measured undefined shift was `1 << 32`; the comment overstates the bit-31 case.

## Apply to a fresh source checkout

Set `PATCH_DIR` to this directory's absolute path. Only GCC and binutils
submodules are needed for this minilibc build with GDB disabled:

```sh
PATCH_DIR=/absolute/path/to/XuanTie-CSKY-Toolchains/patches/macos-arm64
git clone https://github.com/c-sky/toolchain-build.git toolchain-build-macos
cd toolchain-build-macos
git checkout --detach 54d18fdf0ce7f7f65663863424762c998fc14171
git submodule update --init gcc binutils
git apply "$PATCH_DIR/toolchain-build-macos-arm64.patch"
git -C gcc apply "$PATCH_DIR/gcc-combined.patch"
git -C gcc apply "$PATCH_DIR/gcc-pushpop-ub.patch"
git -C binutils apply "$PATCH_DIR/binutils-combined.patch"
```

The bundled `prebuilt-libs/minilibc.tar.gz` SHA-256 recorded for the build is
`3b339a38376cc9a1ac6978c6434f4cca5db652de0dc9ffa5ae4045a17c4a4eca`.
It supplies the target C runtime; this build does not rebuild minilibc from source.

## Recorded full-multilib build command

The original host used macOS 14.8.7 arm64, Xcode 16.2, and Homebrew build
dependencies. GMP, MPFR, and libmpc were supplied from `/opt/homebrew`; Homebrew
Bison and Texinfo preceded the system tools on PATH. With those dependencies
available, set `SRC` to the patched checkout and run from a separate empty build
directory:

```sh
SRC=/absolute/path/to/toolchain-build-macos
env PATH=/opt/homebrew/opt/bison/bin:/opt/homebrew/opt/texinfo/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  TOOLCHAIN_BUILD_LOG="$PWD/build-command.log" \
  /opt/homebrew/bin/python3 "$SRC/build-csky-gcc.py" csky-gcc \
  --src "$SRC" --triple csky-elfabiv2 --host macos-arm64 --jobs 2 \
  --version V3.10-gcc6.3-src54d18fdf0ce7-macos-arm64-ml40-pushpop1 \
  --dep-libs /opt/homebrew --multilib --cpu ck810f --fpu soft \
  --endian little --disable-gdb > "$PWD/build.stdout.log" 2>&1
```

The driver adds `--without-isl` to GCC configuration. The explicit version label
identifies patched sources and does not claim the vendor binary's `V3.10.33`
identity. The saved build passed the 40-row multilib comparison and 120 local
C/C++/floating-point links; those results do not establish byte-identical vendor
compiler libraries, a complete GCC testsuite run, or target execution.
