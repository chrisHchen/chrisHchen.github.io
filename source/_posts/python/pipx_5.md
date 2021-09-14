---
title: pipx 源码解析【5】- pipx inject
date: 2021-09-14 21:12:38
tags: [python, venv]
categories: [python]
---

## pipx inject

`pipx inject` 命令用会往存在的虚拟环境中安装指定的包。语法是 `pipx inject abc --dependencies depA depB`。这个命令会把 `depA` 和 `depB` 安装到已经存在的 `abc` 虚拟环境中。

## inject.py

和之前的命令一样，inject 会调用 `command/inject.py` 模块。最终调用的是 `inject_dep` 方法:

```python
all_success = True

for dep in package_specs:
        all_success &= inject_dep(
            venv_dir,
            None,
            dep,
            pip_args,
            verbose=verbose,
            include_apps=include_apps,
            include_dependencies=include_dependencies,
            force=force,
        )

return EXIT_CODE_OK if all_success else EXIT_CODE_INJECT_ERROR
```

`inject_dep` 做了如下几步：

1. 判断 `inject` 的目标虚拟环境是否存在。
2. 运行 `venv.install_package` 安装 app
3. 如果上面都没有出错，则执行 `run_post_install_actions` 方法处理安装后的收尾工作，如果有一步报错，则执行 `venv.remove_venv` 删除虚拟目录。

这里的 2，3 两步在上一篇的 `pipx install` 命令已经学习过了，所以从这个层面看，inject 和 install 的差别只是 inject 会指定一个存在的虚拟目录，而 install 是创建一个新的 `venv`

inject 命令不复杂，所涉及的知识点也基本上在之前 `install` 和 `run` 两个命令中提到过了。
