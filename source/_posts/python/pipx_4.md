---
title: pipx 源码解析【4】- pipx install
date: 2021-09-06 20:12:38
tags: [python, venv]
categories: [python]
---

## 用 pipx 安装 app

上一篇学习了 `run` 命令, 这一篇主要学习下 `install` 命令的部分, 位置在 `src/pipx/commands/install.py`


这部分的代码相对较直接，从整个 `install` 函数看主要分如下步骤：

1. 从 `package_spec` 解析出 app 的 `package_name`
2. 获取 `venv` 路径。假设我们的 app 名字是 `cowsay`, 获取的 `venv_dir` 路径就是 `~/.local/pipx/venvs/cowsay`
3. 判断 `venv_dir` 是否已经存在
4. 如果已经存在，且有 `force` 选项，则提示用户 `venv` 目录已经存在，安装将覆盖原有目录内容。如果没有 `force` 选项，则提示用户后退出程序
5. 运行 `venv.create_venv` 创建虚拟目录
6. 运行 `venv.install_package` 安装 app
7. 如果上面都没有出错，则执行 `run_post_install_actions` 方法处理安装后的收尾工作，如果有一步报错，则执行 `venv.remove_venv` 删除虚拟目录。 

**注意**：上面 5， 6 两步在上一篇 `run` 命令中已经提到过了。只是 `run` 是在一个路径带 hash 值的临时虚拟目录里安装的（假设 hash 值是 abc 时:`~/.local/pipx/.cache/abc`），而 `install` 是以 package_name 命名的路径安装的: `~/.local/pipx/venvs/cowsay`。

<!--more-->

``` python
def install(
    venv_dir: Optional[Path],
    package_name: Optional[str],
    package_spec: str,
    local_bin_dir: Path,
    python: str,
    pip_args: List[str],
    venv_args: List[str],
    verbose: bool,
    *,
    force: bool,
    include_dependencies: bool,
    suffix: str = "",
) -> ExitCode:
    """Returns pipx exit code."""
    # package_spec is anything pip-installable, including package_name, vcs spec,
    #   zip file, or tar.gz file.

    if package_name is None:
        package_name = package_name_from_spec(
            package_spec, python, pip_args=pip_args, verbose=verbose
        )
    if venv_dir is None:
        venv_container = VenvContainer(constants.PIPX_LOCAL_VENVS)
        venv_dir = venv_container.get_venv_dir(f"{package_name}{suffix}")

    try:
        exists = venv_dir.exists() and next(venv_dir.iterdir())
    except StopIteration:
        exists = False

    venv = Venv(venv_dir, python=python, verbose=verbose)
    if exists:
        if force:
            print(f"Installing to existing venv {venv.name!r}")
        else:
            print(
                pipx_wrap(
                    f"""
                    {venv.name!r} already seems to be installed. Not modifying
                    existing installation in {str(venv_dir)!r}. Pass '--force'
                    to force installation.
                    """
                )
            )
            return EXIT_CODE_INSTALL_VENV_EXISTS

    try:
        venv.create_venv(venv_args, pip_args)
        venv.install_package(
            package_name=package_name,
            package_or_url=package_spec,
            pip_args=pip_args,
            include_dependencies=include_dependencies,
            include_apps=True,
            is_main_package=True,
            suffix=suffix,
        )
        run_post_install_actions(
            venv,
            package_name,
            local_bin_dir,
            venv_dir,
            include_dependencies,
            force=force,
        )
    except (Exception, KeyboardInterrupt):
        print()
        venv.remove_venv()
        raise

    # Any failure to install will raise PipxError, otherwise success
    return EXIT_CODE_OK
```


## 安装完成后的收尾工作

第 7 步的收尾工作里 `run_post_install_actions` 做了什么? 这里我个人理解主要做了如下几步:

1. 检查安装的包中有没有可执行文件，因为 `pipx` 是为了安装 app 而不是安装 library 的。如果安装的内容里没有可执行文件，则 raise error。如果 app 没有可执行文件但它的依赖中有可执行文件，则提示用户添加 `--include-deps` 选项。
2. 将安装的 app 暴露到全局 `expose_apps_globally`。
3. 检查用户的 `PATH` 环境变量，如果其中没有 pipx 的 local bin 路径 `.local/bin` ，则提示用户手动添加或者运行 `pipx ensurepath` 自动为用户添加

其中 `expose_apps_globally` 源码如下：
```python
def expose_apps_globally(
    local_bin_dir: Path, app_paths: List[Path], *, force: bool, suffix: str = ""
) -> None:
    if not can_symlink(local_bin_dir):
        _copy_package_apps(local_bin_dir, app_paths, suffix=suffix)
    else:
        _symlink_package_apps(local_bin_dir, app_paths, force=force, suffix=suffix)
```

默认认为 unix 系统都可以进行软链接，所以在不能软连的系统上直接 copy，可以的则软连。这里 copy 用的是 `shutil.copy`, 软连用的是 `path.symlink_to` 函数。

## 知识点
`pathlib` 里的 `path` 模块使用的时候有几个注意点:

1. 实例化用户主目录时要用 `Path.home() / abc`， 不能直接 `Path('~/abc')`
2. 对于指向软连的 path，`symlink_path.unlink` 是将软连删除
3. 对于软连和源文件 `symlink_path.samefile(source_path)` 返回 True
4. 判断是否是软连 `path.is_symlink()`
5. 对于指向软连的 path 调用 `symlink_path.exists()` 会判断软连和源文件是否都存在，只要有一个不存在，则返回 False