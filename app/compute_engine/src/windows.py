from enum import Enum
from compute_engine.src.exceptions import Error

class WindowType(Enum):
    WGA = 0
    NO_WGA = 1
    BOTH = 2
    N_WIN = 3

    @staticmethod
    def from_string(string):
        if string.upper() == "WGA":
            return WindowType.WGA
        elif string.upper() == "NO_WGA":
            return WindowType.NO_WGA
        elif string.upper() == "BOTH":
            return WindowType.BOTH
        elif string.upper() == 'N_WIN':
            return WindowType.N_WIN

        raise Error("Invalid Window Type. "
                    "Type {0} not in {1}".format(string,
                                                 ["WGA",
                                                  "NO_WGA",
                                                  "BOTH",
                                                  "N_WIN"]))
    @staticmethod
    def get_window_types():
        return [WindowType.WGA.name, WindowType.NO_WGA.name,
                WindowType.BOTH.name, WindowType.N_WIN.name]

class WindowState(Enum):
    DELETE = 0
    ONE_COPY_DELETE = 1
    NORMAL = 2
    INSERTION = 3
    TUF = 4
    NOT_NORMAL = 5
    OTHER = 6
    INVALID = 7

    @staticmethod
    def from_string(string):
        if string.upper() == "DELETE":
            return WindowState.DELETE
        elif string.upper() == "ONE_COPY_DELETE":
            return WindowState.ONE_COPY_DELETE
        elif string.upper() == "NORMAL":
            return WindowState.NORMAL
        elif string.upper() == "INSERTION":
            return WindowState.INSERTION
        elif string.upper() == "TUF":
            return WindowState.TUF
        elif string.upper() == "OTHER":
            return WindowState.OTHER
        elif "STATE" in string.upper():
            return string

        raise Error("Invalid WindowState. "
                    "Type '{0}' not in {1}".format(string,
                                                   ["DELETE",
                                                    "ONE_COPY_DELETE",
                                                    "NORMAL",
                                                    "INSERTION", "TUF", "OTHER"]))


class Window(object):
    """
    Class representing a window for arranging of the data
    """

    __slots__ = ('_id', '_capacity', '_samdata', '_state')

    N_WINDOW_MARKER = -999

    @staticmethod
    def set_window_marker(marker):
        Window.N_WINDOW_MARKER = marker

    def __init__(self, idx, capacity, samdata):

        # the id of the window
        self._id = idx

        # maximum capacity of the window
        self._capacity = capacity

        # the data collected from the SAM file
        self._samdata = samdata

        # the state of the window
        self._state = WindowState.INVALID

    @property
    def idx(self):
        return self._id

    @property
    def start(self):
        return self._samdata["start"]

    @property
    def end(self):
        return self._samdata["end"]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def capacity(self):
        return self._capacity

    @property
    def start_end_pos(self):
        return self.sam_property("start"), self.sam_property("end")

    def sam_property_names(self):
        return self._samdata.keys()

    def sam_property(self, name):
        return self._samdata[name]

    def get_rd_statistic(self, statistic):

        if statistic == "mean":
            return self._samdata["qmean"]

        elif statistic == "median":
            self._samdata["qmedian"]

        raise Error("Statistic '{0}' is not currently "
                    "computed for Window".format(statistic))

    def get_gc_percent(self):
        return self._samdata["gcr"]

    def set_window_rd_mark(self, mark):
        Window.set_window_marker(marker=mark)

    def has_gaps(self):
        return self._samdata["gapAlert"]

    def has_errors(self):
        return self._samdata["errorAlert"]


class MixedWindowView(object):
    """
        Class that holds two instances of windows
    """

    __slots__ = ('_windows', '_state')

    def __init__(self, wga_w, n_wga_w):
        self._windows = {WindowType.WGA: wga_w,
                         WindowType.NO_WGA: n_wga_w}

        # the state of the window
        self._state = WindowState.INVALID

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def start_end_pos(self):
        return self._windows[WindowType.WGA].start_end_pos

    def is_gap_window(self):

        if self._windows[WindowType.WGA].has_gaps() or \
                self._windows[WindowType.NO_WGA].has_gaps():
            return True

        return False

    def is_error_window(self):
        if self._windows[WindowType.WGA].has_errors() or \
                self._windows[WindowType.NO_WGA].has_errors():
            return True

        return False

    def get_window(self, wtype):
        return self._windows[wtype]

    def get_features(self, features, name=WindowType.BOTH):

        if name == WindowType.BOTH:
            vals = []
            for feature in features:
                f1 = self.get_feature(feature=feature, name=WindowType.WGA)
                vals.append(f1)
                f2 = self.get_feature(feature=feature, name=WindowType.NO_WGA)
                vals.append(f2)
            return vals
        else:
            vals = []
            for feature in features:
                vals.append(self.get_feature(feature=feature, name=name))
            return vals

    def get_feature(self, feature, name=WindowType.BOTH):

        if feature == "mean":
            return self.get_rd_statistic(statistics=feature, name=name)
        elif feature == "gc":
            return self.get_gc_statistic(name=name)

        raise Error("Invalid feature '{0}' not in ['mean', 'gc']")

    def get_gc_statistic(self, name):
        if self.is_gap_window():
            if name == WindowType.BOTH:
                return (Window.N_WINDOW_MARKER, Window.N_WINDOW_MARKER)
            else:
                return Window.N_WINDOW_MARKER

        if name == WindowType.BOTH:
            return (self._windows[WindowType.WGA].get_gc_percent(),
                    self._windows[WindowType.NO_WGA].get_gc_percent())
        elif name == WindowType.WGA:
            return self._windows[WindowType.WGA].get_gc_percent()
        elif name == WindowType.NO_WGA:
            return self._windows[WindowType.NO_WGA].get_gc_percent()

        raise Error("Windowtype {0}"
                    " not in {1}".format(name, [WindowType.BOTH.name,
                                                WindowType.WGA.name,
                                                WindowType.NO_WGA.name]))

    def get_rd_statistic(self, statistics="all", name=WindowType.BOTH):
        """
        Returns a statistical summary as a dictionary
        of the read depth variable in the window
        :param statistics:
        :return:
        """

        wtype = name

        # attempt to convert from string
        if isinstance(wtype, str):
            wtype = WindowType.from_string(wtype)

        if self.is_gap_window():
            if wtype == WindowType.BOTH:
                return (Window.N_WINDOW_MARKER, Window.N_WINDOW_MARKER)
            else:
                return Window.N_WINDOW_MARKER

        if wtype == WindowType.BOTH:
            return (self._windows[WindowType.WGA].get_rd_statistic(statistic=statistics),
                    self._windows[WindowType.NO_WGA].get_rd_statistic(statistic=statistics))
        elif wtype == WindowType.WGA:
            return self._windows[WindowType.WGA].get_rd_statistic(statistic=statistics)
        elif wtype == WindowType.NO_WGA:
            return self._windows[WindowType.NO_WGA].get_rd_statistic(statistic=statistics)

        raise Error("Window type {0}"
                    " not in {1}".format(wtype, [WindowType.BOTH.name,
                                                WindowType.WGA.name,
                                                WindowType.NO_WGA.name]))
