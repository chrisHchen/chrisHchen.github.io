import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets

def distance(p1, p2):
  return np.sqrt(np.sum((p1-p2)**2))

def randam_centroid(data, k):
  n = data.shape[1]
  centroids = np.zeros((k, n))
  for i in range(n):
    dmin, dmax = np.min(data[:, i]), np.max(data[:,i])
    centroids[:, i] = dmin + (dmax - dmin) * np.random.rand(k)
  return centroids

def draw(data, centroids, label):
  dn = data.shape[0]
  cn = centroids.shape[0]
  mark = ['or', 'ob', 'og', 'ok', '^r', '+r', 'sr', 'dr', '<r', 'pr']
  for i in range(cn):
    plt.plot(centroids[i, 0], centroids[i, 1], mark[i], markersize = 12)
  mark = ['Dr', 'Db', 'Dg', 'Dk', '^b', '+b', 'sb', 'db', '<b', 'pb']
  for i in range(dn):
    plt.plot(data[i, 0], data[i, 1], mark[label[i]])
  
  plt.show()


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



iris = datasets.load_iris()
X, y = iris.data, iris.target
data = X[:,[0,1]] # 取前两个feature
classifor = KMeans(data)
best_centroids, best_label = classifor.mean_result(2)
draw(classifor.data, best_centroids, best_label)




