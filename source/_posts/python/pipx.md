---
title: pipx 源码解析【1】
date: 2021-08-31 21:33:17
tags: [python, venv]
categories: [python]
---

## pipx 是什么？

[pipx](https://github.com/pypa/pipx) 是一个 python 包管理工具。但和 `pip` 又有区别: `pip` 管理 python 的类库（libraries）和应用（apps），而 `pipx` 专门管理 python 的应用（apps），另外在此基础上添加了环境隔离的能力。总体上来说有点像 Mac 系统上的 `brew`。

类库和应用怎么区分？我个人理解这里的应用主要指的是可以直接在命令行里执行的脚本，也就是发布时会在 `setup.py` 写入 `console_scripts` 字段的 python 库( 安装后生成了可执行脚本并放入 `bin` 文件夹)。举个 🌰 ，比如 `pip`, `virtualenv` 这类可以直接在命令行执行的就是应用，而 `numpy`, `pandas` 这类在代码中 import 的则属于类库。另外 `pipx` 自己本身也是一个应用。

为什么要用隔离环境来单独管理应用呢？我能想到很明显的一个原因是各个应用依赖的版本冲突问题。举个 🌰 ，需要全局安装应用 A 和 应用 B， A 和 B 都依赖某一个类库 C，但依赖的版本不一样，A 依赖 C=1.0，B 依赖 C=2.0。如果先装了 A，在没有环境隔离的情况下，全局的 `site-package` 下面会有 C=1.0 的版本，这时如果我再安装 B，因为 B 依赖 C=2.0，所以安装完成后会将全局 `site-package` 里的 C=1.0 替换为 C=2.0。这可能会导致应用 A 无法正常工作。

更详细的可以参照 `pipx` 的[文档](https://pypa.github.io/pipx/)

<!--more-->

## 前言

我看的是`0.16.3`的版本。因为源码文件较多，我自己也是边学习边记录。总体会分几篇文章来记录我认为值得关注的知识点，看到不熟悉的地方可能会单独开一篇文章来说明。

下面的源码解析还是会通过`思路分析 + 知识点`的方式来记录。我认为阅读源码一方面是学习作者的思路，另一方面也是积累知识点的过程。

## 知识点 1 `setup.cfg`

之前看到的 python 库大部分都是用 setup.py 来发布，所以我对 `setup.cfg` 不熟悉。这里补充一下[文档](https://setuptools.readthedocs.io/en/latest/userguide/declarative_config.html)。具体就不详细说明了。如果写过前端就很容易理解，用法其实类似 `bable.config.js` 和 `.bablerc`的关系。

## 知识点 2 `__main__.py` 和 `__init__.py`

在 python 中，一个文件就是一个模块。那么如果是文件夹呢？ python 的处理方式是，如果文件夹下面有 `__init__.py` 这个文件，则认为该文件夹是一个模块，对于模块就可以直接执行。

举个 🌰 ：对于下面的文件夹 `cow`, 如果执行 `python -m cow` 命令（`-m` 表示以模块的方式执行 `cow`）, 会先执行 `__init__.py`，然后再执行 `__main__.py`。如果直接执行 `python cow`，则不认为`cow` 是一个模块，所以 `__init__.py` 不会执行，只会执行 `__main__.py`

```
└── cow
    ├── __init__.py
    ├── __main__.py
```

另外还有一点要注意的，以模块的方式执行文件夹的时候，会把当前目录放入搜索路径 `sys.path`。而非模块方式执行则不会。也就是说当 `cow` 下有某个文件使用了 `import cow` 这样的语法时，以非模块方式运行将报错，因为系统搜索路径里没有当前路径。

关于这个知识点可以参考这篇文章[`【Package内的__main__.py和__init__.py】`](https://blog.csdn.net/u011857683/article/details/81571425)

看下 `pipx` 源码里的处理：

```python
if sys.version_info < (3, 6, 0):
    sys.exit(
        "Python 3.6 or later is required. "
        "See https://github.com/pypa/pipx "
        "for installation instructions."
    )
```

在 `__init__.py` 中对 python 支持的版本做了判断。

```python
if not __package__:
    # Running from source. Add pipx's source code to the system
    # path to allow direct invocation, such as:
    #   python src/pipx --help
    pipx_package_source_path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, pipx_package_source_path)

from pipx.main import cli  # noqa

if __name__ == "__main__":
    sys.exit(cli())
```

在 `__main__.py` 里对 `__package__` 不存在的情况，也就非模块执行时(不加 `-m` 参数), 手动把源码的 `src` 目录添加到系统搜索路径里面。

待续...
