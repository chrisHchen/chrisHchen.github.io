---
title: 最长回文子串
date: 2020-2-01 12:06:22
tags: [算法, 力扣, python]
categories: 算法
---

## 什么是回文串

最长回文子串是面试中经常问到的算法题。首先得明确什么是回文串？回文串就是正着读和反正读都一样的字符串。

比如 <code>aba</code> 和 <code>acca</code>

## 回文串的特点

回文串的特点：如果一个字符串 s 是回文串，则 s 去掉头尾的字符后的字符串依然是回文串。比如 <code>acbca</code> 是回文串，则去掉头尾的 a 后的字符串 <code>cbc</code> 也肯定是回文串，再迭代一下,去掉头尾的 c 后形成的字符串 <code>b</code> 也是回文串(单字母的字符串永远是回文串)。

所以寻找回文串的问题核心思想是：从中间开始向两边扩散来判断回文串。

这里要注意的一点是，回文串的长度可能是奇数也可能是偶数，比如 <code>acbca</code> 和 <code>acca</code> 都是回文串。

<!--more-->

## 非动态规划算法

按照上面的思路，从中心向两边扩散的思路，可以写出非动态规划的算法，python 实现的版本如下：

```python
# 非动态规划算法
class Solution:
    def longestPalindrome(self, s: str) -> str:
      res = ''
      # 枚举中心位置的索引
      for i in range(len(s)):
        # 长度为奇数时
        s1 = self.palindrome(s,i ,i)
        # 长度为偶数时
        s2 = self.palindrome(s,i ,i + 1)
        res = s1 if len(s1) > len(res) else res
        res = s2 if len(s2) > len(res) else res
      return res


    def palindrome(self, str, l, r):
      length = len(str)
      # 索引界限判断
      while l >=0 and r < length and str[l] == str[r]:
        # 向两边扩展
        l = l - 1
        r = r + 1
      return str[l+1: r]
```

算法的时间复杂度 O(N^2)，空间复杂度 O(1)。

## 动态规划算法

上一篇文章[动态规划总结](https://chrishchen.github.io/2020/01/20/algorithm/dynamic_programming/)提到过，动态规划算法最主要的就是找出状态，并得到状态转移方程。

这里的状态有 2 个，左边界 i 和右边界 j。动态规划的状态转移方程：

**P(i,j)=P(i+1,j−1)∧(S[i]==S[j])**

上面这个方程的意思是：从状态 P(i+1,j−1)是回文串要推导出(转移到) P(i,j) 也是回文串的条件就是 S[i]==S[j]。也就是说 P(i,j) 的值(True/False)是 P(i+1,j−1) and (S[i]==S[j]) 的逻辑交。这个条件其实和上面非动态规划算法是一致的。只是动态规划里需要用到 dp table。

在状态转移方程中，我们是从长度较短的字符串向长度较长的字符串进行转移的，因此一定要注意动态规划的循环顺序：自底向上

具体的算法如下

```python
# 动态规划算法
class SolutionDP:
    def longestPalindrome(self, s: str) -> str:
      length = len(s)
      # 长度为 1 的都是回文串
      if length < 2:
        return s
      # dp[i][j] 表示 s[i..j] 是否是回文串
      dp = [[False for i in range(length)] for j in range(length)]
      maxLen = 0
      start = 0
      # 长度为 1 都都是回文串，初始化为 True
      for i in range(length):
        dp[i][i] = True
      # 枚举子串长度
      for slen in range(2, length):
        # 枚举左边界
        for i in range(length):
          # 右边界
          j = i + slen - 1
          if j > slen:
            break
          if s[i] != s[j]:
            # 状态转移为 False
            dp[i][j] = False
          else:
            if j - i < 3:
              # 状态转移为 True
              dp[i][j] = True
            else:
              # 状态转移为 True/False
              dp[i][j] = dp[i + 1][j - 1]
          if dp[i][j] == True and (j - i + 1) > maxLen:
            maxLen = j - i + 1
            start = i

      return s[start: start + maxLen]
```

python3 版本的算法源文件下载 <a href='/static/longestPalindromicSubstring/lp.py' target="_blank">lp.py</a>
