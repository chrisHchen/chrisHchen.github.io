---
title: python records 源码解析
date: 2021-08-21 18:55:00
tags: [python, 数据库]
categories: [python]
---

## 总览

[records](https://github.com/kennethreitz/records) 库是 python 大神 kennethreitz 写的一个 `SQL for Human` 的 python 库，意在让书写 sql 更加的便捷和人性化。

从 README 里可以看出 `records` 是对 `sqlalchemy` 和 `tablist` 的一层包装，所以阅读源码主要是学习作者 `pythonic` 的代码编写思维。

**所以本文不会纠结于源码的具体逻辑，重点是学习一些知识点，下面的每一段都会针对我觉得值得借鉴和学习的某一个知识点来做记录**。

## 1. 如何让代码既能用做 module 又可以被直接执行

如果是直接执行 `records.py`, 则会进入下面的函数，然后再 `cli()` 方法内部使用 `docopt` 来解析命令行参数。`docopt` 的使用可以参考之前的的文章 [envoy 源码解析](https://chrishchen.github.io/2019/10/26/python/envoy/)

```python
# Run the CLI when executed directly.
if __name__ == '__main__':
    cli()
```

## 2.querystring 转 dict

源码中用到将命令行输入的 `params` 转 `dict` 的函数

```python
try:
        params = dict([i.split('=') for i in params])
    except ValueError:
        print('Parameters must be given in key=value format.')
        exit(64)
```

个人感觉十分巧妙且实用，主要巧妙使用的 `dict` 构造函数:

```python
dict(iterable) -> new dictionary initialized as if via:
    d = {} for k, v in iterable:
        d[k] = v
```

类似的，如果我们有一个 querystring 结构的字符串 `i=1&j=2`, 也可以通过下面的步骤解析为 `dict`:

![](/static/python/records-01.png)

## 3.`__enter__` 和 `__exit__` 魔术方法

源码中 `Database` 类用到了如下的结构：

```python
class Database(object):
    ...
    def __enter__(self):
        return self

    def __exit__(self, exc, val, traceback):
        self.close()
    ...
```

这两个魔术方法主要是配合 `with` 关键词来使用的，为了让一个对象兼容 `with` 语句，必须在这个对象的类中声明 \_\_enter\_\_ 和 \_\_exit\_\_ 方法。具体的知识点可以参考此文：[python 之 \_\_enter\_\_ 和 \_\_exit\_\_](https://blog.csdn.net/qq_37482956/article/details/100056517)

## 4.@contextmanager

上面提到的 `with` 语句的上下文管理，除了使用 \_\_enter\_\_ 和 \_\_exit\_\_ 方法，还可以使用 python 内置的 `contextlib.contextmanager` 装饰器来实现:

```python
@contextmanager
def transaction(self):
    """A context manager for executing a transaction on this Database."""

    conn = self.get_connection()
    tx = conn.transaction()
    try:
        yield conn
        tx.commit()
    except:
        tx.rollback()
    finally:
        conn.close()
```

这里 `yield` 语句其实是一个生成器，`yield` 前面的代码就是 \_\_enter\_\_ 的作用，`yield` 后面的代码就是 \_\_exit\_\_ 的作用。更详细的可以参考这篇文章 [Python 进阶：With 语句和上下文管理器 ContextManager](https://zhuanlan.zhihu.com/p/24709718)

## 5. generator 生成器

`records` 在 query 数据时返回 `results` 是一个 `RecordCollection` 类的实例。这个类的构造方法是接收一个 **生成器(generator)** `row_gen = (Record(cursor.keys(), row) for row in cursor)`:

```python
def query(self, query, fetchall=False, **params):
    """Executes the given SQL query against the connected Database.
    Parameters can, optionally, be provided. Returns a RecordCollection,
    which can be iterated over to get result rows as dictionaries.
    """

    # Execute the given query.
    cursor = self._conn.execute(text(query), **params) # TODO: PARAMS GO HERE

    # Row-by-row Record generator.
    row_gen = (Record(cursor.keys(), row) for row in cursor)

    # Convert psycopg2 results to RecordCollection.
    results = RecordCollection(row_gen)

    # Fetch all results if desired.
    if fetchall:
        results.all()

    return results
```

这里需要注意的是生成器表达式的写法和列表的区别，生成器表达式用`()`, 而列表用 `[]`:

```python
g = (_ for _ in range(5)) # g 是生成器
l = [_ for _ in range(5)] # l 是列表
```

## 6.`__iter__` 和 `__next__` 魔术方法

首先看下源码中 `RecordCollection` 的实现

```python
def __iter__(self):
      """Iterate over all rows, consuming the underlying generator
      only when necessary."""
      i = 0
      while True:
          # Other code may have iterated between yields,
          # so always check the cache.
          if i < len(self):
              yield self[i]
          else:
              # Throws StopIteration when done.
              # Prevent StopIteration bubbling from generator, following https://www.python.org/dev/peps/pep-0479/
              try:
                  yield next(self)
              except StopIteration:
                  return
          i += 1

  def next(self):
      return self.__next__()

  def __next__(self):
      try:
          nextrow = next(self._rows)
          self._all_rows.append(nextrow)
          return nextrow
      except StopIteration:
          self.pending = False
          raise StopIteration('RecordCollection contains no more rows.')
```

这里主要的知识点是区别 `iterable` 和 `iterator`:

```python
class B(object):
    def __next__(self):
        raise StopIteration

class A(object):
    def __iter__(self):
        return B()
```

`Iterable`: 有迭代能力的对象，一个类，实现了**iter**，那么就认为它有迭代能力，通常此函数必须返回一个实现了\_\_next\_\_的对象，如果自己实现了，你可以返回 self，当然这个返回值不是必须的；

`Iterator`: 迭代器(当然也是 `Iterable`)，同时实现了 \_\_iter\_\_和\_\_next\_\_的对象，缺少任何一个都不算是 `Iterator`，比如上面例子中，A()可以是一个 Iterable，但是 A()和 B()都不能算是和 Iterator，因为 A 只实现了\_\_iter\_\_，而 B 只实现了\_\_next\_\_()。

对于这个知识点的详细内容，可以直接看这篇文章[【Python 魔术方法】迭代器(\_\_iter\_\_和\_\_next\_\_)](https://www.jianshu.com/p/1b0686bc166d)。

这里我觉得比较重要的一个点就是当使用 `for r in recordCollection` 这种方式去迭代 `RecordCollection` 的实例的时候，其实并不会直接执行到 `RecordCollection` 的 `__next__` 方法,因为这里 `__iter__` 返回的是一个 `迭代器(generator)`, 而 `generator` 本身就是一个 `iterator`, 它有自己的 `__iter__` 和 `__next__` 方法。

所以本质上用 `for r in recordCollection` 这种方式去迭代 `RecordCollection` 的实例的时候，会调用 `generator` 的 `__next__` 方法，从而返回 `yield` 后面的内容，所以真正执行 `RecordCollection.__next__` 方法的 是 `generator` 的 `__next__` 方法。 另外有关生成器也可以看下这篇文章[【Python 魔术方法】生成器(yield 表达式)](https://www.jianshu.com/p/5ee724a8c366)。

这里说起来有点绕，不如直接看一个 🌰 ：

```python
class Test():
    def __init__(self) -> None:
        self.i = 0

    def __iter__(self):
        print('start __iter__')
        while self.i < 5:
            yield 'iter:{}'.format(self.i)
            self.i += 1

    def __next__(self):
        print('start __next__')
        if self.i > 5:
            raise StopIteration
        self.i += 1
        return 'next:{}'.format(self.i)

for i in Test():
    print(i)
```

这里定义了 `__iter__` 和 `__next__`方法，执行结果如下：

![](/static/python/records-02.png)

可以看到并没有打印 `start __next__`, 也就是说 `__next__` 方法并没有执行，所以去掉 `__next__` 方法也不影响代码执行。

但是当我们用 `next` 方法去执行的时候：

```python
class Test():
    def __init__(self) -> None:
        self.i = 0

    def __iter__(self):
        print('start __iter__')
        while self.i < 5:
            yield 'iter:{}'.format(self.i)
            self.i += 1

    def __next__(self):
        print('start __next__')
        if self.i > 5:
            raise StopIteration
        self.i += 1
        return 'next:{}'.format(self.i)

t = Test()
print(next(t))
```

这时的执行结果是:

![](/static/python/records-03.png)

可以看到 `next` 方法会调用实例上的 `__next__` 方法，这点和 `for` 循环不太一样。如果我们要让 `next` 方法也调用 `__iter__` 返回的 `generator.__next__` 应该怎么写呢，其实也不难：

```python
class Test():
    def __init__(self) -> None:
        self.i = 0

    def __iter__(self):
        print('start __iter__')
        while self.i < 5:
            yield 'iter:{}'.format(self.i)
            self.i += 1

    def __next__(self):
        print('start __next__')
        if self.i > 5:
            raise StopIteration
        self.i += 1
        return 'next:{}'.format(self.i)

t = iter(Test())
print(next(t))
```

执行结果如下：

![](/static/python/records-04.png)

这里使用了 `iter` 方法。 `iter` 方法会调用实例上的 `__iter__` 方法，所以返回的就是一个 `generator` 了。

另外，从上面的几个例子，可以看出来当我们使用 `for _ in iterable` 这样的语法的时候，python 编译器其实会将我们的代码转换为 `for _ in iter(iterable)`, 最终迭代的是 `iterable` 实例上 `__iter__` 方法返回的 `iterator`。

## 7.为什么源码里 `__iter__` 不直接返回 `self`？

作者在这样做的原因是希望迭代器可以缓存之前已经读取过的结果，当再次读取时，可以直接从缓存读取，不需要再从数据库游标去读取, 如果直接返回 self，那么每次 for 循环都会走数据库游标:

```python
def __iter__(self):
  """Iterate over all rows, consuming the underlying generator
  only when necessary."""
  i = 0
  while True:
      # Other code may have iterated between yields,
      # so always check the cache.
      if i < len(self):
          yield self[i]
      else:
          # Throws StopIteration when done.
          # Prevent StopIteration bubbling from generator, following https://www.python.org/dev/peps/pep-0479/
          try:
              yield next(self)
          except StopIteration:
              return
      i += 1
```

作者的这个意图也可以从 test 文件夹里的测试用例看出来:

```python
from collections import namedtuple
import records
from pytest import raises

IdRecord = namedtuple('IdRecord', 'id')

def check_id(i, row):
    assert row.id == i

def test_iter_and_next(self):
    rows = records.RecordCollection(IdRecord(i) for i in range(10))
    i = enumerate(iter(rows))
    check_id(*next(i))  # Cache first row.
    next(rows)  # Cache second row.
    check_id(*next(i))  # Read second row from cache.

```

这里作者测试用例写的是 `i = enumerate(iter(rows))` 而不是 `i = enumerate(rows)`。也就是 `next(i)` 调用的是 `__iter__`，而不是 `__next__`。所以能测试到缓存。

## 8.`__getitem__` 魔术方法

当我们在实例上调用 `[]` 运算符时，实际上调用的就是实例的 `__getitem__` 方法。源码对 `RecordCollection.__getitem__` 的实现如下:

```python
def __getitem__(self, key):
    is_int = isinstance(key, int)

    # Convert RecordCollection[1] into slice.
    if is_int:
        key = slice(key, key + 1)

    while len(self) < key.stop or key.stop is None:
        try:
            next(self)
        except StopIteration:
            break

    rows = self._all_rows[key]
    if is_int:
        return rows[0]
    else:
        return RecordCollection(iter(rows))
```

这里要注意 python 有很灵活的切片方法，比如 `l[1:3]` 这样的用法，使用切片时 `__getitem__` 接收的就不再是 `int` 类型而是 `slice` 类型的实例。源码对这两种情况都统一为 `slice` 做处理。

## 9. keys 和 values 数组转 dict

这里作者用了 `zip` 将 `key` 和 `value` 两个列表组合为一个 `tuple list`, 然后直接使用 `dict/OrderedDict` 的构造方法，十分简洁：

```python
def as_dict(self, ordered=False):
    """Returns the row as a dictionary, as ordered."""
    items = zip(self.keys(), self.values())

    return OrderedDict(items) if ordered else dict(items)
```

## 10.`__slots__` 属性

源码对 `Record` 类定义了 `__slots__` 属性:

```python
 __slots__ = ('_keys', '_values')
```

这里应该是为了限制 Record 类的属性被随意添加。具体可以参考这篇文章[使用`__slots__`](https://www.liaoxuefeng.com/wiki/1016959663602400/1017501655757856)

## 参考文章

[python 之 \_\_enter\_\_ 和 \_\_exit\_\_](https://blog.csdn.net/qq_37482956/article/details/100056517)

[Python 进阶：With 语句和上下文管理器 ContextManager](https://zhuanlan.zhihu.com/p/24709718)

[【Python 魔术方法】迭代器(\_\_iter\_\_和\_\_next\_\_)](https://www.jianshu.com/p/1b0686bc166d)

[【Python 魔术方法】生成器(yield 表达式)](https://www.jianshu.com/p/5ee724a8c366)

[使用`__slots__`](https://www.liaoxuefeng.com/wiki/1016959663602400/1017501655757856)
