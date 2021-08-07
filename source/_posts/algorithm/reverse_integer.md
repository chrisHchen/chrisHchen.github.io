---
title: 整数反转
date: 2020-7-08 12:30:00
tags: [算法, 力扣, python]
categories: 算法
---

## 题目
这是 leetcode 上一道难度为简单的算法题：

给你一个 32 位的有符号整数 x ，返回将 x 中的数字部分反转后的结果。
如果反转后整数超过 32 位的有符号整数的范围 <code>[−2<sup>31</sup>,  2<sup>31</sup> − 1] </code>，就返回 0。

虽然是一个简单题，但如果你对 python 的负数取余和整数除法不熟悉的话，很容易踩坑🙂。
<!--more-->
## 思路
这题的思路并不难，利用取余数和整数除法可以很快得到思路，假如给出的数字是 1357:

```text
第一次循环
1357 % 10 = 7
1357 // 10 = 135
第二次循环
135 % 10 = 5
135 // 10 = 13
第三次循环
13 % 10 = 3
13 // 10 = 1
第四次循环
3 % 10 = 3
3 // 10 = 0
```
如果这题使用 java 来写，基本这样的思路就可以写出来了，但这里我用的是 python。
python 取余数和整数除法这两个运算在遇到负数的时候，结果会和 java 不一样。python 的负数取余总是会让**商尽可能的小**。

举个🌰：比如 -123 % 10，商为 -12 时，余数 -3， 商为 -13 时，余数是 7。python 会返回其中使得商小的结果，因为 - 13 \< -12, 所以返回 7，但实际上我们想要返回 -3。

那有什么办法呢，这里可以让除数为 -10，这样商 12 和 13 两个结果 python 会取 12,因为 12 \< 13 ，返回的余数就是 -3 了。

python 的整数除法也是一样的。对 python 的这个逻辑更加具体的解释可以看[这篇文章](https://blog.csdn.net/weixin_33773996/article/details/112699336)

所以 python 版的算法逻辑如下:

```python
class Solution:
    def reverse(self, x: int) -> int:
      res = 0
      # 根据 x 来选择除数
      devider = 10 if x >= 0 else -10
      while x != 0:
        temp = x % devider
        if res > 214748364 or (res==214748364 and temp > 7):
          return 0
        if res < -214748364 or (res==-214748364 and temp<-8):
          return 0
        res = res * 10 + temp
        # 根据 x 来调整整数除法的正负号
        x = x // devider if x > 0 else -(x // devider)

      return res
```