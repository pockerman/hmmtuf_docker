"""
Preprocessing utilities
"""

from pomegranate import *
from scipy import stats
import numpy as np
import copy


from compute_engine.src.windows import WindowType
from compute_engine.src.constants import INFO
from compute_engine.src.exceptions import Error

VALID_DISTS = ['normal', 'uniform',
               'poisson', 'discrete', ]


def fit_distribution(data, dist_name="normal", **kwargs):
    """
    Fits a distribution within the given dataset
    """
    if dist_name not in VALID_DISTS:
        raise Error("Invalid distribution name. \
                    Name '{0}' not in {1}".format(dist_name, VALID_DISTS))

    if dist_name == 'normal':
        dist = NormalDistribution.from_samples(data)
        return dist
    elif dist_name == 'uniform':
        dist = UniformDistribution.from_samples(data)
        return dist
    elif dist_name == 'poisson':
        dist = PoissonDistribution.from_samples(data)
        return dist
    elif dist_name == 'discrete':
        dist = DiscreteDistribution.from_samples(data)
        return dist


def compute_statistic(data, statistics):
    valid_statistics = ["all", "mean", "var",
                        "median", "min", "max",
                        "mode", "q75", "q50", "q25"]

    if statistics not in valid_statistics:
        raise Error("Invalid statistsics: '{0}'"
                    " not in {1}".format(statistics,
                                         valid_statistics))

    if statistics == "mean":
        return np.mean(data)
    elif statistics == "var":
        return np.var(data)
    elif statistics == "median":
        return np.median(data)
    elif statistics == "min":
        return np.amin(data)
    elif statistics == "max":
        return np.amax(data)
    elif statistics == "mode":
        return stats.mode(data, axis=None).mode[0]
    elif statistics == "q75":
        return np.percentile(data, [75])
    elif statistics == "q25":
        return np.percentile(data, [25])
    elif statistics == "q50":
        return np.percentile(data, [50])
    elif statistics == "all":

        mean = np.mean(data)
        var = np.var(data)
        median = np.median(data)
        min_ = np.amin(data)
        max_ = np.amax(data)
        mode = stats.mode(data, axis=None).mode[0]
        q75, q50, q25 = np.percentile(data, [75, 50, 25])
        return {"mean": mean, "var": var,
                "median": median,
                "min": min_,
                "max": max_,
                "mode": mode,
                "iqr": q75 - q25,
                "q75": q75,
                "q25": q25,
                "q50": q50}


def zscore_outlier_removal(windows, config):
    new_windows = []

    statistics = config["statistics"]
    sigma_wga = np.sqrt(statistics[WindowType.WGA]["var"])
    sigma_no_wga = np.sqrt(statistics[WindowType.NO_WGA]["var"])

    gap_counter = 0
    remove_window_counter = 0
    for window in windows:
        # we don't want to remove the n_windows
        # as these mark gaps
        if not window.is_gap_window():
            mu = window.get_rd_statistic(statistics="mean",
                                         name=WindowType.BOTH)

            zscore_wga = (mu[0] - statistics[WindowType.WGA]["mean"]) / sigma_wga
            zscore_no_wga = (mu[1] - statistics[WindowType.NO_WGA]["mean"]) / sigma_no_wga

            if zscore_wga > config["sigma_factor"] or \
                    zscore_no_wga > config["sigma_factor"]:
                remove_window_counter += 1
                continue
            elif config["use_both_ends"] == True and \
                    (zscore_wga < - config["sigma_factor"] or \
                     zscore_no_wga < - config["sigma_factor"]):

                remove_window_counter += 1
                continue
            else:
                new_windows.append(window)
        else:

            gap_counter += 1
            new_windows.append(window)

    print("{0} Removed {1} windows ".format(INFO, remove_window_counter))
    print("{0} There are {1} GAP windows ".format(INFO, gap_counter))
    return new_windows


def means_cutoff_outlier_removal(windows, config):
    new_windows = []
    limits = config['mu_limits']
    print("{0} Cutoff means limit: {1}".format(INFO, limits))
    gap_counter = 0
    remove_window_counter = 0
    for window in windows:

        # we don't want to remove the n_windows
        # as these mark gaps
        if not window.is_gap_window():
            mu = window.get_rd_statistic(statistics="mean",
                                         name=WindowType.BOTH)

            if mu[0] > limits['wga_mu']:
                remove_window_counter += 1
                continue
            elif mu[1] > limits['no_wga_mu']:
                remove_window_counter += 1
                continue
            else:
                new_windows.append(window)
        else:
            gap_counter += 1
            new_windows.append(window)

    print("{0} Removed {1} windows ".format(INFO, remove_window_counter))
    print("{0} There are {1} GAP windows ".format(INFO, gap_counter))
    return new_windows


def remove_outliers(windows, removemethod, config):
    if removemethod == "zscore":
        return zscore_outlier_removal(windows=windows, config=config)
    elif removemethod == "means_cutoff":
        return means_cutoff_outlier_removal(windows=windows, config=config)

    raise Error("Unknown outlier removal method: {0}".format(removemethod))


def get_distance_metric(dist_metric, degree=4):
    if dist_metric.upper() == "MANHATAN":
        t_metric = type_metric.MANHATTAN
        metric = distance_metric(metric_type=t_metric)
    elif dist_metric.upper() == "EUCLIDEAN":
        t_metric = type_metric.EUCLIDEAN
        metric = distance_metric(metric_type=t_metric)
    elif dist_metric.upper() == "CHEBYSHEV":
        t_metric = type_metric.CHEBYSHEV
        metric = distance_metric(metric_type=t_metric)
    elif dist_metric.upper() == "MINKOWSKI":
        t_metric = type_metric.MINKOWSKI
        metric = distance_metric(metric_type=t_metric, degree=degree)
    else:
        raise Error("Metric type '{0}' "
                    "not in {1}".format(dist_metric,
                                        ['MANHATAN', "EUCLIDEAN", "CHEBYSHEV", "MINKOWSKI"]))

    return metric


def get_data_for_clustering(data, features):
    cfeatures = copy.deepcopy(features)
    print("{0} cluster features used {1}".format(INFO, cfeatures))

    windows = []

    has_gc = False
    if 'gc' in cfeatures:
        cfeatures.pop(cfeatures.index('gc'))
        has_gc = True

    has_mean_ratio = False
    if 'mean_ratio' in cfeatures:
        cfeatures.pop(cfeatures.index('mean_ratio'))
        has_mean_ratio = True

    has_wga_mean = False
    if 'wga_mean' in cfeatures:
        cfeatures.pop(cfeatures.index('wga_mean'))
        has_wga_mean = True

    has_no_wga_mean = False
    if 'no_wga_mean' in cfeatures:
        cfeatures.pop(cfeatures.index('no_wga_mean'))
        has_no_wga_mean = True

    for window in data:

        if has_wga_mean:
            window_values = [window.get_feature(feature='mean', name=WindowType.WGA)]
        elif has_no_wga_mean:
            window_values = [window.get_feature(feature='mean', name=WindowType.NO_WGA)]
        else:
            window_values = window.get_features(features=cfeatures)

        if has_gc:
            window_values.append(window.get_feature(feature='gc', name=WindowType.WGA))

        if has_mean_ratio:
            means = window.get_features(features=['mean'])
            ratio = (means[0] + 1) / (means[1] + 1)
            window_values.append(ratio)

        windows.append(window_values)
    return windows


def build_clusterer(data, nclusters, method, **kwargs):
    """
      A simple wrapper to various clustering approaches.
      Cluster the given data into nclusters by using the
      specified method. Depending on the specified method
      different packages may be required and different
      arguments are expected in the kwargs dict.
    """

    features = copy.deepcopy(kwargs["config"]["features"])
    print("{0} cluster features used {1}".format(INFO, features))

    windows = []

    has_gc = False
    if 'gc' in features:
        features.pop(features.index('gc'))
        has_gc = True

    has_mean_ratio = False
    if 'mean_ratio' in features:
        features.pop(features.index('mean_ratio'))
        has_mean_ratio = True

    has_wga_mean = False
    if 'wga_mean' in features:
        features.pop(features.index('wga_mean'))
        has_wga_mean = True

    has_no_wga_mean = False
    if 'no_wga_mean' in features:
        features.pop(features.index('no_wga_mean'))
        has_no_wga_mean = True

    for window in data:

        if has_wga_mean:
            window_values = [window.get_feature(feature='mean', name=WindowType.WGA)]
        elif has_no_wga_mean:
            window_values = [window.get_feature(feature='mean', name=WindowType.NO_WGA)]
        else:
            window_values = window.get_features(features=features)

        if has_gc:
            window_values.append(window.get_feature(feature='gc', name=WindowType.WGA))

        if has_mean_ratio:
            means = window.get_features(features=['mean'])
            ratio = (means[0] + 1) / (means[1] + 1)
            window_values.append(ratio)

        windows.append(window_values)

    if method == "kmeans":

        from sklearn.cluster import KMeans
        clusterer = KMeans(n_clusters=nclusters)

        clusterer.fit(windows)
        return clusterer
    elif method == "kmedoids":

        from pyclustering.cluster.kmedoids import kmedoids

        metric = get_distance_metric(dist_metric=kwargs["config"]["metric"].upper(),
                                     degree=kwargs["config"]["metric_degree"]
                                     if 'metric_degree' in kwargs["config"] else 0)

        initial_index_medoids = []
        if kwargs["config"]["init_cluster_idx"] == "random_from_data":
            import random

            for c in range(nclusters):
                idx = random.randint(0, len(windows) - 1)

                if idx in initial_index_medoids:

                    # try ten times before quiting
                    for time in range(10):
                        idx = random.randint(0, len(windows) - 1)

                        if idx in initial_index_medoids:
                            continue
                        else:
                            initial_index_medoids.append(idx)
                            break

                else:
                    initial_index_medoids.append(idx)
        else:
            initial_index_medoids = kwargs["config"]["init_cluster_idx"]

        clusterer = kmedoids(data=windows,
                             initial_index_medoids=initial_index_medoids,
                             metric=metric)
        clusterer.process()
        return clusterer, initial_index_medoids

    raise Error("Invalid clustering method: " + method)


def get_distributions_list_from_names(dists_name, params):
    dists = []

    for name in dists_name:
        if name == "normal":
            dists.append(NormalDistribution(params["mean"], params["std"]))
        elif name == "poisson":
            dists.append(PoissonDistribution(params["mean"]))
        elif name == "uniform":
            dists.append(UniformDistribution(params["uniform_params"][0],
                                             params["uniform_params"][1]))
        else:
            raise Error("Name '{0}' is an unknown distribution ".format(name))
    return dists
