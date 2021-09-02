---
title: pipx 源码解析【2】- argparse 模块
date: 2021-09-02 23:00:17
tags: [python, venv]
categories: [python]
---

## 入口函数 `cli`

第一篇说到 `__main__` 函数，里面执行的就是入口函数 `cli`。`cli` 函数的逻辑如下:

```python
def cli() -> ExitCode:
    """Entry point from command line"""
    try:
        # 隐藏光标
        hide_cursor()
        # 初始化命令行参数解析器
        parser = get_command_parser()
        # 自动补全
        argcomplete.autocomplete(parser)
        # 解析命令行参数
        parsed_pipx_args = parser.parse_args()
        # 初始化准备工作（建立pipx 工作目录，配置日志）
        setup(parsed_pipx_args)
        # 检查参数准确性
        check_args(parsed_pipx_args)
        # 命令行参数是否有 command 参数
        if not parsed_pipx_args.command:
            parser.print_help()
            return ExitCode(1)
        # 执行命令
        return run_pipx_command(parsed_pipx_args)
        # 错误处理
    except PipxError as e:
        print(str(e), file=sys.stderr)
        logger.debug(f"PipxError: {e}", exc_info=True)
        return ExitCode(1)
    except KeyboardInterrupt:
        return ExitCode(1)
    except Exception:
        logger.debug("Uncaught Exception:", exc_info=True)
        raise
    finally:
        logger.debug("pipx finished.")
        # 显示光标
        show_cursor()
```

里面每个函数主要的功能都做了注释，最主要的就是 `get_command_parser` 和 `run_pipx_command` 两个函数。

这一篇这里先看 `get_command_parser` 函数，该只有一个作用，就是解析命令行参数。主要涉及到了 `argparse` 模块的使用，下面详细说明。

<!--more-->

## argparse 模块

`argparse` 是 python 内置的模块，主要用来解析命令行参数。具体的使用可以参照官方[文档](https://docs.python.org/3/library/argparse.html).注意只有在 python3.2 以及之后的版本才有这个模块。

我个人把 `argparse` 模块主要的用法分为`单命令`和`多命令`两类。单命令就是类似 `ls` 这样的命令，可以直接加参数，而多命令则类似 `brew` 这样的命令，会有很多子命令，比如 `brew install`, `brew update` 等等
。

## 单命令

下面是一个单命令的 🌰 。例子的命令就是文件名 `arg`,添加了三个参数 `--foo`, `--biz` 和 `--bar`, 更具体的可以参照官方文档。如果在命令行运行 `arg -f a`, 则会输出 `Namespace(bar=False, biz='b', foo='a')`。当然前提是需要把文件 `arg` 文件放到系统的 Path 目录里。

`arg.py`

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse


parser = argparse.ArgumentParser(prog='CliTest', description='this is a test cli')

parser.add_argument('--foo', '-f', help="arg for foo")
parser.add_argument('--biz', help="arg for biz", default='b')
parser.add_argument('--bar', help="flag for bar",  action='store_true')

parsed_args = parser.parse_args()

print(parsed_args)
```

## 多命令

多命令具体就只展示 🌰 ，不展开说明了，所有的用法都可以在官方文档里找到。

`subarg.py`

```python
#!/usr/bin/env python

# -*- coding: utf-8 -*-
import argparse

# create the top-level parser
parser = argparse.ArgumentParser(prog='CliTest', description='this is a test cli')
parser.add_argument('--foo', action='store_true', help='foo help')
parser.add_argument('--bar', help='bar help')
subparsers = parser.add_subparsers(
  dest="command", description="Get help for commands with pipx COMMAND --help"
)

# create the parser for the "install" command
parser_install = subparsers.add_parser('install', help='install help msg', description='desc for install')
parser_install.add_argument('name', type=str, help='name help msg')
parser_install.add_argument('version', type=int, help='version help msg', default=1)

# create the parser for the "uninstall" command
parser_uninstall = subparsers.add_parser('uninstall', help='uninstall help msg', description='desc for uninstall')
parser_uninstall.add_argument('name', type=str, help='name help msg')
parser_uninstall.add_argument('version', type=int, help='version help msg')

# create the parser for "list" command
parser_list = subparsers.add_parser("list", help='help msg for list', description='desc for list')
parser_list.add_argument("names", nargs="+", default=[], help='list names help msg')


parsed_args = parser.parse_args()

print(parsed_args)
```

## 例子代码下载

上面两个例子的源码可以在这里下载：

<a href='/static/python/arg' target="_blank">arg</a>
<a href='/static/python/subarg' target="_blank">subarg</a>
