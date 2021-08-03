---
title: Service-worker 使用案例
date: 2019-1-05 10:30:00
tags: service-worker
categories: javascript
---

这篇文章将简单的实现一个 service-worker 的 demo

## 生命周期

首先熟悉一下 service worker 首次被安装后的生命周期：

![life cycle](./static/Service-worker/sw-lifecycle.png)

## HTTPS

service worker 只能部署在 HTTPS 的服务器上。因为它本身可以劫持请求并对请求返回的内容做修改，所以为了防止中间人攻击，保证浏览器收到的 service worker 没有被修改过，service worker 只能注册在部署于 HTTPS 服务器的页面上。但在开发阶段，是可以使用 localhost 的。

<!--more-->

## 注册

```js
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("/sw.js").then(
      function (registration) {
        // Registration was successful
        console.log(
          "ServiceWorker registration successful with scope: ",
          registration.scope
        );
      },
      function (err) {
        // registration failed :(
        console.log("ServiceWorker registration failed: ", err);
      }
    );
  });
}
```

以上代码会在页面加载完成后注册名称为 sw.js 的 service worker。**<code>register</code> 方法在每次页面加载时都会执行，浏览器自己会区分是否是新注册的**

<blockquote>
So once there's an active service worker, it doesn't matter when you call navigator.serviceWorker.register(), or in fact, whether you call it at all. Unless you change the URL of the service worker script, navigator.serviceWorker.register() is effectively a no-op during subsequent visits. When it's called is irrelevant.
</blockquote>

至于为什么要在 <code>[loaded](https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onload)</code> 事件里注册 service worker，可以在[这篇文章](https://developers.google.com/web/fundamentals/primers/service-workers/registration)找答案。

<code>load</code> 事件定义：

<blockquote>
The load event fires at the end of the document loading process. At this point, all of the objects in the document are in the DOM, and all the images, scripts, links and sub-frames have finished loading.
</blockquote>

另外需要注意的是 sw.js 所在的域(domain)。例子中是处于根目录，所以 sw.js 可以处理整个域名 origin 的请求。假如我们注册的 sw 是在 <code>/abc/sw.js</code>，那么他只能处理 <code>/abc/</code> 域下页面发出的请求(eg: <code>/abc/page1</code>, <code>/abc/page2</code>)

## 隐身窗口

在隐身窗口中打开的页面中注册的 service worker ，包括其缓存，会在页面关闭时自动清除。所以在开发和调试阶段，为了保证之前的 service worker 不会影响当前的环境。可以使用隐身窗口。

## 查看

我们可以在 chrome 浏览器的 <code>chrome://inspect/#service-workers</code> 位置查看 service worker，如果要看具体的生命周期状态，也可以看 <code>chrome://serviceworker-internals</code>

## 安装

<code>Install</code> 事件是在 service worker 内监听并实现其逻辑的:

```js
var CACHE_NAME = "my-site-cache-v1";
var urlsToCache = ["/", "/styles/main.css", "/script/main.js"];

self.addEventListener("install", function () {
  // Perform install steps
  event.waitUntil(
    // Open a cache.
    caches.open(CACHE_NAME).then(function (cache) {
      console.log("Opened cache");
      // Cache our files.
      return cache.addAll(urlsToCache);
    })
  );
});
```

<code>event.waitUntil()</code> 函数接受一个 promise 入参。如果所有文件列表里的文件都成功缓存，则 service worker 安装成功。相反，如果其中一个文件缓存失败，则整个 service worker 就会安装失败。

<code>Install</code> 回调函数内也可以执行别的逻辑，不一定要缓存资源，甚至可以不提供 install 的回调。

## 缓存并返回请求

```js
self.addEventListener("fetch", function (event) {
  event.respondWith(
    caches.match(event.request).then(function (response) {
      // Cache hit - return response
      if (response) {
        return response;
      }
      return fetch(event.request);
    })
  );
});
```

<code>event.respondWith()</code> 函数也接受一个 promise 入参，首先查找是否命中缓存，如果命中则返回缓存内容，否则发起网络请求并返回请求数据。上面这个简单的例子展现的如何使用 install 过程中缓存的数据，但如果要累积的缓存新请求的话，需要修改一下代码：

```js
self.addEventListener("fetch", function (event) {
  event.respondWith(
    caches.match(event.request).then(function (response) {
      // Cache hit - return response
      if (response) {
        return response;
      }

      return fetch(event.request).then(function (response) {
        // Check if we received a valid response
        // Make sure the response type is basic, which indicates that it's a request from our origin.
        // This means that requests to third party assets aren't cached as well.
        if (!response || response.status !== 200 || response.type !== "basic") {
          return response;
        }

        // IMPORTANT: Clone the response. A response is a stream
        // and because we want the browser to consume the response
        // as well as the cache consuming the response, we need
        // to clone it so we have two streams.
        var responseToCache = response.clone();

        caches.open(CACHE_NAME).then(function (cache) {
          cache.put(event.request, responseToCache);
        });

        return response;
      });
    })
  );
});
```

## 更新 service worker

更新分以下几步：

1. 手动更新 sw.js 的内容。当用户的浏览器再次打开页面，重新下载 sw.js 时，浏览器会自动发现下载的 sw.js 和之前的差异，只要内容稍有不同，浏览器就会认为是新的。
2. 新的 service worker 会启动，并触发 <code>install</code> 事件
3. 到这一步为止，旧的 sw 依然控制着页面，所以新的 sw 会进入 <code>waiting</code> 的状态
4. 当所有的页面被关闭时，旧的 sw 会被 killed，新的 sw 会接替控制权
5. 新 sw 获得控制权后，<code>activate</code> 事件会被触发

<code>activate</code> 事件回调中通常会清除旧 sw 的缓存。假设旧的 sw 有一个缓存为 <code>my-site-cache-v1</code>, 当新 sw 的 <code>install</code>
事件触发时，我们创建了两个新的缓存 <code>pages-cache-v1</code> 和 <code>blog-cache-v1</code>，然后在 <code>activate</code> 事件中删掉 <code>my-site-cache-v1</code> 的缓存。

```js
self.addEventListener("activate", function (event) {
  var cacheAllowlist = ["pages-cache-v1", "blog-posts-cache-v1"];

  event.waitUntil(
    caches.keys().then(function (cacheNames) {
      return Promise.all(
        cacheNames.map(function (cacheName) {
          if (cacheAllowlist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
```

## FAQ

fetch 默认不发送 credentials, 比如 cookies

```js
fetch(url, {
  credentials: "include",
});
```

<blockquote>
This behaviour is on purpose, and is arguably better than XHR's more complex default of sending credentials if the URL is same-origin, but omitting them otherwise. Fetch's behaviour is more like other CORS requests, such as <img crossorigin>, which never sends cookies unless you opt-in with <img crossorigin="use-credentials">.
</blockquote>

## 参考文章

[Service Workers: an Introduction](https://developers.google.com/web/fundamentals/primers/service-workers)
