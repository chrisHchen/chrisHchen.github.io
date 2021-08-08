---
title: 字符串转换整数 (atoi)
date: 2020-8-20 11:30:00
tags: [算法, 力扣, python]
categories: 算法
---

## 题目
请你来实现一个 myAtoi(string s) 函数，使其能将字符串转换成一个 32 位有符号整数（类似 C/C++ 中的 atoi 函数）。

函数 myAtoi(string s) 的算法如下：

读入字符串并丢弃无用的前导空格

检查下一个字符（假设还未到字符末尾）为正还是负号，读取该字符（如果有）。 确定最终结果是负数还是正数。 如果两者都不存在，则假定结果为正。

读入下一个字符，直到到达下一个非数字字符或到达输入的结尾。字符串的其余部分将被忽略。

将前面步骤读入的这些数字转换为整数（即，"123" -> 123， "0032" -> 32）。如果没有读入数字，则整数为 0 。必要时更改符号（从步骤 2 开始）。

如果整数数超过 32 位有符号整数范围 [−231,  231 − 1] ，需要截断这个整数，使其保持在这个范围内。具体来说，小于 −2<sup>31</sup> 的整数应该被固定为 −2<sup>31</sup> ，大于 2<sup>31</sup> − 1 的整数应该被固定为 2<sup>31</sup> − 1 。

返回整数作为最终结果。
<!--more-->
**注意：**
本题中的空白字符只包括空格字符 ' ' 。
除前导空格或数字后的其余字符串外，请勿忽略 任何其他字符。

## 思路
- 循环字符串 s 的每个字符 c
- 如果 c 是 + 或 -。则认为是数字符号
- 如果 c 是数字，则 <code>result = result * 10 + c</code>。这里判断数字可以用<code> isdigit </code>方法 或者正表达式
- 如果 c 是非数字，则结束，返回 result

python 版本的实现如下：
```python
import re

class Solution:
    def myAtoi(self, s: str) -> int:
      # 去除左侧的空格
      s = s.lstrip()
      # 长度为 0，则直接返回
      if len(s) == 0:
        return 0
      mark = '+'
      result = 0
      max = 2**31 -1
      min = -2**31
      if s[0] == '+' or s[0] == '-':
        mark = s[0]
        s = s[1:]
      for i in s:
        # if i.isdigit():
        if re.match('\d', i):
          result = result * 10 + int(i)
        else:
          break
        if mark == '+' and result > max:
          return max
        if mark == '-' and -result < min:
          return min
      return result if mark == '+' else -result
```