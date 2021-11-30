"""
Implementation of the modified bisection
k-means algorithm discussed in
A novel hierarchical clustering algorithm for gene
sequences by Wei et all
"""
import numpy as np
from compute_engine.src.constants import INFO


class Cluster(object):

    def __init__(self, idx, centroid, indexes=None):
        self._idx = idx
        self._centroid = centroid
        self._indexes = indexes

    @property
    def idx(self):
        return self._idx

    @idx.setter
    def idx(self, value):
        self._idx = value

    @property
    def centroid(self):
        return self._centroid

    @centroid.setter
    def centroid(self, value):
        self._centroid = value

    @property
    def indexes(self):
        return self._indexes

    @indexes.setter
    def indexes(self, value):
        self._indexes = value

    def compute_variance(self, distance_metric, dataset):

        if len(self._indexes) == 0:
            raise ValueError("Cluster is empty. Cannot compute variance")

        sum = 0.0
        for index in self._indexes:
            seq = dataset[index]
            dist = distance_metric(seq, self._centroid)
            sum += dist**2
        return sum/len(self._indexes)


class MbKMeans(object):

    def __init__(self, distance_metric, iterations,
                 tolerance, n_clusters, initializer,
                 use_largest_cluster_to_bisect=False,
                 verbose=False,
                 n_bisection_iterations=10,
                 use_sklearn_kmeans=False):

        self._distance_metric = distance_metric
        self._iterations = iterations
        self._tolerance = tolerance
        self._n_clusters = n_clusters
        self._initializer = initializer
        self._clusters = []
        self._use_largest_cluster_to_bisect = use_largest_cluster_to_bisect
        self._verbose = verbose
        self._n_bisection_iterations = n_bisection_iterations
        self._use_sklearn_kmeans  = use_sklearn_kmeans

    @property
    def clusters(self):
        return self._clusters

    def cluster(self, dataset):

        if self._n_clusters > len(dataset):
            raise ValueError("Number of clusters cannot be larger than data points")

        # create the first cluster
        # no centroid is chosen here. This is set up during
        # the first subclustering
        init_cluster = Cluster(idx=0, centroid=None, indexes=[idx for idx in range(len(dataset))])
        self._clusters.append(init_cluster)

        itr = 0
        while itr != self._iterations:

            print("{0} At iteration {1} number of clusters {2}".format(INFO, itr, len(self._clusters)))

            # pick a cluster to split
            cluster = self._select_cluster_to_split(dataset=dataset)

            if self._verbose:
                print("{0} Sub-clustering cluster {0}".format(INFO, cluster.idx))
                print("{0} Cluster centroid {0}".format(INFO, cluster.centroid))

            if self._use_sklearn_kmeans:
                if self._verbose:
                    print("{0} Using sklearn k-means...".format(INFO))
                self._apply_sklearn_kmeans(cluster=cluster, dataset=dataset)
            else:
                if self._verbose:
                    print("{0} Using default k-means...".format(INFO))
                self._sub_cluster(cluster=cluster, dataset=dataset)

            itr += 1

            if len(self._clusters) == self._n_clusters:
                print("{0} Reached number of clusters stopping iterations".format(INFO))
                print("{0} Number of iterations {1}".format(INFO, itr))
                break

    def _apply_sklearn_kmeans(self, cluster, dataset):
        from sklearn.cluster import KMeans

        # get the data that belong in the cluster
        # we sub-cluster only based on that

        ncols = dataset[0].shape[0]
        if len(dataset[0].shape) == 2:
            ncols = dataset[0].shape[1]

        new_data = np.empty((0, ncols), np.float)
        cluster_idxs = cluster.indexes

        for idx in cluster_idxs:
            new_data = np.append(new_data, np.array([dataset[idx]]), axis=0)

        kmeans = KMeans(n_clusters=2, algorithm="full",
                        n_init=10, max_iter=20, random_state=0)
        kmeans.fit(X=new_data)

        if len(self._clusters) < self._n_clusters:

            labels = kmeans.labels_
            centroids = kmeans.cluster_centers_

            if len(labels) != len(new_data):
                raise ValueError("Invalid number of labels and data")

            indexes1 = []
            indexes2 = []
            for l in range(len(labels)):
                if labels[l] == 0:
                    indexes1.append(cluster_idxs[l])
                elif labels[l] == 1:
                    indexes2.append(cluster_idxs[l])
                else:
                    raise ValueError("Invalid cluster index detected")

            if len(indexes1) == 0:
                raise ValueError("Indexes for cluster 0 are empty")

            if len(indexes2) == 0:
                raise ValueError("Indexes for cluster 1 are empty")

            new_cluster = Cluster(idx=len(self._clusters),
                                  centroid=centroids[1],
                                  indexes=indexes2)

            cluster.centroid = centroids[0]
            cluster.indexes = indexes1

            self._clusters.append(new_cluster)

    def _sub_cluster(self, cluster, dataset):
        """
        subcluster the given cluster. Repeatedly divides
        the given cluster until the cluster centroid change is
        less than self._tolerance
        """

        current_indexes = cluster.indexes

        # select two initial centroids from the cluster
        init_centroids = self._select_new_centroids(indices=current_indexes,
                                                    dataset=dataset)

        old_centroid = cluster.centroid

        for bisect_itr in range(self._n_bisection_iterations):

            if self._verbose:
                print("{0} Bisection iteration {1} of {2}".format(INFO, bisect_itr, self._n_bisection_iterations))

            indexes1, indexes2 = self._get_indices(dataset=dataset,
                                                   current_indexes=current_indexes,
                                                   init_centroids=init_centroids)

            # as long as we can add clusters
            # ad the cluster
            if len(self._clusters) < self._n_clusters:

                # update the current cluster
                # indexes and centroid
                cluster.indexes = indexes1
                cluster.centroid = dataset[init_centroids[0]]

                if len(cluster.indexes) == 0:
                    raise ValueError("indexes for given cluster are empty")

                # what happens if the centroids already exist?
                new_cluster = Cluster(idx=len(self._clusters),
                                      centroid=dataset[init_centroids[1]],
                                      indexes=indexes2)

                if len(new_cluster.indexes) == 0:
                    raise ValueError("indexes for created cluster are empty")

                self._clusters.append(new_cluster)

                # updates
                old_centroid = cluster.centroid
                current_indexes = cluster.indexes
                init_centroids = self._select_new_centroids(indices=current_indexes,
                                                            dataset=dataset)

            elif old_centroid is not None and \
                    self._distance_metric(old_centroid, dataset[init_centroids[0]]) < self._tolerance:

                if self._verbose:
                    print("{0} Cluster centroid did not change stopping bisection.".format(INFO))
                break

            elif len(self._clusters) == self._n_clusters:

                if self._verbose:
                    print("{0} Number of clusters reached.".format(INFO))
                break

    def _select_cluster_to_split(self, dataset):

        if len(self._clusters) == 0:
            raise ValueError("Empty clusters")

        if len(self._clusters) == 1:
            return self._clusters[0]

        if self._use_largest_cluster_to_bisect:

            items = 0
            cluster = None

            for cls in self._clusters:

                if len(cls.indexes) > items:
                    items = len(cls.indexes)
                    cluster = cls

            if cluster is None:
                raise ValueError("No cluster selected")
            return cluster

        cluster_idx = -1
        cluster_variance = 0.0

        for cluster in self._clusters:

            var = cluster.compute_variance(distance_metric=self._distance_metric,
                                           dataset=dataset)

            if self._verbose:
                print("Cluster {0} variance {1}".format(cluster.idx, var))

            if var > cluster_variance:
                cluster_variance = var
                cluster_idx = cluster.idx

        if cluster_idx < 0:
            raise ValueError("Invalid cluster index")

        return self._clusters[cluster_idx]

    def _get_indices(self, dataset, current_indexes, init_centroids):

        indexes1 = []
        indexes2 = []

        centroid1 = dataset[init_centroids[0]]
        centroid2 = dataset[init_centroids[1]]

        for seq_id in current_indexes:
            seq = dataset[seq_id]

            # to which new centroid is this closer
            dist1 = self._distance_metric(seq, centroid1)
            dist2 = self._distance_metric(seq, centroid2)

            if dist1 < dist2:
                indexes1.append(seq_id)
            else:
                indexes2.append(seq_id)
        return indexes1, indexes2

    def _select_new_centroids(self, indices, dataset):

        idx_seq1 = -1
        idx_seq2 = -1
        max_dist = 0.0

        # compute the distance pairs
        for idx1 in indices:
            for idx2 in indices:

                if idx1 != idx2:
                    sq1 = dataset[idx1]
                    sq2 = dataset[idx2]
                    dist = self._distance_metric(sq1, sq2)

                    if dist > max_dist:
                        max_dist = dist
                        idx_seq1 = idx1
                        idx_seq2 = idx2
        return idx_seq1, idx_seq2, max_dist