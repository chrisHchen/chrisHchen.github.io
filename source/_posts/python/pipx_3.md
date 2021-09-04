---
title: pipx 源码解析【3】- pipx run
date: 2021-09-03 20:00:38
tags: [python, venv]
categories: [python]
---

## 执行命令

上一篇学习了如何解析参数，这一篇主要学习如何执行命令。`pipx` 的命令(command)包括 `run`, `install`, `inject`, `upgrade`, `upgrade-all`, `list`, `uninstall`, `uninstall-all`, `reinstall`, `reinstall-all`。

`run_pipx_command` 作为命令的主入口，将不同的 command 分配给不同的模块处理。处理 `run` 命令是 `run.py`。

这篇就先学一个 `run`， 我也将通过记录知识点的方式学习。

## 知识点：下载网络文件

`run.py` 首先判断参数是否为 url，且以 `.py` 结尾，如果为真就直接从 url 下载这个文件:

```python
...
if urllib.parse.urlparse(app).scheme:
        if not app.endswith(".py"):
            raise PipxError(
                """
                pipx will only execute apps from the internet directly if they
                end with '.py'. To run from an SVN, try pipx --spec URL BINARY
                """
            )
        logger.info("Detected url. Downloading and executing as a Python file.")

        content = _http_get_request(app)
        exec_app([str(python), "-c", content])

...

def _http_get_request(url: str) -> str:
    try:
        res = urllib.request.urlopen(url)
        charset = res.headers.get_content_charset() or "utf-8"
        return res.read().decode(charset)
    except Exception as e:
        logger.debug("Uncaught Exception:", exc_info=True)
        raise PipxError(str(e))
```

其中下载网络文件用了 `urllib.request.urlopen(url)` 这个方法。下载完成后进入 `exec_app` 方法。

<!--more-->

## 知识点: 获取/调整系统环境变量

`exec_app` 方法内首先获取了系统环境变量 `env = dict(os.environ)`。然后又设置了系统变量 `PYTHONPATH`。
另外也可以学习一下 python 里 `join` 和 `split` 的用法。然后按操作系统的不同分别调用了不同的执行方法，源码里也有注释。

```python
def exec_app(
    cmd: Sequence[Union[str, Path]],
    env: Optional[Dict[str, str]] = None,
    extra_python_paths: Optional[List[str]] = None,
) -> NoReturn:
    """Run command, do not return

    POSIX: replace current processs with command using os.exec*()
    Windows: Use subprocess and sys.exit() to run command
    """

    if env is None:
        env = dict(os.environ)
    env = _fix_subprocess_env(env)

    if extra_python_paths is not None:
        env["PYTHONPATH"] = os.path.pathsep.join(
            extra_python_paths
            + (
                os.getenv("PYTHONPATH", "").split(os.path.pathsep)
                if os.getenv("PYTHONPATH")
                else []
            )
        )

    # make sure we show cursor again before handing over control
    show_cursor()

    logger.info("exec_app: " + " ".join([str(c) for c in cmd]))

    if WINDOWS:
        sys.exit(
            subprocess.run(
                cmd,
                env=env,
                stdout=None,
                stderr=None,
                encoding="utf-8",
                universal_newlines=True,
            ).returncode
        )
    else:
        os.execvpe(str(cmd[0]), [str(x) for x in cmd], env)
```

`os.execvpe` 函数在 $PATH 上寻找并执行可执行文件，并且会替代原来的进程, 具体的用法可以看下面的例子:

<img src="/static/python/pipx1.png" alt="os.execvpe" width="640" align="bottom" />

可以看到运行完以后退出了 python 的 REPL,说明已经替换了原来的进程。

另外 `python -c` 是执行源码的命令，而我们平时常用的是没有 `-c` 的，是直接执行文件的命令。

更多关于 `os.exec*` 的内容可以参考下面文章：

[Python:OS 模块 -- 进程管理](https://blog.csdn.net/u011630575/article/details/50917476)
[python 文档: os 模块](https://docs.python.org/zh-cn/3/library/os.html?highlight=execvpe#os.execvpe)

## 知识点: `__pypackages__`

上面说的是从网络 url 下载 `.py` 文件并执行，如果不是 `.py` 而是 binary 该如何处理呢？也就是运行 `pipx run BINARY`的情况。这里涉及到一个概念 `__pypackages__` 的概念，也称为 `python local packages directory`。具体定义可以看[这里](https://github.com/cs01/pythonloc):

<blockquote style='text-align:left'>
pythonloc is a drop in replacement for python and pip that automatically recognizes a __pypackages__ directory and prefers importing packages installed in this location over user or global site-packages. If you are familiar with node, __pypackages__ works similarly to node_modules.
</blockquote>

`pipx` 也支持这个特性, 通过下面的函数获得了 `local packages` 的 binary 文件：

```python
def get_pypackage_bin_path(binary_name: str) -> Path:
    return (
        Path("__pypackages__")
        / (str(sys.version_info.major) + "." + str(sys.version_info.minor))
        / "lib"
        / "bin"
        / binary_name
    )
```

如果上面的函数找到了对应的 `binary`, 这会进入下面 `run_pypackage_bin` 函数，内部最后还是调用到上文提到过的 `exec_app` 函数:

```python
def run_pypackage_bin(bin_path: Path, args: List[str]) -> NoReturn:
    exec_app(
        [str(bin_path.resolve())] + args,
        extra_python_paths=[".", str(bin_path.parent.parent)],
    )
```

## 知识点: venv

上文说到了网络 `.py` 文件和本地已经存在 `binary` 的情况。下面会处理本地不存在 `binary` 的情况。
这时需要首先下载 binary，然后才能执行。这时就存在一个存放路径的目录问题。`pipx` 的介绍中提到对 app 有环境隔离的能力，这里就是用了 venv 模块的能力。

首先用 hash 算法获得一个唯一的 venv 路径：

```python
def _get_temporary_venv_path(
    package_or_url: str, python: str, pip_args: List[str], venv_args: List[str]
) -> Path:
    """Computes deterministic path using hashing function on arguments relevant
    to virtual environment's end state. Arguments used should result in idempotent
    virtual environment. (i.e. args passed to app aren't relevant, but args
    passed to venv creation are.)
    """
    m = hashlib.sha256()
    m.update(package_or_url.encode())
    m.update(python.encode())
    m.update("".join(pip_args).encode())
    m.update("".join(venv_args).encode())
    venv_folder_name = m.hexdigest()[0:15]  # 15 chosen arbitrarily
    return Path(constants.PIPX_VENV_CACHEDIR) / venv_folder_name
```

其中的 `PIPX_VENV_CACHEDIR` 指向 `Path.home() / ".local/pipx" / ".cache"` 。所以最终临时目录指向是用户目录下的 `~/.local/pipx/.cache/xxx`,其中 `xxx` 就是通过 `package_or_url`, `python 路径`，`pip_args`, `venv_args` 这几个参数计算出来的 15 位 hash 值。

接下来获得了 `Venv` 的实例：`venv = Venv(venv_dir)`，Vene 类是 pipx 对虚拟目录的抽象，提供了一些列对虚拟目录操作的方法。个人感觉用一个例子来说明这个类会更加直观。所以假设某个 run 某个 app 时获取的 hash 值为 `abc`，那么对应 `venv_dir`就是 `~/.local/pipx/.cache/abc`，实例化 Venv 后对应的一些属性的值如下(POSIX)：

`venv.root = ~/.local/pipx/.cache/abc`
`venv.bin_path = ~/.local/pipx/.cache/abc/bin`
`venv.python_path = ~/.local/pipx/.cache/abc/bin/python`
`venv.python = 系统默认 python 路径`

接下来执行的代码如下:

```python
if venv.has_app(app, app_filename):
        logger.info(f"Reusing cached venv {venv_dir}")
        venv.run_app(app, app_filename, app_args)
    else:
        logger.info(f"venv location is {venv_dir}")
        _download_and_run(
            Path(venv_dir),
            package_or_url,
            app,
            app_filename,
            app_args,
            python,
            pip_args,
            venv_args,
            use_cache,
            verbose,
        )
```

如果 `venv` 里之前就下载了这个 app，并且参数 `use_cache` 是 true，就直接执行，否则先下载再执行。
`venv.run_app` 进过一些列 `entry_point` 的解析后最终还是调用了上文提到过的 `exec_app`。

如果之前没有下载过，则进入 `_download_and_run` 函数，并创建一个新的虚拟环境 `venv.create_venv(venv_args, pip_args)`：

```python
def create_venv(self, venv_args: List[str], pip_args: List[str]) -> None:
        with animate("creating virtual environment", self.do_animation):
            cmd = [self.python, "-m", "venv", "--without-pip"]
            venv_process = run_subprocess(cmd + venv_args + [str(self.root)])
        subprocess_post_check(venv_process)

        shared_libs.create(self.verbose)
        pipx_pth = get_site_packages(self.python_path) / PIPX_SHARED_PTH
        # write path pointing to the shared libs site-packages directory
        # example pipx_pth location:
        #   ~/.local/pipx/venvs/black/lib/python3.8/site-packages/pipx_shared.pth
        # example shared_libs.site_packages location:
        #   ~/.local/pipx/shared/lib/python3.6/site-packages
        #
        # https://docs.python.org/3/library/site.html
        # A path configuration file is a file whose name has the form 'name.pth'.
        # its contents are additional items (one per line) to be added to sys.path
        pipx_pth.write_text(f"{shared_libs.site_packages}\n", encoding="utf-8")

        self.pipx_metadata.venv_args = venv_args
        self.pipx_metadata.python_version = self.get_python_version()
```

创建虚拟目录使用的是 `run_subprocess`, 最后执行到的是 `subprocess.run` 函数。注意 `subprocess.run` 不会替换原来的进程，(和上面的 `os.execvpe` 不一样)，因为虚拟目录创建完成后主进程还有别的工作要完成。

创建虚拟目录用的是 python 内置模块 `venv`, 使用的命令是 `python -m venv --without-pip ~/.local/pipx/.cache/abc`。

虚拟目录创建完成后执行 `venv.install_package` 方法安装 app，安装 app 用的是 `pip`, 这里用的 python 是虚拟目录里的 python， 安装的目录是虚拟目录下的 `lib/pythonx.x/site-package`。

```python
cmd = (
    [str(self.python_path), "-m", "pip", "install"]
    + pip_args
    + [package_or_url]
)
# no logging because any errors will be specially logged by
#   subprocess_post_check_handle_pip_error()
pip_process = run_subprocess(cmd, log_stdout=False, log_stderr=False)
```

安装完成后最终还是调用 `venv.run_app` 方法来执行。到这里 `run` 命令的主体就学习完了。下面补充几个过程中值得注意的知识点。

## 知识点: shared library

在 `create_venv` 函数中，除了创建虚拟目录外，还创建了 `share libs`, share libs 是一个所有 pipx 的虚拟目录都可以共享的目录，有点像全局安装目录。

```python
# venv.py
shared_libs.create(self.verbose)
pipx_pth = get_site_packages(self.python_path) / PIPX_SHARED_PTH
# write path pointing to the shared libs site-packages directory
# example pipx_pth location:
#   ~/.local/pipx/venvs/black/lib/python3.8/site-packages/pipx_shared.pth
# example shared_libs.site_packages location:
#   ~/.local/pipx/shared/lib/python3.6/site-packages
#
# https://docs.python.org/3/library/site.html
# A path configuration file is a file whose name has the form 'name.pth'.
# its contents are additional items (one per line) to be added to sys.path
pipx_pth.write_text(f"{shared_libs.site_packages}\n", encoding="utf-8")

# shared_libs.py
def create(self, verbose: bool = False) -> None:
    if not self.is_valid:
        with animate("creating shared libraries", not verbose):
            create_process = run_subprocess(
                [DEFAULT_PYTHON, "-m", "venv", "--clear", self.root]
            )
        subprocess_post_check(create_process)

        # ignore installed packages to ensure no unexpected patches from the OS vendor
        # are used
        self.upgrade(pip_args=["--force-reinstall"], verbose=verbose)
```

pipx share_libs 的目录是 `~/.local/pipx/shared`, 进入 `shared_libs.create` 方法，用默认的 python 解释器在 `~/.local/pipx/shared` 目录下创建了虚拟目录。最后在 venv 的 `site_packages` 下的 `pipx_shared.pth` 文件里写入了 share_libs 的 `site_packages` 目录。这样在虚拟目录中运行 app 时，遇到模块加载时也会去 share_libs 搜索。其中有关 share_libs 可以参考源码给出的[文档连接](https://docs.python.org/3/library/site.html)

## 知识点: 获取系统默认 python 解释器路径

`Venv` 类中创建虚拟目录的默认 python 解释器是如何获取的呢？

```python
def _get_sys_executable() -> str:
    if WINDOWS:
        return _find_default_windows_python()
    else:
        return sys.executable
```

其中 window 系统的获取比较繁琐，主要是处理几类兼容性问题，而 POSIX 系统则直接取 `sys.executable` 的值就可以了。

## 知识点: 移除过期文件夹

源码中判断过期的函数如下：

```python
def _is_temporary_venv_expired(venv_dir: Path) -> bool:
    created_time_sec = venv_dir.stat().st_ctime
    current_time_sec = time.mktime(datetime.datetime.now().timetuple())
    age = current_time_sec - created_time_sec
    expiration_threshold_sec = 60 * 60 * 24 * TEMP_VENV_EXPIRATION_THRESHOLD_DAYS
    return age > expiration_threshold_sec or (venv_dir / VENV_EXPIRED_FILENAME).exists()
```

其中 `venv_dir.stat().st_ctime` 返回的是最后一次 metadata 改变的时间，这里可以认为是文件夹被创建的时间。关于 `Path.stat()` 返回的数据可以参考官方[文档](https://docs.python.org/3/library/os.html#os.stat_result)

另外获取当前时间戳的函数是 `time.mktime(datetime.datetime.now().timetuple())`

## 知识点: 获取 site-package 路径

源码用的方法如下, 这里获取的是特定 python 解释器的 site-package：

```python
def get_site_packages(python: Path) -> Path:
    output = run_subprocess(
        [python, "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
        capture_stderr=False,
    ).stdout
    path = Path(output.strip())
    path.mkdir(parents=True, exist_ok=True)
    return path
```

待续...
