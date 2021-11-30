import array
from compute_engine.src.windows import WindowType, MixedWindowView, Window

from compute_engine.src.exceptions import Error
from compute_engine.src.preprocess_utils import remove_outliers, compute_statistic
from compute_engine.src.analysis_helpers import save_windows_statistic
from compute_engine.src.cengine_configuration import TREAT_ERRORS_AS_WARNINGS, PRINT_WARNINGS
from compute_engine.src.constants import WARNING, INFO


class RegionIterator(object):
    """
    Helper class to allow iteration over the window
    elements
    """

    def __init__(self, data):
        # data over which to iterate
        self._data = data

        # current index
        self._counter = 0

    def __next__(self):
        if self._counter < len(self._data):
            tmp = self._data[self._counter]
            self._counter += 1
            return tmp

        raise StopIteration


class Region(object):
    """
  A region is simply a collection
  of windows
  """

    @staticmethod
    def load(filename):

        print("{0} Loading region from file: {1}".format(INFO, filename))
        with open(filename, 'r') as f:

            idx = int(f.readline().split(":")[1].rstrip("\n"))
            start = int(f.readline().split(":")[1].rstrip("\n"))
            end = int(f.readline().split(":")[1].rstrip("\n"))
            w_size = int(f.readline().split(":")[1].rstrip("\n"))

            region = Region(idx=idx, start=start,
                            end=end, window_size=w_size)

            n_wag_wins = int(f.readline().split(":")[1].rstrip("\n"))
            windows = []
            for w in range(n_wag_wins):
                wid = int(f.readline().split(":")[1].rstrip("\n"))
                cap = int(f.readline().split(":")[1].rstrip("\n"))

                n_props = int(f.readline().split(":")[1].rstrip("\n"))
                samdata = {}
                for prop in range(n_props):
                    line = f.readline().split(":")
                    name = line[0]
                    val = line[1].rstrip("\n")

                    if val == 'False':
                        val = False
                    elif val == 'True':
                        val = True
                    else:
                        try:
                            val = float(val)
                        except:

                            if TREAT_ERRORS_AS_WARNINGS:

                                if PRINT_WARNINGS:
                                    print("{0} Could not float parse value {1} "
                                          "for name {2} and WGA window id {3}".format(WARNING, val, name, wid))
                                val = 0.0
                            else:
                                raise ValueError("Could not float parse value {0} "
                                      "for name {1} and WGA window id {2}".format(val, name, wid))

                    samdata[name] = val

                window = Window(idx=wid, capacity=cap, samdata=samdata)
                windows.append(window)

            region.set_windows(wtype=WindowType.WGA, windows=windows)
            n_no_wag_wins = int(f.readline().split(":")[1].rstrip("\n"))

            windows = []
            for w in range(n_no_wag_wins):
                wid = int(f.readline().split(":")[1].rstrip("\n"))
                cap = int(f.readline().split(":")[1].rstrip("\n"))

                n_props = int(f.readline().split(":")[1].rstrip("\n"))
                samdata = {}
                for prop in range(n_props):
                    line = f.readline().split(":")
                    name = line[0]
                    val = line[1].rstrip("\n")

                    if val == 'False':
                        val = False
                    elif val == 'True':
                        val = True
                    else:
                        try:
                            val = float(val)
                        except:
                            if TREAT_ERRORS_AS_WARNINGS:

                                if PRINT_WARNINGS:
                                    print("{0} Could not float parse value {1} "
                                          "for name {2} and NO-WGA window id {3}".format(WARNING, val, name, wid))
                                val = 0.0
                            else:
                                raise ValueError("Could not float parse value {0} "
                                      "for name {1} and NO-WGA window id {2}".format(val, name, wid))

                    samdata[name] = val

                window = Window(idx=wid, capacity=cap, samdata=samdata)
                windows.append(window)
            region.set_windows(wtype=WindowType.NO_WGA, windows=windows)
            return region

    def __init__(self, idx, start, end, window_size):

        if end <= start:
            raise Error("Invalid start/end points. "
                        "End cannot be less than or equal to start")

        self._idx = idx
        self._start = start
        self._end = end
        self._w_size = window_size
        self._windows = {WindowType.WGA: [],
                         WindowType.NO_WGA: []}

        self._mixed_windows = None

    @property
    def ridx(self):
        return self._idx

    @property
    def w_size(self):
        return self._w_size

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    def size(self):
        return self._end - self._start

    def get_n_windows(self, type_):
        if self._mixed_windows is not None:
            return len(self._mixed_windows)
        return len(self._windows[type_])

    def get_n_mixed_windows(self):
        if self._mixed_windows is None:
            return 0

        return len(self._mixed_windows)

    def save(self, path, filename, tips):

        #filename = "region_" + str(self.ridx)

        #filename_ = path + filename

        if tips is not None:
            for tip in tips:
                filename += "_" + tip

        filename += ".txt"

        with open(path + filename, 'w') as f:
            f.write("ID:" + str(self.ridx) + "\n")
            f.write("Start:" + str(self.start) + "\n")
            f.write("End:" + str(self.end) + "\n")
            f.write("WinSize:" + str(self.w_size) + "\n")

            f.write("WGA_N_WINDOWS:" + str(self.get_n_windows(type_=WindowType.WGA)) + "\n")

            for window in self._mixed_windows:
                wga_w = window.get_window(wtype=WindowType.WGA)
                f.write("WID:" + str(wga_w.idx) + "\n")
                f.write("Capacity:" + str(wga_w.capacity) + "\n")

                f.write("N props:" + str(len(wga_w.sam_property_names())) + "\n")
                for name in wga_w.sam_property_names():
                    f.write(name + ":" + str(wga_w.sam_property(name)) + "\n")

            f.write("NO_WGA_N_WINDOWS:" + str(self.get_n_windows(type_=WindowType.NO_WGA)) + "\n")
            for window in self._mixed_windows:
                no_wga_w = window.get_window(wtype=WindowType.NO_WGA)
                f.write("WID:" + str(no_wga_w.idx) + "\n")
                f.write("Capacity:" + str(no_wga_w.capacity) + "\n")

                f.write("N props:" + str(len(no_wga_w.sam_property_names())) + "\n")

                for name in no_wga_w.sam_property_names():
                    f.write(name + ":" + str(no_wga_w.sam_property(name)) + "\n")

    def count_gap_windows(self):

        counter = 0
        for win in self._mixed_windows:
            if win.is_gap_window():
                counter += 1

        return counter

    def set_windows(self, wtype, windows):

        if wtype != WindowType.WGA and \
                wtype != WindowType.NO_WGA:
            raise Error("Invalid Window type {0}"
                        " not in ['WGA', 'NO_WGA']".format(wtype))

        self._windows[wtype] = windows

    def make_wga_windows(self, chromosome,
                         ref_filename,
                         bam_filename, **kwargs):

        args = {"start_idx": self._start,
                "end_idx": self._end,
                "windowsize": self._w_size}

        if "debug" in kwargs:
            args["debug"] = kwargs["debug"]

        args["sam_read_config"] = kwargs["sam_read_config"]

        #windows = extract_windows(chromosome=chromosome,
        #                          ref_filename=ref_filename,
        #                          bam_filename=bam_filename,
        #                          **args)
        windows = []

        if len(windows) != 0:
            print("{0} Region Start Window "
                  "Coords: Start/End idx {1}".format(INFO, windows[0].start_end_pos))
            print("{0} Region End Window "
                  "Coords: Start/End idx {1}".format(INFO, windows[-1].start_end_pos))
        else:

            if TREAT_ERRORS_AS_WARNINGS:
                print("{0} WGA Windows were not  created ".format(INFO))
            else:
                raise Error("Empty WGA windows list")

        self._windows[WindowType.WGA] = windows

    def make_no_wga_windows(self, chromosome,
                            ref_filename,
                            bam_filename, **kwargs):

        args = {"start_idx": self._start,
                "end_idx": self._end,
                "windowsize": self._w_size}

        if "debug" in kwargs:
            args["debug"] = kwargs["debug"]

        args["sam_read_config"] = kwargs["sam_read_config"]

        #windows = extract_windows(chromosome=chromosome,
        #                          ref_filename=ref_filename,
        #                          bam_filename=bam_filename,
        #                          **args)

        windows = []

        if len(windows) != 0:
            print("{0} Region Start Window "
                  "Coords: Start/End idx {1}".format(INFO, windows[0].start_end_pos))
            print("{0} Region End Window "
                  "Coords: Start/End idx {1}".format(INFO, windows[-1].start_end_pos))
        else:

            if TREAT_ERRORS_AS_WARNINGS:
                print("{0} NO_WGA Windows were not  created ".format(INFO))
            else:
                raise Error("Empty NO WGA windows list")

        self._windows[WindowType.NO_WGA] = windows

    def check_windows_sanity(self):

        if len(self._windows[WindowType.NO_WGA]) > len(self._windows[WindowType.WGA]):
            print("{0} Windows size mismatch"
                  " WGA {1} NON_WGA {2}".format(WARNING,
                                                len(self._windows[WindowType.WGA]),
                                                len(self._windows[WindowType.NO_WGA])))
        elif len(self._windows[WindowType.NO_WGA]) < len(self._windows[WindowType.WGA]):
            print("{0} Windows size mismatch"
                  " WGA {1} NON_WGA {2}".format(WARNING,
                                                len(self._windows[WindowType.WGA]),
                                                len(self._windows[WindowType.NO_WGA])))

        # check if the rest of the windows
        # are aligned
        self.get_mixed_windows()

        for window in self._mixed_windows:
            start_wga, end_wga = window.get_window(wtype=WindowType.WGA).start_end_pos
            start_no_wga, end_no_wga = window.get_window(wtype=WindowType.NO_WGA).start_end_pos
            if (start_wga, end_wga) != (start_no_wga, end_no_wga):
                raise Error("Invalid window matching "
                            "window WGA at {0}, {1} "
                            "matched with NO WGA window at {2}, {3}".format(start_wga,
                                                                            end_wga,
                                                                            start_no_wga,
                                                                            end_no_wga))

    def get_mixed_windows(self):

        if self._mixed_windows is not None:
            return self._mixed_windows

        self._mixed_windows = []
        for win1, win2 in zip(self._windows[WindowType.WGA],
                              self._windows[WindowType.NO_WGA]):
            self._mixed_windows.append(MixedWindowView(wga_w=win1,
                                                       n_wga_w=win2))

        # we don't need these anymore
        # self._windows[WindowType.WGA] = None
        # self._windows[WindowType.NO_WGA] = None
        return self._mixed_windows

    def remove_windows_with_gaps(self):

        if self._mixed_windows is None:
            raise Error("Mixed windows have not been computed")

        mixed_windows = []
        for w in self._mixed_windows:

            if w.is_gap_window():
                continue
            mixed_windows.append(w)

        self._mixed_windows = mixed_windows

    def remove_windows_with_errors(self):

        if self._mixed_windows is None:
            raise Error("Mixed windows have not been computed")

        mixed_windows = []
        for w in self._mixed_windows:

            if w.is_error_window():
                continue
            mixed_windows.append(w)

        self._mixed_windows = mixed_windows

    def save_mixed_windows_gc_content(self, tips):
        if self._mixed_windows is None:
            raise Error("Mixed windows have not been computed")

        window_gc = \
            [window.get_gc_statistic(name=WindowType.WGA)
             for window in self._mixed_windows if not window.is_gap_window()]

        statistic = 'gc'
        filename = "windows_" + statistic + "_" + str(self.ridx)

        if tips is not None:
            for tip in tips:
                filename += "_" + tip
            filename += ".txt"
        else:
            filename = "windows_" + statistic

        with open(filename, 'w') as file:
            file.write(str(window_gc))

    def save_mixed_windows_statistic(self, statistic, tips):

        if self._mixed_windows is None:
            raise Error("Mixed windows have not been computed")

        save_windows_statistic(windows=self._mixed_windows,
                               statistic="mean", region_id=self._idx, tips=tips)

    def remove_outliers(self, configuration):

        if self._mixed_windows is None:
            raise Error("Mixed windows have not been computed")

        # compute the statistics
        wga_means = array.array('d')
        no_wga_means = array.array('d')

        for window in self._mixed_windows:
            if not window.is_gap_window():
                wga_means.append(window.get_rd_statistic(statistics="mean",
                                                         name=WindowType.WGA))
                no_wga_means.append(window.get_rd_statistic(statistics="mean",
                                                            name=WindowType.NO_WGA))

        if len(wga_means) == 0 or len(no_wga_means) == 0:
            print("{0} Cannot remove outliers for region. "
                  "Empty RD list detected".format(WARNING))
            return

        wga_statistics = compute_statistic(data=wga_means,
                                           statistics="all")
        no_wga_statistics = compute_statistic(data=no_wga_means,
                                              statistics="all")

        config = configuration["outlier_remove"]["config"]
        config["statistics"] = {WindowType.NO_WGA: no_wga_statistics,
                                WindowType.WGA: wga_statistics}

        self._mixed_windows = \
            remove_outliers(windows=self._mixed_windows,
                            removemethod=configuration["outlier_remove"]["name"],
                            config=config)

    def mark_windows_with_gaps(self, n_mark):

        if self._mixed_windows is None:
            raise Error("Mixed windows have not been computed")

        counter = 0
        for window in self._mixed_windows:
            wga_w = window.get_window(wtype=WindowType.WGA)
            n_wga_w = window.get_window(wtype=WindowType.NO_WGA)

            # Add error if one has gap and the other not
            if wga_w.has_gaps() == True and \
                    n_wga_w.has_gaps() == False:
                raise Error("WGA Window {0} has GAP "
                            "but Non WGA Window {1} does not".format(wga_w.idx,
                                                                     n_wga_w.idx))
            elif wga_w.has_gaps() == False and \
                    n_wga_w.has_gaps() == True:
                raise Error("WGA Window {0} does not have GAP "
                            "but Non WGA Window {1} does".format(wga_w.idx,
                                                                 n_wga_w.idx))

            if wga_w.has_gaps() or n_wga_w.has_gaps():
                wga_w.set_window_rd_mark(mark=n_mark)
                wga_w.state = WindowType.N_WIN

                n_wga_w.set_window_rd_mark(mark=n_mark)
                n_wga_w.state = WindowType.N_WIN
                counter += 1

        return counter

    def get_rd_mean_sequence(self, size, window_type, exclude_gaps):

        if self._mixed_windows is None:
            raise Error("Mixed windows have not been computed")

        sequence = []

        if size < len(self._mixed_windows):
            counter = 0
            for window in self._mixed_windows:

                if exclude_gaps and window.is_gap_window():
                    continue

                sequence.append(window.get_rd_statistic(statistics="mean",
                                                        name=window_type))
                counter += 1

                if counter == size:
                    break
        else:

            print("{0} Region size is less than {1}".format(WARNING, size))
            for window in self._mixed_windows:

                if exclude_gaps and window.is_gap_window():
                    continue
                sequence.append(window.get_rd_statistic(statistics="mean",
                                                        name=window_type))

        return sequence

    def get_region_as_rd_mean_sequences(self, size, window_type, n_seqs, exclude_gaps):

        if self._mixed_windows is None:
            raise Error("Mixed windows have not been computed")

        if size == None:
            # return the whole region
            sequences = []

            for window in self._mixed_windows:

                if exclude_gaps and window.is_gap_window():
                    continue

                sequences.append(window.get_rd_statistic(statistics="mean",
                                                         name=window_type))

            return sequences

        sequences = []
        sequence_local = []
        for window in self._mixed_windows:

            if exclude_gaps and window.is_gap_window():
                continue

            sequence_local.append(window.get_rd_statistic(statistics="mean",
                                                          name=window_type))

            if len(sequence_local) == size:
                sequences.append(sequence_local)
                sequence_local = []

            if n_seqs is not None and len(sequences) == n_seqs:
                break

        return sequences

    def get_region_as_rd_mean_sequences_with_windows(self, size, window_type,
                                                     n_seqs, exclude_gaps):

        if self._mixed_windows is None:
            raise Error("Mixed windows have not been computed")

        if size == None:
            # return the whole region
            sequences = []

            for window in self._mixed_windows:

                if exclude_gaps == True and window.is_gap_window():
                    continue

                sequences.append((window.get_rd_statistic(statistics="mean",
                                                          name=window_type), window.start_end_pos))

            return sequences

        sequences = []
        sequence_local = []
        for window in self._mixed_windows:

            if exclude_gaps and window.is_gap_window():
                continue

            sequence_local.append((window.get_rd_statistic(statistics="mean",
                                                           name=window_type),
                                   window.start_end_pos))

            if len(sequence_local) == size:
                sequences.append(sequence_local)
                sequence_local = []

            if n_seqs is not None and len(sequences) == n_seqs:
                break

        return sequences

    def __len__(self):
        return self.get_n_mixed_windows()

    def __iter__(self):
        return RegionIterator(data=self._mixed_windows)

    def __getitem__(self, item):
        return self._mixed_windows[item]

    def __setitem__(self, o, value):
        self._mixed_windows[o] = value
