"""
Various helpers to be used in the analysis module
"""

from compute_engine.src.windows import WindowType


def save_cluster(filename, cluster, statistic, wtype):

  with open(filename, 'w') as file:
    file.write(str(cluster.get_window_statistics(statistic=statistic,
                                                 window_type=wtype)))


def save_clusters(clusters, statistic, tips):

  for cluster in clusters:

    if tips is not None:
      wga_file = "cluster_"+str(cluster.cidx) +"_wga_w_" + statistic
      no_wga_file = "cluster_"+str(cluster.cidx) +"_no_wga_w_" + statistic

      for tip in tips:
        wga_file += "_" + tip
        no_wga_file += "_" + tip

      wga_file += ".txt"
      no_wga_file += ".txt"

    else:
      wga_file = "cluster_"+str(cluster.cidx) +"_wga_w_" + statistic + ".txt"
      no_wga_file = "cluster_"+str(cluster.cidx) +"_no_wga_w_" + statistic + ".txt"


    save_cluster(filename=wga_file, cluster=cluster,
                 statistic=statistic, wtype=WindowType.WGA)

    save_cluster(filename=no_wga_file, cluster=cluster,
                   statistic=statistic, wtype=WindowType.NO_WGA)


def save_clusters_gc_content(clusters, tips):
  statistic = 'gc'
  for cluster in clusters:

    if tips is not None:
      wga_file = "cluster_"+str(cluster.cidx) +"_wga_w_" + statistic

      for tip in tips:
        wga_file += "_" + tip
      wga_file += ".txt"

    else:
      wga_file = "cluster_"+str(cluster.cidx) +"_wga_w_" + statistic + ".txt"

    save_cluster(filename=wga_file, cluster=cluster,
                 statistic=statistic, wtype=WindowType.WGA)


def save_windows_statistic(windows, statistic, region_id=None, tips=None):

  window_stats = \
    [window.get_rd_statistic(statistics=statistic,
                             name=WindowType.NO_WGA)
       for window in windows if not window.is_gap_window()]

  if region_id is not None:
    filename = "no_wga_windows_" + statistic + "_" + str(region_id)

    if tips is not None:
      for tip in tips:
        filename += "_" + tip
      filename += ".txt"
  else:
    filename = "no_wga_windows_" + statistic

    if tips is not None:
      for tip in tips:
        filename += "_" + tip
      filename += ".txt"

  with open(filename, 'w') as file:
    file.write(str(window_stats))

  window_stats = \
    [window.get_rd_statistic(statistics=statistic,
                             name=WindowType.WGA)
     for window in windows if not window.is_gap_window()]

  if region_id is not None:
    filename = "wga_windows_" + statistic + "_" + str(region_id)
    if tips is not None:
      for tip in tips:
        filename += "_" + tip
      filename += ".txt"
  else:
    filename = "wga_windows_" + statistic

    if tips is not None:
      for tip in tips:
        filename += "_" + tip
      filename += ".txt"

  with open(filename, 'w') as file:
    file.write(str(window_stats))
