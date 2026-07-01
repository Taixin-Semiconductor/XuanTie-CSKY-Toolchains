# 玄铁 C-SKY GCC 工具链

[English](README.md)

本仓库保存来自 [XRVM](https://www.xrvm.cn/) 的玄铁 / C-SKY GCC 交叉编译工具链预编译二进制包。

这些工具链用于构建 C-SKY ELF ABI v2 裸机固件，并包含 minilibc 运行库。本仓库包含 Linux x86_64 主机版和 Windows MinGW 主机版。

## 仓库内容

| 压缩包 | 主机系统 | 目标平台 | 说明 | SHA256 |
| --- | --- | --- | --- | --- |
| `csky-elfabiv2-tools-x86_64-minilibc-20250328.tar.gz` | Linux x86_64 | `csky-elfabiv2` / `csky-abiv2-elf` | GCC 命令名和版本目录使用 `6.3.0`；包含 binutils、GDB、minilibc、多库支持 | `AD5C8564ADA7FBF77ACB952448B03A394D7AAFB56C945B2F8698D598076A69F9` |
| `csky-elfabiv2-tools-mingw-minilibc-20250328.tar.gz` | Windows MinGW | `csky-elfabiv2` / `csky-abiv2-elf` | GCC 命令名和版本目录使用 `6.3.0`；包含 binutils、GDB、minilibc、多库支持 | `3EB0FA8681F0996136902171855DB974659674ED3D6EBE7DDC6A601DDC0F27F2` |

版本日期为 `20250328`，来自上游压缩包文件名。

## 支持的目标变体

压缩包内包含以下 multilib 目录：

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
csky-elfabiv2-gdb
```

压缩包中也包含 `csky-abiv2-elf-*` 命令名称。请使用你的构建系统或 SDK 所要求的前缀。

编译示例：

```sh
csky-elfabiv2-gcc -mcpu=ck803 -Os -g -o app.elf main.c
```

实际固件项目通常还需要开发板相关的启动文件、链接脚本、CPU 参数、ABI 参数和库选择。

## 注意事项

- 这些是预编译二进制工具链，不是源码包。
- 不建议将 Linux 和 Windows 压缩包解压到同一目录，除非你明确需要混合不同主机平台的文件。
- 部分随包文本字符串可能包含与 GCC 命令名不同的组件版本。如果需要确认精确组件来源，请在解压后执行 `--version`。
- 压缩包内未发现独立的 license 文件。重新分发前，请检查上游 XRVM 页面以及 GCC、binutils、GDB、minilibc 和其他随包组件的许可证。
- 编写本 README 时，这两个压缩包均低于 GitHub 常规的单文件 100 MB 限制。未来更大的版本可能需要使用 Git LFS 或 GitHub Releases。
