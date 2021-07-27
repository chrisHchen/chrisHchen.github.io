---
title: momoize-one 源码解析
date: 2018-05-20 23:13:01
tags: 源码解析
---

[momoize-one](https://github.com/alexreardon/memoize-one) 是一个 javascript 记忆库。它能根据函数的参数来缓存函数运算的结果。momoize-one 和其他 js 记忆库相比的不同之处在于它只会缓存函数**最近一次**入参对应的执行结果，所以内存溢出的风险较小。

## Usage

memoize-one 的 api 非常简便，模块只 export 唯一一个 api： <code>memoizeOne</code>。先看下 memoize-one 如何使用：

<!--more-->

```js
// memoize-one uses the default import
import memoizeOne from "memoize-one";

const add = (a, b) => a + b;
const memoizedAdd = memoizeOne(add);

memoizedAdd(1, 2); // 3

memoizedAdd(1, 2); // 3
// Add function is not executed: previous result is returned

memoizedAdd(2, 3); // 5
// Add function is called to get new value

memoizedAdd(2, 3); // 5
// Add function is not executed: previous result is returned

memoizedAdd(1, 2); // 3
// Add function is called to get new value.
// While this was previously cached,
// it is not the latest so the cached result is lost
```

## 源码

memoize-one 的源码非常精简，这也是为什么它 gzip 后只有 355b 的原因，最主要的逻辑都在这个函数里：

```js
function memoizeOne(resultFn, isEqual) {
  if (isEqual === void 0) {
    isEqual = areInputsEqual;
  }
  var lastThis;
  var lastArgs = [];
  var lastResult;
  var calledOnce = false;
  function memoized() {
    var newArgs = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      newArgs[_i] = arguments[_i];
    }
    if (calledOnce && lastThis === this && isEqual(newArgs, lastArgs)) {
      return lastResult;
    }
    lastResult = resultFn.apply(this, newArgs);
    calledOnce = true;
    lastThis = this;
    lastArgs = newArgs;
    return lastResult;
  }
  return memoized;
}

module.exports = memoizeOne;
```

这里很好的利用了 javascript **闭包**的能力：<code>memoized</code>函数内部使用了函数作用域外的变量，然后返回了 <code>memoized</code> 函数。所以只要函数的指针依然存在，则函数作用域外部的变量不会被垃圾回收。

调用 <code>memoizeOne</code> 后返回一个 memoized 函数, memoized 执行时会先做如下判断:

- 函数是否被调用过
- this 上下文是否和上次一致
- 参数是否和上次一致

如果三个比较的结果都是 true，则返回上次执行的结果，反之，则执行原函数，并缓存参数列表，this 指向和执行结果，供下次执行时做对比。

总体而且逻辑是非常清晰的。另外，用来判断 <code>isEqual</code> 的函数也可以自定义，如果不传，则使用默认的<code>areInputsEqual</code>函数。
