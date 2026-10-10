# 玄铁 C-SKY GCC 工具链

[English](README.md)

本仓库保存玄铁 / C-SKY GCC 交叉编译工具链二进制包。Linux 和 Windows
包来自 [XRVM](https://www.xrvm.cn/)；原生 macOS arm64 包从固定的 V3.10
GCC/binutils 源码构建，上游为
[c-sky/toolchain-build](https://github.com/c-sky/toolchain-build)。另有 macOS arm64 兼容包，通过 elfuse 运行 Linux
厂商工具链。

这些包用于构建带 minilibc 的 C-SKY ELF ABI v2 裸机固件。请按主机平台
选择一个包，并分别解压到独立目录。

Git 仓库保存打包源码、文档和 [SHA256SUMS](SHA256SUMS)；工具链压缩包作为固定发布版本
`toolchains-20261009` 的资源分发。`git clone` 不会下载这些二进制文件。请从上表下载所需资源，
解压前按 [SHA256SUMS](SHA256SUMS) 中对应条目校验 SHA-256。

## 仓库内容

| 压缩包 | 主机系统 | 目标平台 | 说明 | SHA256 |
| --- | --- | --- | --- | --- |
| [`csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz`](https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/toolchains-20261009/csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz) | Linux x86_64 | `csky-elfabiv2` / `csky-abiv2-elf` | GCC 命令名和版本目录使用 `6.3.0`；包含 binutils、GDB、minilibc、多库支持 | `AD5C8564ADA7FBF77ACB952448B03A394D7AAFB56C945B2F8698D598076A69F9` |
| [`csky-elfabiv2-tools-mingw-minilibc-20250328.tar.gz`](https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/toolchains-20261009/csky-elfabiv2-tools-mingw-minilibc-20250328.tar.gz) | Windows MinGW | `csky-elfabiv2` / `csky-abiv2-elf` | GCC 命令名和版本目录使用 `6.3.0`；包含 binutils、GDB、minilibc、多库支持 | `3EB0FA8681F0996136902171855DB974659674ED3D6EBE7DDC6A601DDC0F27F2` |
| [`csky-elfabiv2-tools-macos-arm64-native-ml40-20260930.tar.xz`](https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/toolchains-20261009/csky-elfabiv2-tools-macos-arm64-native-ml40-20260930.tar.xz) | macOS arm64 原生 | `csky-elfabiv2` / `csky-abiv2-elf` | GCC 6.3.0、binutils 2.27、40 种 multilib；C/C++；无 GDB；依赖 Homebrew GMP/MPFR/libmpc | `c22d4d2566f9a5b49d58c8bb048805a899de596d04a75f7cd615f507717bc973` |
| [`csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz`](https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/toolchains-20261009/csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz) | macOS arm64 elfuse | `csky-elfabiv2` / `csky-abiv2-elf` | 通过随包 elfuse 和客户机 sysroot 运行固定版本的 Linux x86_64 厂商 GCC 6.3.0；未提供 GDB 包装命令 | `6fde30003fe1f9f2a4de296a04c372c698c1a45f60c442aeacc5e312bdec9ab6` |
| [`csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz`](https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/toolchains-20261009/csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz) | macOS arm64 elfuse | `csky-elfabiv2` / `csky-abiv2-elf` | 通过 elfuse 运行厂商 GCC 6.3.0 与 GDB 7.12；完整 ncurses5/tinfo5 运行库；GDB/MI 与有限硬件调试验证通过 | `f6b5f7cc0998bf501f40688bd29e34b90cfc703763e89ce3775c7aa7c7aa0c45` |

厂商包保留上游文件名中的 `20250328`。两个 `20260930` 包来自本地
有日期记录的 macOS 构建与 elfuse 验证。

## 原生 macOS 源码与补丁

原生 macOS arm64 压缩包基于上游
[`c-sky/toolchain-build`](https://github.com/c-sky/toolchain-build) 的
`gcc-6_3-Release_V3_10` 分支构建，使用以下固定源码版本：

| 组件 | 上游仓库 | 提交 |
| --- | --- | --- |
| 构建脚本及随附 minilibc | [c-sky/toolchain-build](https://github.com/c-sky/toolchain-build) | `54d18fdf0ce7f7f65663863424762c998fc14171` |
| GCC 6.3.0 | [c-sky/gcc](https://github.com/c-sky/gcc) | `86994d519c83c7a9e1785774014eeacb6ca17adb` |
| binutils 2.27 | [c-sky/binutils-gdb](https://github.com/c-sky/binutils-gdb) | `2409f5af709d5fef4f41cbeb30ef59bc1046b252` |

本仓库在 [patches/macos-arm64](patches/macos-arm64/README.md) 中保存实际应用于
GCC/binutils 的三个补丁，内容与构建记录一致：
[`gcc-combined.patch`](patches/macos-arm64/gcc-combined.patch)、
[`gcc-pushpop-ub.patch`](patches/macos-arm64/gcc-pushpop-ub.patch) 和
[`binutils-combined.patch`](patches/macos-arm64/binutils-combined.patch)。
另提供从保留的构建源码导出的构建脚本补丁。补丁说明记录了用途、SHA-256、
应用顺序与构建命令；原生压缩包的 `source-info/` 也保留构建说明与源码补丁。
这些补丁用于原生源码构建；elfuse 包运行厂商 Linux 二进制工具链。

## 支持的目标变体

厂商工具链与原生 macOS 包的 40 条 multilib 列表相同；elfuse 包运行
厂商工具链。目录包括：

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

请根据芯片、开发板、SDK 或链接脚本选择对应的 CPU 和浮点 ABI 参数。

## Linux 安装

```sh
mkdir -p "$HOME/opt/csky-elfabiv2"
tar -xzf csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz -C "$HOME/opt/csky-elfabiv2"
export PATH="$HOME/opt/csky-elfabiv2/bin:$PATH"
```

如果需要永久生效，可以把 `export PATH=...` 这一行加入 `~/.bashrc` 或 `~/.profile`。

验证工具链：

```sh
csky-elfabiv2-gcc --version
csky-elfabiv2-gdb --version
```

## Windows 安装

在 PowerShell 中执行：

```powershell
mkdir C:\csky-elfabiv2
tar -xzf csky-elfabiv2-tools-mingw-minilibc-20250328.tar.gz -C C:\csky-elfabiv2
$env:Path = "C:\csky-elfabiv2\bin;$env:Path"
```

如果需要永久生效，请将 `C:\csky-elfabiv2\bin` 加入 Windows 用户或系统 `Path` 环境变量。

验证工具链：

```powershell
csky-elfabiv2-gcc.exe --version
csky-elfabiv2-gdb.exe --version
```

## Apple Silicon macOS 安装

原生包与 elfuse 包使用不同的顶层目录；两个 elfuse 包共享顶层目录，
请解压到独立的目标目录。原生 Mach-O 工具声明的
最低部署目标为 macOS 14.0，elfuse 声明 macOS 14.4；尚未在第二台
Mac 上验证这些最低版本。使用**原生**源码构建包：

```sh
tar -xJf csky-elfabiv2-tools-macos-arm64-native-ml40-20260930.tar.xz
export PATH="$PWD/csky-elfabiv2-macos-arm64-native/bin:$PATH"
csky-elfabiv2-gcc --version
csky-elfabiv2-g++ --version
csky-elfabiv2-gcc -print-multi-lib | wc -l  # 40
```

原生 C/C++ 前端从 `/opt/homebrew/opt` 加载 GMP、MPFR 和 libmpc。
在另一台 Mac 上使用前，需要安装这些 Homebrew 库。本次构建使用
`--disable-gdb` 和 `--without-isl`，因此没有 `csky-elfabiv2-gdb`。

若要通过 elfuse 使用**厂商编译器**，请在另一个 shell 中执行，
或替换上面的 `PATH` 项：

```sh
tar -xJf csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz
export PATH="$PWD/csky-elfabiv2-macos-arm64-elfuse/bin:$PATH"
csky-elfabiv2-gcc --version
csky-elfabiv2-g++ --version
```

此包包含 Linux 厂商工具链、客户机 sysroot 和已签名的 macOS arm64 elfuse。
包装脚本相对于解压目录定位文件。客户机 GDB 二进制仍在包内，但未提供
Mac 侧包装命令：当前客户机 sysroot 缺少 `libncurses.so.5`，GDB 无法启动。
SDKTools 不在此包中。在不区分大小写的卷上运行时，elfuse 会警告；
CK803 小型编译/链接检查仍然通过，但客户机文件名大小写冲突时需要
区分大小写的卷。

原生包在搬移后通过了 CK803 C/C++ 编译/链接检查；elfuse 包也通过了
相同检查。此前工作目录中的 elfuse 路径还完成了 TXW8301 SDKTools
构建与打包，共 197 个 Ninja 步骤。原生包的 40 种 multilib 共通过
120 个 C/C++/浮点编译与链接检查。上述原始编译器包验证均为主机侧结果。
20261009 更新包的有限硬件调试验证见下文，尚未证明完整应用执行；原生源码构建的 `libgcc.a` 和 `libstdc++.a` 也与
厂商包不逐字节一致。

### macOS 厂商 GDB 更新包（2026-10-09）

新增的 `csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz`
为现有厂商工具链/elfuse 组件提供 Mac 侧 `csky-elfabiv2-gdb` 包装命令。
客户机包含经 SHA-256 校验的 Debian Bookworm amd64 `libncurses5` 和
`libtinfo5` 6.4-4，并加入客户机 `elfuse` 主机名映射。包中包含可搬移的 GDB
包装命令，以及经过验证的厂商 GDB 7.12 所需的完整客户机运行库。

将计算得到的 SHA-256 与上表比对后，解压到独立目录：

```sh
shasum -a 256 csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz
mkdir -p /path/to/new-csky-gdb
# 使用空目录；旧 elfuse 包与此包具有相同顶层目录。
tar -xJf csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz -C /path/to/new-csky-gdb
export PATH="/path/to/new-csky-gdb/csky-elfabiv2-macos-arm64-elfuse/bin:$PATH"
printf '1-gdb-version\n2-gdb-exit\n' | csky-elfabiv2-gdb -nx -nh --interpreter=mi2
```

全新解压通过了清单/摘要校验、GDB 7.12 MI2 启动和本地 C-SKY ELF 符号
加载。配合单独准备的 XuanTie DebugServer r2 包，SDKTools CLI/MCP 在
已测试的 CK-Link Lite V2 app 2.32 与 CK803SG 开发板上完成连接，以及
寄存器、调用栈、全局字段和内存读取。在此前 RAM 加载的 `main`
（`0x20005B40`）执行一条指令，命中 `main+2`（`0x20005B42`）的硬件断点；
随后删除断点，释放测试进程和端口。未执行烧写、RAM 加载、PC 赋值或
显式复位命令。完整应用运行、第二台 Mac 和其他探针兼容性仍未验证。
SDKTools 与 DebugServer 是单独的包，不包含在本工具链包中。

使用独立脚本从固定输入重建。先下载旧 elfuse 包和 Linux x86_64 厂商包，保留原文件名；
脚本会校验其固定摘要：

```sh
curl -fL --retry 3 \
  -o csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz \
  https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/toolchains-20261009/csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz
curl -fL --retry 3 \
  -o csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz \
  https://github.com/Taixin-Semiconductor/XuanTie-CSKY-Toolchains/releases/download/toolchains-20261009/csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz
shasum -a 256 csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz

python3 scripts/refresh-elfuse-vendor.py \
  --bundle-archive csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz \
  --vendor-archive csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz \
  --libncurses5-deb /path/to/libncurses5_6.4-4_amd64.deb \
  --libtinfo5-deb /path/to/libtinfo5_6.4-4_amd64.deb \
  --output /path/to/new/csky-elfabiv2-tools-macos-arm64-elfuse-gdb-20261009.tar.xz
python3 scripts/test_refresh_vendor.py
```

脚本校验四个输入的摘要，保留已验证的 elfuse 运行时，重新生成来源及
完整性清单，并校验全新解压结果；已有输出文件会被拒绝覆盖。Debian 输入
SHA-256 分别为
`02f4f7f52c4ce2fc4021793a931bfd85f7870554b8e4d56576d73a4ed0bdb390`
（`libncurses5`）和
`dd347f794e651039e7b4c391f86c674fed7f415b3dca6b0937beb0d470f09c1a`
（`libtinfo5`）。客户机中保留对应版权说明。

## 基本用法

主要命令前缀为：

```sh
csky-elfabiv2-
```

常用工具：

```sh
csky-elfabiv2-gcc
csky-elfabiv2-g++
csky-elfabiv2-as
csky-elfabiv2-ld
csky-elfabiv2-objcopy
csky-elfabiv2-objdump
csky-elfabiv2-size
csky-elfabiv2-gdb  # Linux/Windows 厂商包及 20261009 macOS GDB 更新包
```

压缩包中也包含 `csky-abiv2-elf-*` 命令名称。请使用你的构建系统或 SDK 所要求的前缀。

编译示例：

```sh
csky-elfabiv2-gcc -mcpu=ck803 -Os -g -o app.elf main.c
```

实际固件项目通常还需要开发板相关的启动文件、链接脚本、CPU 参数、ABI 参数和库选择。

## 注意事项

- 这些是二进制工具链，不是完整源码包。原生包的 `source-info/`
  保存 macOS 补丁副本与构建说明；elfuse 包包含 Apache-2.0 许可证。
- 不同主机包应分别放在独立目录。
- 部分随包文本字符串可能包含与 GCC 命令名不同的组件版本。如果需要确认精确组件来源，请在解压后执行 `--version`。
- 原始厂商包内未发现独立的 license 文件。重新分发前，请检查上游
  XRVM 页面以及 GCC、binutils、GDB、minilibc 和其他随包组件的许可证。
- macOS 工具链尚处于实验阶段；请勿假定它生成的二进制文件与厂商工具链生成的完全等效。
