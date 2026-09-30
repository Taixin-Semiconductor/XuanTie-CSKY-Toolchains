# 玄铁 C-SKY GCC 工具链

[English](README.md)

本仓库保存玄铁 / C-SKY GCC 交叉编译工具链二进制包。Linux 和 Windows
包来自 [XRVM](https://www.xrvm.cn/)；原生 macOS arm64 包从固定的 V3.10
GCC/binutils 源码构建。另有 macOS arm64 兼容包，通过 elfuse 运行 Linux
厂商工具链。

这些包用于构建带 minilibc 的 C-SKY ELF ABI v2 裸机固件。请按主机平台
选择一个包，并分别解压到独立目录。

## 仓库内容

| 压缩包 | 主机系统 | 目标平台 | 说明 | SHA256 |
| --- | --- | --- | --- | --- |
| `csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz` | Linux x86_64 | `csky-elfabiv2` / `csky-abiv2-elf` | GCC 命令名和版本目录使用 `6.3.0`；包含 binutils、GDB、minilibc、多库支持 | `AD5C8564ADA7FBF77ACB952448B03A394D7AAFB56C945B2F8698D598076A69F9` |
| `csky-elfabiv2-tools-mingw-minilibc-20250328.tar.gz` | Windows MinGW | `csky-elfabiv2` / `csky-abiv2-elf` | GCC 命令名和版本目录使用 `6.3.0`；包含 binutils、GDB、minilibc、多库支持 | `3EB0FA8681F0996136902171855DB974659674ED3D6EBE7DDC6A601DDC0F27F2` |
| `csky-elfabiv2-tools-macos-arm64-native-ml40-20260930.tar.xz` | macOS arm64 原生 | `csky-elfabiv2` / `csky-abiv2-elf` | GCC 6.3.0、binutils 2.27、40 种 multilib；C/C++；无 GDB；依赖 Homebrew GMP/MPFR/libmpc | `c22d4d2566f9a5b49d58c8bb048805a899de596d04a75f7cd615f507717bc973` |
| `csky-elfabiv2-tools-macos-arm64-elfuse-20260930.tar.xz` | macOS arm64 elfuse | `csky-elfabiv2` / `csky-abiv2-elf` | 通过随包 elfuse 和客户机 sysroot 运行固定版本的 Linux x86_64 厂商 GCC 6.3.0；未提供 GDB 包装命令 | `6fde30003fe1f9f2a4de296a04c372c698c1a45f60c442aeacc5e312bdec9ab6` |

厂商包保留上游文件名中的 `20250328`。两个 `20260930` 包来自本地
有日期记录的 macOS 构建与 elfuse 验证。

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

两个 macOS 包分别解压到不同的顶层目录。原生 Mach-O 工具声明的
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
120 个 C/C++/浮点编译与链接检查。这些均为主机侧结果，尚无目标端执行
或真实硬件验证；原生源码构建的 `libgcc.a` 和 `libstdc++.a` 也与
厂商包不逐字节一致。

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
csky-elfabiv2-gdb  # 仅 Linux 和 Windows 厂商包
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
