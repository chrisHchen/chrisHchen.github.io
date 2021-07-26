---
title: python 实现 k-means 算法
date: 2018-05-26 22:33:17
tags: python 机器学习
categories: python 算法
---

## 算法基础

机器学习中有两大类问题，一个是分类，一个是聚类。分类是根据已知类别标号(label)的样本，训练某个分类器，使它能够对未知类别的样本进行分类。属于 <code>supervised learning</code> (监督学习)。而聚类指事先并不知道任何样本的类别标号，而希望通过某种算法来把一组未知类别的样本划分成若干类别，这在机器学习中属于 <code>unsupervised learning</code>（非监督学习）

而本文要实现的 k-means 算法就是一个比较简单的聚类算法。

k-means 算法的基本思想是：通过迭代寻找 k 个聚类，使得用这 k 个聚类的均值来代表相应各类样本时所得的总体误差最小。k-means 算法的基础是最小误差平方和准则。

k-means 算法的代价函数如下：
![](/static/kmeans/losfn.gif)

x(i) 表示第 i 个样本点，μc(i)表示第 i 个聚类的均值，c 表示某个类别的集合

我们希望代价函数最小，如果各类内的样本越相似，其与该类均值间的误差平方越小，则各类的误差平方和也越小。

k-means 算法基本步骤如下：

<!--more-->

1. 随机选取 k 个点作为初始质心。
2. 对于样本中每一个点，分别求与 k 点的距离。距离最小者就属于该类。
3. 此时对得到的 k 个类，重新计算新的质心。
4. 当 3 步得到的质心与之前的质心误差很小时，分类结束。

## 数据集

本例使用 sklearn 提供的 iris 数据：

```python
from sklearn import datasets

iris = datasets.load_iris()
X, y = iris.data, iris.target
data = X[:,[0,1]] # 取前两个维度作为样本 feature
```

## 计算欧式距离

欧式距离的计算函数如下：

```python
import numpy as np

def distance(p1, p2):
  return np.sqrt(np.sum((p1-p2)**2))

# test
distance(np.array([0,0]), np.array([1,2])) # 2.23606797749979
```

## 随机选取 Centroid

算法要求初始化时随机在数据集范围内选取 k 个 centroid:

```python
def randam_centroid(data, k):
  n = data.shape[1]
  centroids = np.zeros((k, n))
  for i in range(n):
    dmin, dmax = np.min(data[:,i]), np.max(data[:,i])
    centroids[:, i] = dmin + (dmax - dmin) * np.random.rand(k)
  return centroids
```

其中 <code>np.random.rand(k)</code> 表示随机生成一个 k 维的 np.array 数组，数组每项都在 [0, 1) 之间

## k-means 聚类算法

其中 <code>calc_kmeans</code> 是算法主体函数，主要有两个逻辑：
循环数据集，并计算样本和每个 centroid 的欧氏距离，最后将样本归类到距离最小的簇。
循环 centroids，计算属于该 centroid 簇的样本平均值，结果作为新的 centroids。

converged 函数的逻辑是判断两组 centroids 是否完全一致，用来判断 k-means 算法是否收敛。当 centroids 不再变化时则算法结束。

另外，k-means 有个缺点可能会陷入局部最优解（而不是全局最优解），所以这里通过多次计算取代价最小的解。这部分的逻辑在 mean_result 函数中实现。

```python
class KMeans:
  def __init__(self, data) -> None:
      self.data = data

  def converged(self, c1, c2):
    set1 = set([tuple(c) for c in c1])
    set2 = set([tuple(c) for c in c2])
    return set1 == set2

  def calc_kmeans(self, k=2):
      data = self.data
      n = data
      n = data.shape[0] # number of entries
      centroids = randam_centroid(data, k)
      label = np.zeros(n, dtype=int) # track the nearest centroid
      assement = np.zeros(n) # for the assement of our model
      converged = False

      while not converged:
          old_centroid = np.copy(centroids)
          for i in range(n):
            min_dist = np.inf
            for j in range(k):
              dist = distance(data[i], centroids[j])
              if dist < min_dist:
                min_dist = dist
                label[i] = j
            assement[i] = distance(data[i], centroids[label[i]])**2

          # update centroid
          for m in range(k):
            centroids[m] = np.mean(data[label==m], axis=0)
          converged = self.converged(centroids, old_centroid)
      return centroids, label, np.sum(assement)

  """
  由于算法可能局部收敛的问题，随机多运行几次，取最优值
  """
  def mean_result(self, k, m = 10):
    best_assement = np.inf
    best_centroids = None
    best_label = None
    for i in range(m):
        centroids, label, assement = self.calc_kmeans(k)
        if assement < best_assement:
          best_centroids = centroids
          best_label = label
          best_assement = assement
    return best_centroids, best_label
```

使用以上算法在 iris 数据子集上计算的结果如下，分别为 k=2，3，4 的结果, 图中的圆点为 centroid：
<img src="/static/kmeans/Figure_2.png" alt="k=2" width="640" height="480" align="bottom" />
<img src="/static/kmeans/Figure_3.png" alt="k=3" width="640" height="480" align="bottom" />
<img src="/static/kmeans/Figure_4.png" alt="k=4" width="640" height="480" align="bottom" />

最后提供下完整代码
<a href='/static/kmeans/kmeans.py' target="_blank">kmeans.py</a>

K-Means 的主要优点有：
1）原理比较简单，实现也是很容易，收敛速度快。
2）聚类效果较优。
3）算法的可解释度比较强。
4）主要需要调参的参数仅仅是簇数 k。

K-Means 的主要缺点有：
1）K 值的选取不好把握
2）对于不是凸的数据集比较难收敛
3）如果各隐含类别的数据不平衡，比如各隐含类别的数据量严重失衡，或者各隐含类别的方差不同，则聚类效果不佳。
4） 采用迭代方法，得到的结果只是局部最优。
5） 对噪音和异常点比较的敏感。
