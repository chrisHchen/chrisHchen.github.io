---
title: Web Worker vs Service Worker
date: 2019-1-04 19:32:00
tags: service-worker
categories: javascript
---

## 前言

web worker 和 service worker 都属于 **"JavaScript Workers"**。虽然工作方式很类似，但应用场景却差别很大。

## 什么是 worker

通常来说，一个 worker 是一个 **和主线程隔离的单独线程里的 javascript 脚本**。
在 html 里用 \<script\> 标签加载的 js 脚本都是在主线程里加载的。如果主线程的活动很频繁，比如有密集的计算，就会拖慢整个 web 页面甚至使得页面没有响应。

## Web workers

Web workers 是最常见的一种 worker，它可以用来处理任何不想占主线程资源的繁重任务，比如密集计算等，并且可以和主线程并行执行。

Web workers 通过 postMessge 来和主线程通信：

<!--more-->

![web-worker 和主线程的通信](https://bitsofco.de/content/images/2018/11/web-worker.jpg)

Web work 需要通过 Web Worker API 来创建，同时需要创建单独的 js 文件：

```js
/* main.js */

const myWorker = new Worker("worker.js");
```

现实中对 web worker 应用较好的 🌰 是[squoosh](https://squoosh.app/) 这个 web app, 它在 worker 线程来执行图片处理任务，保证主线程不会阻塞 UI 交互。
Web work 和其他 worker 一样，也不能操作 DOM，所以相关的数据都需要通过 postMessage 来通信：

```js
/* main.js */

// create worker
const myWorker = new Worker("worker.js");

// send message to worker
myWorker.postMessage("Hello!");

// receive message from worker
myWorker.onmessage = function (e) {
  console.log(e.data);
};
```

在 web worker 的代码中，我们可以监听主线程发来的信息，并且做相应的数据交互：

```js
/* worker.js */

// Receive message from main file
self.onmessage = function (e) {
  console.log(e.data);
  // Send message to main file
  self.postMessage(workerResult);
};
```

## Service workers

Service worker 有很明确的应用场景：作为浏览器和网络/缓存的代理。

![Service worker](https://bitsofco.de/content/images/2018/11/service-worker.jpg)

Service worker 也是在主线程注册，并需要单独创建 js 文件。

```js
/* main.js */

navigator.serviceWorker.register("/service-worker.js");
```

Service worker 安装(install)并激活(activate)后, service worker 可以拦截主线程的网络请求。

```js
self.addEventListener("install", function (event) {
  //...
});
self.addEventListener("activate", function (event) {
  //...
});
self.addEventListener("fetch", function (event) {
  //...
});
```

拦截到请求后，service worker 可以选择某种策略，比如从缓存返回数据，实现应用的离线化。

```js
self.addEventListener("fetch", function (event) {
  event.respondWith(catches.match(event.request));
});
```

## 总结

**Web workers** 的用途主要作用是把原本需要主线程执行的计算密集型的任务放到独立的 worker 线程执行，使得主线程可以继续相应 UI 交互

**Service workers** 的用途主要是作为浏览器和网络请求的代理，通过缓存返回策略来实现离线化。

## 参考文章

[Web workers vs Service workers vs Worklets](https://bitsofco.de/web-workers-vs-service-workers-vs-worklets/)
