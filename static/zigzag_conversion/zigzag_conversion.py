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