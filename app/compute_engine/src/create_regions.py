import sys

#from helpers import read_configuration_file
#from helpers import set_up_logger
from compute_engine.src.windows import WindowType
from compute_engine.src.constants import INFO, WARNING
from compute_engine.src.utils import timefn
from compute_engine.src.region import Region


@timefn
def make_window_regions(configuration):
    print("{0} Creating window regions...".format(INFO))
    print("{0} Processing type is: {1}".format(INFO, configuration['processing']['type']))

    if configuration['processing']['type'] == 'multi':
        from parallel import par_make_window_regions
        return par_make_window_regions(configuration=configuration)

    windowsize = configuration["window_size"]
    chromosome = configuration["chromosome"]

    print("{0} Window size: {1}".format(INFO, windowsize))
    print("{0} Chromosome:  {1}".format(INFO, chromosome))

    regions = configuration["regions"]
    print("{0} Regions used {1}".format(INFO, regions))

    regions_list = [(start, end) for start, end
                    in zip(regions["start"], regions["end"])]

    regions_created = []

    counter = 0
    for r in regions_list:

        start_idx = r[0]
        end_idx = r[1]

        print("{0} Start index: {1}".format(INFO, start_idx))
        sys.stdout.flush()
        print("{0} End index:   {1}".format(INFO, end_idx))
        sys.stdout.flush()
        region = Region(idx=counter,
                        start=start_idx,
                        end=end_idx,
                        window_size=windowsize)

        kwargs = {"sam_read_config": configuration["sam_read_config"]}

        if "debug" in configuration:
            kwargs["debug"] = configuration["debug"]

        print("{0} Creating WGA Windows...".format(INFO))
        sys.stdout.flush()
        region.make_wga_windows(chromosome=chromosome,
                                ref_filename=configuration["reference_file"]["filename"],
                                bam_filename=configuration["wga_file"]["filename"],
                                **kwargs)

        #if region.get_n_windows(type_=WindowType.WGA) == 0:
        #    raise Error("WGA windows have not been created")
        #else:
        print("{0} Number of WGA "
                  "windows: {1}".format(INFO,
                                        region.get_n_windows(type_=WindowType.WGA)))
        sys.stdout.flush()

        print("{0} Creating No WGA Windows...".format(INFO))
        sys.stdout.flush()
        region.make_no_wga_windows(chromosome=chromosome,
                                   ref_filename=configuration["reference_file"]["filename"],
                                   bam_filename=configuration["no_wga_file"]["filename"],
                                   **kwargs)

        #if region.get_n_windows(type_=WindowType.NO_WGA) == 0:
        #    raise Error("Non-WGA windows have not  been created")
        #else:
        print("{0} Number of Non WGA"
                  " windows: {1}".format(INFO,
                                         region.get_n_windows(type_=WindowType.NO_WGA)))
        sys.stdout.flush()

        regions_created.append(region)
        counter += 1

    return regions_created


def remove_or_mark_gaps(region, configuration):
    # filter the windows for GAPs
    if "remove_windows_with_gaps" in configuration and \
            configuration["remove_windows_with_gaps"]:

        print("{0} Removing windows with gaps...".format(INFO))

        region.remove_windows_with_gaps()

        print("{0} Number of wga windows"
              " after removing GAP windows: {1}".format(INFO,
                                                        region.get_n_windows(type_=WindowType.WGA)))
        sys.stdout.flush()
        print("{0} Number of non-wga windows"
              " after removing GAP windows: {1}".format(INFO,
                                                        region.get_n_windows(type_=WindowType.NO_WGA)))
        print("{0} Done...".format(INFO))
        sys.stdout.flush()
    else:
        # mark the Gap windows
        print("{0} Marking Gap "
              " windows with: {1}".format(INFO,
                                          configuration["mark_for_gap_windows"]))
        sys.stdout.flush()

        counter_ns = \
            region.mark_windows_with_gaps(n_mark=configuration["mark_for_gap_windows"])

        print("{0} Marked as Gap {1} Windows".format(INFO, counter_ns))
        sys.stdout.flush()


def remove_outliers(region, configuration):

    if "outlier_remove" in configuration:

        print("{0} Remove outliers...".format(INFO))
        region.remove_outliers(configuration=configuration)
        print("{0} Number of windows "
              "after outlier removal: {1}".format(INFO,
                                                  region.get_n_mixed_windows()))
        sys.stdout.flush()

        print("{0} Number of GAP windows "
              "after outlier removal {1}".format(INFO,
                                                 region.count_gap_windows()))
        sys.stdout.flush()
    else:
        print("{0} No outlier "
              "removal performed".format(INFO))
        sys.stdout.flush()


@timefn
def clean_up_regions(regions, configuration):
    print("{0} Clean up regions".format(INFO))
    sys.stdout.flush()
    for region in regions:

        if "check_windowing_sanity" in configuration and \
                configuration["check_windowing_sanity"]:
            region.check_windows_sanity()
        else:
            print("{0} Window sanity check is disabled".format(WARNING))

        # compute the mixed windows for the region
        region.get_mixed_windows()

        print("{0} Number of windows for region: {1}".format(INFO, len(region)))
        print("{0} Removing windows with errors".format(INFO))
        region.remove_windows_with_errors()
        print("{0} Number of windows after removing errors: {1}".format(INFO, len(region)))
        print("{0} Remove/Mark GAP windows: ".format(INFO))
        remove_or_mark_gaps(region=region, configuration=configuration)

        print("{0} Number of mixed "
              "windows: {1}".format(INFO,
                                    region.get_n_mixed_windows()))
        sys.stdout.flush()

        print("{0} Number of GAP windows: {1}".format(INFO,
                                                      region.count_gap_windows()))
        sys.stdout.flush()

        if "do_remove_outliers" in configuration and configuration["do_remove_outliers"]:
            remove_outliers(region=region, configuration=configuration)
        else:
            print("{0} No outlier removal".format(INFO))
            sys.stdout.flush()


@timefn
def save_regions(regions, configuration):
    print("{0} Saving regions".format(INFO))
    sys.stdout.flush()

    for region in regions:
        #region.save_mixed_windows_statistic(statistic="mean", tips=configuration["plot_tips"])
        #region.save_mixed_windows_gc_content(tips=configuration["plot_tips"])
        region.save(path=configuration["region_path"], filename=configuration["region_name"], tips=None)# tips=configuration["plot_tips"])


@timefn
def main(configuration):

    """
    print("{0} Set up logger".format(INFO))
    sys.stdout.flush()
    set_up_logger(configuration=configuration)
    logging.info("Checking if logger is sane...")
    print("{0} Done...".format(INFO))
    sys.stdout.flush()
    """

    regions = make_window_regions(configuration=configuration)

    clean_up_regions(regions=regions, configuration=configuration)

    proc = None
    if configuration['processing'] == 'multi':
        # create a process to save the regions
        # and keep on doing what we have to do
        from multiprocessing import Process
        proc = Process(target=save_regions,
                       args=(regions, configuration))
        proc.start()
    else:
        save_regions(regions, configuration=configuration)

    if proc is not None:
        proc.join()


if __name__ == '__main__':
    raise ValueError("You should not call this as main script")
