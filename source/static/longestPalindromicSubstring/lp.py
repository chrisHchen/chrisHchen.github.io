# 非动态规划算法
class Solution:
    def longestPalindrome(self, s: str) -> str:
      res = ''
      for i in range(len(s)):
        s1 = self.palindrome(s,i ,i)
        s2 = self.palindrome(s,i ,i + 1)
        res = s1 if len(s1) > len(res) else res
        res = s2 if len(s2) > len(res) else res
      return res
    
    
    def palindrome(self, str, l, r):
      length = len(str)
      while l >=0 and r < length and str[l] == str[r]:
        l = l - 1
        r = r + 1
      return str[l+1: r]

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

        

    

sol = Solution()
soldp = SolutionDP()
str = "abbacba"
print(sol.longestPalindrome(str))
print(soldp.longestPalindrome(str))