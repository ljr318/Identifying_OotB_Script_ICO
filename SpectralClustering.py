import json
import matplotlib.pyplot as plt
from sklearn.cluster import SpectralClustering
import matplotlib as mpl
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from config import color_map
from scipy import sparse
import random
from scipy.sparse.linalg import eigsh
import numpy as np
from scipy.sparse.csgraph import laplacian as csgraph_laplacian


class SpectralClustering(object):
    def __init__(self):
        self.n_clusters = None
        self.similarity_matrix = None
        self.sc = None

    # modified from sklearn _spectrual_embedding
    def _set_diag(self, laplacian, value, norm_laplacian):
        n_nodes = laplacian.shape[0]
        if not sparse.isspmatrix(laplacian):
            if norm_laplacian:
                laplacian.flat[::n_nodes + 1] = value
        else:
            laplacian = laplacian.tocoo()
            if norm_laplacian:
                diag_idx = (laplacian.row == laplacian.col)
                laplacian.data[diag_idx] = value
            n_diags = np.unique(laplacian.row - laplacian.col).size
            if n_diags <= 7:
                laplacian = laplacian.todia()
            else:
                laplacian = laplacian.tocsr()
        return laplacian

    # modified from sklearn _spectrual_embedding
    def _deterministic_vector_sign_flip(self, u):
        max_abs_rows = np.argmax(np.abs(u), axis=1)
        signs = np.sign(u[range(u.shape[0]), max_abs_rows])
        u *= signs[:, np.newaxis]
        return u

    # modified from sklearn _spectrual_embedding
    def laplacian_embedding(self, similarity_matrix, *, n_components=8, eigen_tol=0.0, norm_laplacian=True, drop_first=True):
        n_nodes = similarity_matrix.shape[0]
        if drop_first:
            n_components = n_components + 1

        laplacian, dd = csgraph_laplacian(similarity_matrix, normed=norm_laplacian,
                                          return_diag=True)
        laplacian = self._set_diag(laplacian, 1, norm_laplacian)
        laplacian *= -1
        v0 = random.uniform(-1, 1, laplacian.shape[0])
        _, diffusion_map = eigsh(
            laplacian, k=n_components, sigma=1.0, which='LM',
            tol=eigen_tol, v0=v0)
        embedding = diffusion_map.T[n_components::-1]
        if norm_laplacian:
            embedding = embedding / dd

        embedding = self._deterministic_vector_sign_flip(embedding)
        return embedding[1:n_components].T

    def determine_cluster_num(self):
        count = len(self.similarity_matrix)
        distance_matrix = [[0 for col in range(count)] for row in range(count)]
        for i in range(count):
            for j in range(count):
                distance_matrix[i][j] = 100 - self.similarity_matrix[i][j]
        n_cluster = []
        score = []
        max_score = -999
        max_n = -1
        for n in range(2, 150):
            sc = SpectralClustering(n_clusters=n, affinity='precomputed', assign_labels='discretize')
            sc.fit(self.similarity_matrix)
            n_cluster.append(n)
            silhouette_coefficient = metrics.silhouette_score(distance_matrix, sc.labels_, metric='precomputed')
            if silhouette_coefficient > max_score:
                max_n = n
                max_score = silhouette_coefficient
            score.append(silhouette_coefficient)
        self.n_clusters = max_n
        plt.plot(n_cluster, score)
        plt.show()

    def clustering_visualization(self):
        vectors = self.laplacian_embedding(self.similarity_matrix)
        X = StandardScaler().fit_transform(vectors)
        pca = PCA(n_components=2)
        principalComponents = pca.fit_transform(X)
        cm_dark = mpl.colors.ListedColormap(color_map)
        plt.scatter(principalComponents[:, 0], principalComponents[:, 1], c=self.sc.labels_, cmap=cm_dark, s=36, alpha=0.7)
        plt.show()

    def cluster_size_visualization(self):
        labels = self.sc.labels_
        x = [i for i in range(1, self.n_clusters+1)]
        y = [0 for i in range(0, self.n_clusters)]
        for i in labels:
            y[i] = y[i] + 1
        plt.scatter(x, y, s=12)
        plt.xlabel('Cluster Label')
        plt.ylabel('Cluster Size')
        print('min:' + str(min(y)))
        print('max:' + str(max(y)))
        plt.show()

    def start_clustering(self):
        with open('similarity_matrix.json', 'r') as f:
            self.similarity_matrix = json.load(f)
        self.sc = SpectralClustering(n_clusters=self.n_clusters, affinity='precomputed', assign_labels='discretize')
        self.sc.fit(self.similarity_matrix)



