---
title: webpack loader vs plugin
date: 2020-05-11 20:05:50
tags: webpack
categories: javascript
---

## 前言

webpack 配置文件中最常见同时也是配置最繁琐的就是 loader 和 plugin。本文是我个人对 loader 和 plugin 理解的总结。可能有不准确的地方，后续会再次修改。

## 什么是 Loader ?

Loader 翻译过来可以叫**加载器**。官方文档对 loader 的[解释原文](https://webpack.js.org/concepts/#loaders)如下:

<blockquote style='font-size:12px;text-align:left'>
Out of the box, webpack only understands JavaScript and JSON files. Loaders allow webpack to process other types of files and convert them into valid modules that can be consumed by your application and added to the dependency graph.

Loaders are transformations that are applied to the source code of a module. They allow you to pre-process files as you import or “load” them. Thus, loaders are kind of like “tasks” in other build tools and provide a powerful way to handle front-end build steps. Loaders can transform files from a different language (like TypeScript) to JavaScript or load inline images as data URLs. Loaders even allow you to do things like import CSS files directly from your JavaScript modules!

</blockquote>

**loader 是一个转换器，将 A 文件进行编译成 B 文件，属于单纯的文件转换过程**；

我总结为如下几点：

1. loader 需要处理的是除了 js 和 json 之外的文件类型。
2. loader 将这类文件转换(transform)为应用可以消费的合法模块。

第一点很好理解。第二点就有点抽象了，什么是“应用可以消费的合法模块”呢？
<!--more-->
这里首先要了解 webpack 中**模块**的概念。本质上，任意的文件在 webpack 中都可以认为是一个模块。但有些模块是 webpack 原生就支持的，比如 js 文件，有些则需要通过特定的 loader 处理后才能被 webpack 打包。其中 webpack 原生支持的模块如下：

- ECMAScript modules(用 import 加载的模块)
- CommonJS modules(用 require 加载的模块)
- AMD modules（用 define 加载的模块，现在基本很少使用了）
- Assets
- WebAssembly modules

其中 <code>Assets</code> 类型的包括 fonts, icons, txt，etc。在 webpack 5 之前是需要额外使用

- <code>raw-loader(以 string 形式加载文件内容)</code>,
- <code>url-loader(以内联 data URI 的形式加载文件)</code>,
- <code>file-loader(将文件放到 output 目录，并以 path 加载文件) 来处理的</code>。

webpack 5 已经原生支持 <code>Asset Modules </code>，所以不需要再使用以上的 loader 了。

总结而言对于原生支持的文件类型，webpack 可以自己分析依赖并打包，对于不支持的文件类型，需要使用特定的 loader 来告诉 webpack 文件的依赖关系和如何打包。

所以从 loader 的配置也可以看出，必须指定 <code>test</code> 和 <code>use</code>：
<code>test</code>指定文件类型，<code>use</code>指定使用什么 loader 来处理。

```js
const path = require("path");

module.exports = {
  output: {
    filename: "my-first-webpack.bundle.js",
  },
  module: {
    rules: [{ test: /\.txt$/, use: "raw-loader" }],
  },
};
```

这里要注意 loader 是配置在 <code>module.rules</code> 下面，而不是 <code>rules</code>

## 例子

看一个简单的例子 [raw-loader](https://github.com/webpack-contrib/raw-loader/blob/master/src/index.js)：

```js
import { getOptions } from "loader-utils";
import { validate } from "schema-utils";

import schema from "./options.json";

export default function rawLoader(source) {
  const options = getOptions(this);

  validate(schema, options, {
    name: "Raw Loader",
    baseDataPath: "options",
  });

  const json = JSON.stringify(source)
    .replace(/\u2028/g, "\\u2028")
    .replace(/\u2029/g, "\\u2029");

  const esModule =
    typeof options.esModule !== "undefined" ? options.esModule : true;

  return `${esModule ? "export default" : "module.exports ="} ${json};`;
}
```

函数签名是 <code>(source: string) => string</code>
可见 loader 首先是一个 function， function 内部会对源码 source 进行处理，这里的 raw-loader 主要是对元数据使用 json.stringify 做序列化。最后输出 js 源码字符串。

## 什么是 plugins?

<blockquote style='font-size:12px;text-align:left'>
While loaders are used to transform certain types of modules, plugins can be leveraged to perform a wider range of tasks like bundle optimization, asset management and injection of environment variables.

Plugins are the backbone of webpack. webpack itself is built on the same plugin system that you use in your webpack configuration!
They also serve the purpose of doing anything else that a loader cannot do.

</blockquote>

**plugin 是一个扩展器，它丰富了 webpack 本身，webpack 本身就是建立在插件系统上的，plugin 针对是 loader 结束后，webpack 打包的整个过程，它并不直接操作文件，而是基于事件机制工作，会监听 webpack 打包过程中的某些节点，执行广泛的任务。**

plugin 需要 require 进来。另外，plugin 可能会被使用多次，所以需要用 <code>new</code> 关键字实例化

```js
const HtmlWebpackPlugin = require("html-webpack-plugin"); //installed via npm
const webpack = require("webpack"); //to access built-in plugins

module.exports = {
  module: {
    rules: [{ test: /\.txt$/, use: "raw-loader" }],
  },
  plugins: [new HtmlWebpackPlugin({ template: "./src/index.html" })],
};
```

plugin 是一个包含 <code>apply</code> 方法的 js 对象：

```js
const pluginName = "ConsoleLogOnBuildWebpackPlugin";

class ConsoleLogOnBuildWebpackPlugin {
  apply(compiler) {
    compiler.hooks.run.tap(pluginName, compilation => {
      console.log("The webpack build process is starting!!!");
    });
  }
}

module.exports = ConsoleLogOnBuildWebpackPlugin;
```

## Tapable

webpack 中有很多对象都继承自 [Tapable](https://github.com/webpack/tapable#tapable) 类，该类暴露了 <code>tap</code>,<code>tapAsync</code>,<code>tapPromise</code> 三个函数供 plugins 来注入特定的构建流程。

## 参考文章

[webpack doc about loaders](https://webpack.js.org/concepts/#loaders)
[Plugin API](https://webpack.js.org/api/plugins/)
