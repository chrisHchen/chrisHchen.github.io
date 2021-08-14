---
title: 正则表达式匹配
date: 2021-1-20 10:32:00
tags: [算法, 力扣]
categories: 算法
---

## 题目

给你一个字符串  s  和一个字符规律  p，请你来实现一个支持 '.'  和  '\*'  的正则表达式匹配。

'.' 匹配任意单个字符
'\*' 匹配零个或多个前面的那一个元素
所谓匹配，是要涵盖   整个   字符串  s 的，而不是部分字符串。

## 思路

首先状态 dp 一定能自己想出来。
dp[i][j] 表示 s 的前 i 个是否能被 p 的前 j 个匹配

1. 如果 p.charAt(j) == s.charAt(i) : dp[i][j] = dp[i-1][j-1]；

2. 如果 p.charAt(j) == '.' : dp[i][j] = dp[i-1][j-1]；

3. 如果 p.charAt(j) == '\*'：

   - 如果 p.charAt(j-1) != s.charAt(i) : dp[i][j] = dp[i][j-2] // in this case, a\* only counts as empty
   - 如果 p.charAt(j-1) == s.charAt(i) or p.charAt(i-1) == '.'：
     - dp[i][j] = dp[i-1][j] //in this case, a\* counts as multiple a
     - or dp[i][j] = dp[i][j-1] // in this case, a\* counts as single a
     - or dp[i][j] = dp[i][j-2] // in this case, a\* counts as empty

<!--more-->

## 最终代码

```python

class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        if not p: return not s
        if not s and len(p) == 1: return False

        nrow = len(s) + 1
        ncol = len(p) + 1

        dp = [[False for c in range(ncol)] for r in range(nrow)]

        dp[0][0] = True
        dp[0][1] = False
        for c in range(2, ncol):
            j = c-1
            if p[j] == '*': dp[0][c] = dp[0][c-2]

        for r in range(1, nrow):
            i = r-1
            for c in range(1, ncol):
                j = c-1
                if s[i] == p[j] or p[j] == '.':
                    dp[r][c] = dp[r-1][c-1]
                elif p[j] == '*':
                    if p[j-1] == s[i] or p[j-1] == '.':
                        dp[r][c] = dp[r-1][c] or dp[r][c-2]
                    else:
                        dp[r][c] = dp[r][c-2]
                else:
                    dp[r][c] = False

        return dp[nrow-1][ncol-1]
```
