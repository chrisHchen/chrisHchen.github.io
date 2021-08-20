---
title: python envoy 源码解析
date: 2019-10-26 22:33:17
tags: [python, 子进程]
categories: [python]
---

## envoy

[envoy](https://github.com/not-kennethreitz/envoy) 库的介绍上说它是一个可以被人类理解的 python 子进程。可以看出这个库的主要做用是使得 python 子进程的使用更加便利高效，并且符合人类的使用习惯。

## 前置知识点

看源码前需要对下面几个 python 原生库的使用有了解：

1. `shlex`
2. `subprocess.Popen`
3. `threading.Thread`

可以参考本文最后的参考资料。我也是边看源码边看查阅资料 🙂 ，感觉这样比较高效

<!--more-->

## 使用

![](/static/python/envoy.png)

## 源码

envoy 首先使用 `shlex` 对输入的命令行字符串进行解析:

```python
def expand_args(command):
    """Parses command strings and returns a Popen-ready list."""

    # Prepare arguments.
    if isinstance(command, (str, unicode)):
        splitter = shlex.shlex(command.encode('utf-8'))
        splitter.whitespace = '|'
        splitter.whitespace_split = True
        command = []

        while True:
            token = splitter.get_token()
            if token:
                command.append(token)
            else:
                break

        command = list(map(shlex.split, command))

    return command
```

如果对 `shlex` 原生库的使用比较熟悉的（我也不熟悉），这个函数就很容易理解。
举个例子：当函数接受的参数是 `ls -l | grep py` 时， 函数的 `while`循环首先会将输入解析为数组 `['ls -l', 'grep py']`，然后再使用 `shlex.split` 进一步解析为二维数组 `[['ls', '-l'], ['grep', 'py']]`。

这里解析为二维数组是因为后面的 `subprocess.Popen` 方法的第一个参数是字符串列表。`subprocess.Popen` 的使用参考本文最后的参考文章。

然后是构建子进程和传递 `stdin` 和 `stdout` 的过程, 具体的解析我在代码里做了注释:

```python
def run(self, data, timeout, kill_timeout, env, cwd):
        self.data = data
        # 覆盖更新环境变量
        environ = dict(os.environ)
        environ.update(env or {})

        def target():
            try:
                '''
                执行子进程
                这里的 self.cmd 就是上面 shlex 处理后返回的字符串列表
                注意接受字符串列表时 shell=False
                要给子进程的stdin发送数据，则Popen的时候，stdin要为PIPE；
                同理，要可以发送数据的话，stdout或者stderr也要为PIPE
                '''
                self.process = subprocess.Popen(self.cmd,
                    universal_newlines=True,
                    shell=False,
                    env=environ,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=0,
                    cwd=cwd,
                )

                if sys.version_info[0] >= 3: ## 兼容 python 版本
                    '''
                    和子进程交互：
                    将上一个子进程的 stdout 数据 PIPE 到这个子进程的 stdin
                    并从stdout和stderr读数据，直到收到EOF
                    '''
                    self.out, self.err = self.process.communicate(
                        input = bytes(self.data, "UTF-8") if self.data else None
                    )
                else:
                    self.out, self.err = self.process.communicate(self.data)
            except Exception as exc:
                self.exc = exc

        # 新建子线程
        thread = threading.Thread(target=target)
        thread.start()
        # 阻塞主线程，等待子线程执行结束
        thread.join(timeout)
        if self.exc:
            raise self.exc
        # 关闭子线程，一般是子线程出错的情况才会进入 if 的逻辑
        if _is_alive(thread) :
            _terminate_process(self.process)
            thread.join(kill_timeout)
            if _is_alive(thread):
                _kill_process(self.process)
                thread.join()
        self.returncode = self.process.returncode
        return self.out, self.err
```

另外，对于 `Popen` 的使用，下面是一个简单的例子：

![](/static/python/Popen.png)

## 参考资料

[python 中的 subprocess.Popen()使用](https://blog.csdn.net/qq_34355232/article/details/87709418)

[Python 多线程编程(一）：threading 模块 Thread 类的用法详解](https://blog.csdn.net/briblue/article/details/85101144)
