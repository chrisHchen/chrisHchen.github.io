---
title: Z 字形变换
date: 2020-3-08 12:30:00
tags: [算法, 力扣, python]
categories: 算法
---

## 题目
这是 leetcode 上一道难度为中等的算法题：

将一个给定字符串 s 根据给定的行数 numRows ，以从上往下、从左到右进行 Z 字形排列。
比如输入字符串为 "ABCDEFGHIJKLMN" 行数为 3 时，排列如下：

```text
A   E   I   M
B D F H J L N
C   G   K
```

而输出需要从左往右逐行读取，产生出一个新的字符串："AEIMBDFHJINCGK"。

## 思路

有很大一部分算法题的思路都源于找到其中的**规律**。

输入字符串 s 经过转换后有 numRows 行，如果我们遍历 s 的每个字符 c 会发现，c 的行序列总是从 0 开始增长到 numRows - 1, 然后又从 numRows - 1 回到 0，比如上面的例子：
<!--more-->
```text
字符   index
 A      0
 B      1
 C      2
 D      1
 E      0
 ....
```

所以我的思路就是通过遍历 S, 然后按字符 C 的 index 序列，分别添加到 <code>row[i]</code> 中，然后把 row 的每个元素都 join 起来得到输出。

具体代码如下：

```python
class Solution:
    def convert(self, s: str, numRows: int) -> str:
      length = len(s)
      row = ["" for _ in range(length)]
      i = 0
      flag = -1
      if length < 2: 
          return s
      for c in s:
        row[i] += c
        if i == numRows - 1 or i == 0:
          flag = -flag
        i = i + flag
      return "".join(row)
```