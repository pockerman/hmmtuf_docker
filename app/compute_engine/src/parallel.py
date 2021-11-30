import sys
import time
from multiprocessing import Process
from multiprocessing import Manager

from helpers import partition_range
from helpers import WindowType
from helpers import INFO
from exceptions import Error
from bam_helpers import extract_windows
from region import Region


def test_windowing(**args):
    start_idx = args['start_idx']
    end_idx = args['end_idx']
    windowcapacity = args["windowsize"]
    windows = []
    while start_idx < end_idx:

        end = start_idx + windowcapacity
        # make sure we stay in bounds
        if end > end_idx:
            end = end_idx

        windows.append((start_idx, end))

        if end == end_idx:
            break

        start_idx += windowcapacity
    return windows


def regions_worker(worker_id, configuration, regions_chuncks,
                   regions_dict, msg_dict, errors_dict):
    try:

        args = {}
        if "debug" in configuration:
            args["debug"] = configuration["debug"]

        args["sam_read_config"] = configuration["sam_read_config"]
        windowsize = configuration["window_size"]

        chromosome = configuration["chromosome"]
        ref_filename = configuration["reference_file"]['filename']

        tstart = time.perf_counter()
        for rid in regions_chuncks.keys():
            worker_chunck = regions_chuncks[rid][worker_id]

            args["start_idx"] = worker_chunck[0]
            args["end_idx"] = worker_chunck[1]
            args["windowsize"] = windowsize

            wga_windows = []
            no_wga_windows = []

            bam_filename = configuration['wga_file']['filename']
            wga_windows = extract_windows(chromosome=chromosome,
                                          ref_filename=ref_filename,
                                          bam_filename=bam_filename,
                                          **args)

            bam_filename = configuration['no_wga_file']['filename']
            no_wga_windows = extract_windows(chromosome=chromosome,
                                             ref_filename=ref_filename,
                                             bam_filename=bam_filename,
                                             **args)

            regions_dict[rid][worker_id] = {"wga_windows": wga_windows,
                                            "no_wga_windows": no_wga_windows}
        tend = time.perf_counter()
        msg = ("Process {0} finished in {1} secs").format(worker_id, tend - tstart)
        msg_dict[worker_id] = msg
    except Exception as e:
        msg = "An exception occured in worker {0}. Exception message {1}".format(worker_id, str(e))
        errors_dict[worker_id] = msg
        return


def par_make_window_regions(configuration):
    n_procs = configuration["processing"]["n_procs"]
    print("{0} Creating regions with {1} processes".format(INFO, n_procs))
    sys.stdout.flush()

    regions = configuration["regions"]
    regions_list = [(start, end) for start, end
                    in zip(regions["start"], regions["end"])]

    regions_created = []

    # get the chunks that each process will work on
    chunks_dict = dict()

    for i, r in enumerate(regions_list):
        chunks_dict[i] = partition_range(start=r[0], end=r[1], npieces=n_procs)
        print("{0} chuncks for region {1}: {2}".format(INFO, i, chunks_dict[i]))
        sys.stdout.flush()
    manager = Manager()
    windows_dict = manager.dict()
    errors_dict = manager.dict()
    msg_dict = manager.dict()

    for i in range(len(regions_list)):
        windows_dict[i] = manager.dict()
        for p in range(n_procs):
            windows_dict[i][p] = {"wga_windows": [],
                                  "no_wga_windows": []}

    for p in range(n_procs):
        errors_dict[p] = "No error"
        msg_dict[p] = "No msg"

    procs = []

    for p in range(n_procs - 1):
        procs.append(Process(target=regions_worker,
                             args=(p, configuration,
                                   chunks_dict,
                                   windows_dict,
                                   msg_dict,
                                   errors_dict)))
        procs[p].start()

    print("{0} Created: {1} processes".format(INFO, n_procs))
    sys.stdout.flush()

    p = n_procs - 1
    print("{0} Master process is: {1} ".format(INFO, p))
    sys.stdout.flush()

    print("{0} Master process doing its share".format(INFO))
    sys.stdout.flush()

    p = n_procs - 1
    regions_worker(p,
                   configuration,
                   chunks_dict,
                   windows_dict,
                   msg_dict,
                   errors_dict)

    if errors_dict[p] != "No error":
        raise Error(errors_dict[p])
    else:
        print("{0} Process {1} msg: {2}".format(INFO, p, msg_dict[p]))
        sys.stdout.flush()

    # wait here and join the processes
    for p in range(n_procs - 1):
        procs[p].join()

        if errors_dict[p] != "No error":
            raise Error(errors_dict[p])
        else:
            print("{0} Process {1} msg: {2}".format(INFO, p, msg_dict[p]))
            sys.stdout.flush()

    regions = []

    # now bring together the pieces of the regions
    for i, r in enumerate(regions_list):
        region = Region(idx=i, start=r[0],
                        end=r[1], window_size=configuration["window_size"])

        wga_windows = []
        no_wga_windows = []
        for p in range(n_procs):
            wga_windows.extend(windows_dict[i][p]["wga_windows"])
            no_wga_windows.extend(windows_dict[i][p]["no_wga_windows"])

        region.set_windows(wtype=WindowType.WGA, windows=wga_windows)

        if region.get_n_windows(type_=WindowType.WGA) == 0:
            raise Error("WGA windows have not been created")
        else:
            print("{0} Number of WGA "
                  "windows: {1}".format(INFO,
                                        region.get_n_windows(type_=WindowType.WGA)))
            sys.stdout.flush()

        region.set_windows(wtype=WindowType.NO_WGA, windows=no_wga_windows)

        if region.get_n_windows(type_=WindowType.NO_WGA) == 0:
            raise Error("Non-WGA windows have not  been created")
        else:
            print("{0} Number of Non WGA"
                  " windows: {1}".format(INFO,
                                         region.get_n_windows(type_=WindowType.NO_WGA)))
            sys.stdout.flush()

        regions.append(region)

    return regions
