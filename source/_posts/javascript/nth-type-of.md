---
title: nth-type-of 和 nth-child 的区别
date: 2018-06-25 10:16:01
tags: css
categories: css
---

## CSS 伪类选择器

本文将用代码例子的形式展示以下几个比较容易混淆的 css 伪类选择器的使用:

- p:first-of-type 选择属于其父元素的首个元素
- p:last-of-type 选择属于其父元素的最后元素
- p:only-of-type 选择属于其父元素唯一的元素
- p:only-child 选择属于其父元素的唯一子元素
- p:nth-type-of(n) 选择属于其父元素的第 n 个 p 元素
- p:nth-child(n) 选择属于其父元素的第 n 个子元素

点击[这里](https://jsbin.com/govuputire/edit?html,output)查看本文提到的例子.

使用到的 html 片段如下：

<!--more-->

```html
<body>
  <div>
    <p>1st paragraph</p>
    <h3>2nd paragraph</h3>
    <p>3rd paragraph</p>
    <p>4th paragraph</p>
    <p>5th paragraph</p>
    <p>6th paragraph</p>
    <p>7th paragraph</p>
    <p>8st paragraph</p>
  </div>

  <hr />

  <div class="my">
    <p>only paragraph</p>
  </div>
</body>
```

## first-of-type

```css
p:first-of-type {
  color: red;
}
```

结果如下，p:first-of-type 选择属于其父元素的首个 p 元素。这里有 2 个 p 元素分别在各自的 div 父元素内部位于第一个，所以选择器选中了两个。
![](./static/nth-type-of/first-of-type.jpg)

## last-of-type

```css
p:last-of-type {
  color: red;
}
```

last-of-type 和 first-of-type 对应，选择属于其父元素的最后一个 p 元素

![](./static/nth-type-of/last-of-type.jpg)

## only-of-type

```css
h3:only-of-type {
  color: red;
}
```

x:only-of-type 选择属于其父元素唯一的 x 类型元素, 可以和下面的 only-child 对比，区别在于 only-child 限制更加强，必须是唯一子元素。

![](./static/nth-type-of/only-of-type.jpg)

## only-child

```css
h3:only-child {
  color: orange;
}
p:only-child {
  color: orange;
}
```

only-child 限制更加强，必须是唯一子元素。可以看到由于第一个 div 里不止一个 p 元素，所以没有 p 元素被选中，同样因为 h3 也不是第一个 div 里唯一的子元素，所以也没有被选中。

![](./static/nth-type-of/only-child.jpg)

## nth-type-of(n)

```css
p:nth-of-type(2n + 1) {
  color: red;
}
```

可以看到 nth-type-of 选择器会忽略非选择的 type，比如这里的 h3,然后只对 p 做排序，选中奇数序列的元素

![](./static/nth-type-of/nth-type-of.jpg)

## nth-child(n)

```css
p:nth-of-type(2n + 1) {
  color: red;
}
```

和上面的 nth-type-of 相比, nth-child 不作元素类型的区别，只要是子元素都计入排序。

![](./static/nth-type-of/nth-child.jpg)
