---
title: 什么是反向代理
date: 2021-2-12 07:30:20
tags: [ngix]
categories: 服务器
---

## 正向代理

首先回顾下我们最常见的代理: 正向代理。

我们常说的代理也就是指正向代理，正向代理的过程，它隐藏了真实的请求客户端，服务端不知道真实的客户端是谁，客户端请求的服务都被代理服务器代替来请求，某些科学上网工具扮演的就是典型的正向代理角色。用浏览器访问

![](https://pic1.zhimg.com/80/v2-07ededff1d415c1fa2db3fd89378eda0_720w.jpg?source=1940ef5c)

## 正向代理的实现

<!--more-->

用户希望代理服务器帮助自己，和要访问服务器通信，为了实现此目标，需要以下工作：

1. 用户 IP 报文的目的 IP = 代理服务器 IP
2. 用户报文端口号 = 代理服务器监听端口号
3. HTTP 消息里的 URL 要提供服务器的链接
4. 服务器返回网页
5. 代理服务器打包 4 中的网页，返回用户。

其中 2 里代理服务器可以根据 3 里的链接与服务器直接通信

## 反向代理

反向代理则正好相反。反向代理隐藏了真实的服务端，当我们请求 ww.baidu.com 的时候，就像拨打 10086 一样，背后可能有成千上万台服务器为我们服务，但具体是哪一台，你不知道，也不需要知道，你只需要知道反向代理服务器是谁就好了，www.baidu.com 就是我们的反向代理服务器，反向代理服务器会帮我们把请求转发到真实的服务器那里去。Nginx 就是性能非常好的反向代理服务器，用来做负载均衡。

![](https://pic2.zhimg.com/80/v2-816f7595d80b7ef36bf958764a873cba_720w.jpg?source=1940ef5c)

## 为什么要反向代理

在计算机世界里，由于单个服务器的处理客户端（用户）请求能力有一个极限，当用户的接入请求蜂拥而入时，会造成服务器忙不过来的局面，可以使用多个服务器来共同分担成千上万的用户请求，这些服务器提供相同的服务，对于用户来说，根本感觉不到任何差别。

![](https://pic1.zhimg.com/80/v2-3b4274d49d3babd1cc2ba521b72892aa_720w.jpg?source=1940ef5c)

## 反向代理的实现

1. 需要有一个负载均衡设备来分发用户请求，将用户请求分发到空闲的服务器上
2. 服务器返回自己的服务到负载均衡设备
3. 负载均衡将服务器的服务返回用户

以上的潜台词是：用户和负载均衡设备直接通信，也意味着用户做服务器域名解析时，解析得到的 IP 其实是负载均衡的 IP，而不是服务器的 IP，这样有一个好处是，当新加入/移走服务器时，仅仅需要修改负载均衡的服务器列表，而不会影响现有的服务。

## 总结

两者的区别在于代理的对象不一样：正向代理代理的对象是客户端，反向代理代理的对象是服务端
