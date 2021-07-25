---
title: fastdom 源码解析
date: 2018-02-25 20:16:21
tags: 源码解析
categories: javascript
---

## 浏览器如何渲染页面

说到 [fastdom](https://github.com/wilsonpage/fastdom)，就必须先了解浏览器渲染一个页面的流程。通常浏览器渲染页面需要如下的步骤:
![页面渲染流程图](/static/fastdom/frame.jpg)
（其中的 layout 有时候也称为 reflow）

layout 是非常消耗性能和时间的，所以应该尽量避免 js 的执行过程中频繁触发 layout 。特别是在有动画的情况下，太多的 layout 会使得浏览器的刷新频率低于 60fps，出现动画卡顿的现象。具体的原理和细节可以参考这篇文章:

[Avoid Large, Complex Layouts and Layout Thrashing](https://developers.google.com/web/fundamentals/performance/rendering/avoid-large-complex-layouts-and-layout-thrashing)

[fastdom](https://github.com/wilsonpage/fastdom) 的出现就是为了优化 layout，防止出现 forced synchronous layouts 。

<!--more-->

源码比较简单，首先 fastdom 库是一个全局单例的库:

```js
var exports = (win.fastdom = win.fastdom || new FastDom());
```

fastdom 主要通过管理单例上的 reads 和 writes 两个数组来缓存读(measure)写(mutate) dom 节点两种的操作， 因为这些操作会触发 layout。

```js
function FastDom() {
  var self = this;
  self.reads = [];
  self.writes = [];
  self.raf = raf.bind(win); // test hook
  debug("initialized", self);
}
```

然后通过 scheduleFlush 函数在下一帧(requestAnimationFrame)执行数组中的函数 — 先执行 reads 再执行 writes。

```js
// scheduleFlush
try {
  debug("flushing reads", reads.length);
  runTasks(reads);
  debug("flushing writes", writes.length);
  runTasks(writes);
} catch (e) {
  error = e;
}
```

这样所有的读写操作都被分到不同的数组中，然后异步的统一在下一帧(next frame)中执行， 从而保证了 js 执行过程中不出现 forced synchronous layouts 的现象。
