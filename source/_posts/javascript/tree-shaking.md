---
title: 简析 Tree-Shaking
date: 2018-08-25 10:16:01
tags: [javascript, webpack]
categories: javascript
---

## tree-shaking 解决的问题

web 端 js 代码正在朝着越来越复杂的方向发展，代码体积也越来越大，于是出现了代码模块化的概念。
但随之也产生了一些问题，比如最终打包的文件会包含一些实际上用不到的代码。Tree Shaking 是一种通过消除最终文件中未使用的代码来优化体积的方法。

官方有标准的说法：Tree-shaking 的本质是消除无用的 js 代码。无用代码消除广泛存在于传统的编程语言编译器中，编译器可以判断出某些代码根本不影响输出，然后消除这些代码，这个称之为 DCE（dead code elimination）

先举个 🌰，比如有个 <code>util.js</code> 库如下：

<!--more-->

```js
export function add(a, b) {
  return a + b;
}

export function minus(a, b) {
  return a - b;
}
```

假设我们项目的打包入口 <code>index.js</code> 如下：

```js
import { add } from "./util";

add(1, 1);
```

如果我们用 webpack 打包，最终输出的文件会包含 minus 函数的代码，但实际上我们的项目中并没有用到。

## 静态加载 vs 动态加载

在 ES6 模块规范之前，我们使用 require() 语法的 CommonJS 模块规范。这些模块是 dynamic 动态加载的，这意味着我们可以根据代码中的条件导入新模块。

```js
var myModule;

if (condition) {
  myModule = require("foo");
} else {
  myModule = require("bar");
}
```

这种 dynamic 的语法规范无法应用 Tree Shaking，因为在实际运行代码之前无法确定需要哪些模块。

而在 ES6 中，引入了模块的新语法，这是 static 的。使用 import 语法，我们不再能够动态导入模块。

下面的代码是错误的 ❎

```js
if (condition) {
  import foo from "foo";
} else {
  import bar from "bar";
}
```

有了这种新语法还就可以有效地进行 Tree Shaking，因为这种语法确定导入后使用的任何代码，而无需先运行这些代码。
有了 ES6 的 import 语法，对上面的例子而言，最终打包的代码就可以去掉未使用的 minus 函数了。

(另外既然说到静态和动态，顺便可以区分一下动态语言和静态语言 🙂

静态类型语言 如果在编译时知道变量的类型，则该语言是静态类型的。我们经常说道的 Java、C、C++在写代码的时候必须指定每个变量的类型。 优点就是编译器可以执行各种检查，也就是程序还没跑起来就能找到一些小错误，也就是是在 compile-time 检查出错误的。
动态类型语言 一般是脚本语言，比如说 Perl、Ruby、Python、PHP、JavaScript，可以更快地编写代码，不必每次都指定类型，做 type checking 是在 run-time 的时候去做的。优点是可能代码开发快，但是维护难)

## 副作用

一个副作用是：有一些代码，是在 import 时执行了一些行为，这些行为不一定和任何导出相关。例如 polyfill ，Polyfills 通常是在项目中全局引用，而不是在 index.js 中使用导入的方式引用。

Tree Shaking 并不能自动判断哪些脚本是副作用，因此手动指定它们非常重要。

## 如何使用

Tree Shaking 通常是和打包工具配合使用，例如 Webpack，只需在配置文件中设置 mode 即可。

```js
module.exports = {
    ...,
    mode: "production",
    ...,
};
```

要将某些文件标记为副作用，我们需要将它们添加到 package.json 文件中。

```js
{
    ...,
    "sideEffects": [
        "./src/polyfill.js"
    ],
    ...,
}
```

[【参考】](https://zhuanlan.zhihu.com/p/127804516)
