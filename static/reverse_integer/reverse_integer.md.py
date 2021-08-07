class Solution:
    def reverse(self, x: int) -> int:
      res = 0
      devider = 10 if x >= 0 else -10
      while x != 0:
        temp = x % devider
        if res > 214748364 or (res==214748364 and temp > 7):
          return 0
        if res < -214748364 or (res==-214748364 and temp<-8):
          return 0
        res = res * 10 + temp
        x = x // devider if x > 0 else -(x // devider)

      return res