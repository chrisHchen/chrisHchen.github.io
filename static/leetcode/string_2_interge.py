import re

class Solution:
    def myAtoi(self, s: str) -> int:
      s = s.lstrip()
      # 去除空格后长度为 1，则直接返回 0
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
      
sol = Solution()
print(sol.myAtoi("-91283472332"))