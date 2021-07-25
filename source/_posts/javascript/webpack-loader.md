---
title: 写一个 webpack loader
date: 2018-04-24 23:05:50
tags: webpack
categories: javascript
---

前几天看了 webpack 的官网介绍 [write a loader](https://webpack.js.org/contribute/writing-a-loader/) 的文档，觉得挺有意思，于是打算自己实践一下。

**什么是 loader**

官网的介绍很直接明了：
<code>
[A loader is a node module that exports a function. This function is called when a resource should be transformed by this loader. The given function will have access to the Loader API using the this context provided to it](https://webpack.js.org/contribute/writing-a-loader/)
</code>

首先 loader 是一个 nodejs 的模块，然后这个模块需要 exports 一个 function。这个 function 可以通过 this 上下文获得 [Loader API](https://webpack.js.org/api/loaders/) 上的数据。

**sync/async loader**

sync loader 可以直接返回转义后的 js 字符串。async loader 需要调用 this.async() 来指明需要等待一个异步的结果，this.async() 返回 this.callback 函数，之后 async loader 必须 return undefined 并通过 callback 来返回转义后的 js。

<!--more-->

例子：

```js
export default function (source) {
  var callback = this.async();
  fetch().then(() => {
    callback(null, `export default ${source}`);
  });
}
```

**链式调用**

loader 是可以链式调用的。调用的顺序是逆序调用，也就是最后的 loader 先执行，最前的 loader 最后执行。最后的 loader 会接收源代码内容作为参数，其他 load 都接收前一个 loader 的返回值作为参数。最前的 loader 执行后返回一个 js 字符串做为最终的返回结果。

**一个简单的例子**

假如要写 2 个 js 的 loader, 第一个添加作者信息。另一个再每个 <code>console.log</code> 前加一句 <code>console.log(Date.now())</code>

- comment-loader: 在代码前加一个作者的注释
- logtime-loader: 在每个 console.log 语句前面加一个 console.log(Date.now())

_webpack.config.js_

```js
export default {
  entry: path.resolve(__dirname, "index.js"),
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "bundle.js",
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /(node_modules|bower_components)/,
        use: [
          {
            loader: path.resolve(__dirname, "./src/logtime-loader.js"),
          },
          {
            loader: "babel-loader",
          },
          {
            loader: path.resolve(__dirname, "./src/comment-loader.js"),
            options: {
              name: "Chris",
            },
          },
        ],
      },
    ],
  },
};
```

注意配置文件里的 <code>comment-loader</code> 带有 options。待会会用 loader-utils 来获取这个参数作为作者的名字。

_src/comment-loader.js_ 是一个 sync loader，所以直接返回代码字符串。

```js
import { getOptions } from "loader-utils";

export default function (source) {
  const options = getOptions(this);
  return `/*author:${options.name}*/\n${source}`;
}
```

_src/logtime-loader.js_

```js
export default function (source) {
  const re = /console\.log\([\w\W]*?\)/gm;
  const newSource = source.replace(re, function (matched) {
    return `console.log(Date.now())\n  ${matched}`;
  });
  return newSource;
}
```

假设 loader 将要对 _index.js_ 的代码进行处理，index.js 代码如下:

```js
const test = function () {
  let a = 0,
    i = 100;
  console.log("start loop");
  while (i) {
    a = a + i;
    i--;
  }
  console.log("end loop");
  return a;
};
```

执行 webpack 命令后在 dist 目录下生成了 bundle.js 文件。可以在 bundle.js 中看到转义后的 js 代码如下:

![](/static/webpack-loader/loader.png)

除了 webpack 添加的部分模块转换代码之外，可以看到注释已经被添加进去，而且原本出现 console.log() 的地方也加上了 console.log(Date.now())。

这是一个最基本的例子，更多的用法可以参照 [loader 的文档](https://webpack.js.org/contribute/writing-a-loader/)来进行尝试。另外，如果在要对正在开发中的 loader 做测试，且 loader 已经单独建库了，那么可以使用 [npm link](https://docs.npmjs.com/cli/v7/commands/npm-link) 把仓库 link 到需要使用 loader 的项目。
