"""
Utility functions for reading various
.bed files generated from SPADE processing
"""

import csv
import json
from pathlib import Path
from typing import List, Tuple

from compute_engine.src.enumeration_types import FileReaderType
from compute_engine.src.exceptions import IndexExists, InvalidReadingMode, InvalidFileFormat

def read_line_nucl_out_file(line: str, delimiter='\t') -> tuple:
    line_data = line.split(delimiter)
    chromosome = line_data[0]
    start = int(line_data[1])
    end = int(line_data[2])
    seq = str(line_data[3])
    state = str(line_data[4].rstrip("\n"))
    return chromosome, start, end, seq, state

def read_sequence_from_nucl_out_file(filename: str, exclude_seqs: list, delimiter: str='\t') -> list:

    with open(filename, 'r', newline="\n") as fh:
        seqs = []

        for line in fh:
            chromosome, start, end, seq, state = read_line_nucl_out_file(line=line, delimiter=delimiter)

            if seq not in exclude_seqs:
                seqs.append(seq)

        return seqs
"""
def read_nucl_out_file(filename: str, exclude_seqs: list=["NO_REPEATS"], delimiter: str='\t'):

    with open(filename, 'r', newline="\n") as fh:
        seqs = []

        for line in fh:
            chromosome, start, end, seq, state = read_line_nucl_out_file(line=line, delimiter=delimiter)

            if seq not in exclude_seqs:
                seqs.append([chromosome, start, end, seq, state])

        return seqs
"""


class CsvFileReader(object):

    def __init__(self, delimiter: str=',') -> None:
        self._delimiter = delimiter


    @property
    def delimiter(self)-> str:
        return self._delimiter

    def __call__(self, filename: Path) -> list:
        with open(filename, 'r', newline="\n") as fh:
            reader = csv.reader(fh, delimiter=self._delimiter)

            lines = []

            for line in reader:
                lines.append(line)
            return lines



class DeaultReader(object):

    def __init__(self) -> None:
        pass

    def read_default(self, filename: Path) -> List[str]:

        with open(filename, 'r', newline="\n") as fh:
            lines = []

            for line in fh:
                lines.append(line)
            return lines

    def read_with_delimiter_strip(self, filename: Path, delimiter: str) -> list:
        lines = self.read_default(filename=filename)

        stripped_lines = []

        for line in lines:

            line_data = line.split(delimiter)
            stripped_lines.append(line_data)
        return stripped_lines


class ViterbiPathReader(DeaultReader):

    def __init__(self, mode):
        self._mode = mode

    def __call__(self, filename: Path):

        if self._mode == 'default':
            return self.read_default(filename=filename)
        elif self._mode == 'dict_coords_state':
            return self.read_dict_coords_state(filename=filename)
        else:
            raise InvalidReadingMode(mode=self._mode, values=['default', 'dict_coords_state'])


    def read_dict_coords_state(self, filename: Path) -> dict:

        with open(filename, 'r', newline='\n') as fh:
            reader = csv.reader(fh, delimiter=':')
            result = dict()

            for line in reader:

                if len(line) != 5:
                    continue

                chromosome = line[0]
                indexes = line[2].split(",")
                indexes[0] = int(indexes[0].strip("(").strip())
                indexes[1] = int(indexes[1].strip(")").strip())

                if (chromosome, indexes[0], indexes[1]) in result:
                    raise IndexExists(index=(chromosome, indexes[0], indexes[1]))

                result[(chromosome, indexes[0], indexes[1])] = line[4].strip()

            return result

class CoordsBedFile(DeaultReader):
    def __init__(self, mode: str='default', delimiter: str="\t") -> None:
        super(CoordsBedFile, self).__init__()
        self._mode = mode
        self._delimiter = delimiter

    def __call__(self, filename: Path) -> list:
        if self._mode == 'default':
            return self.read_default(filename=filename)
        elif self._mode == 'tuple_list':
            return self.read_tuple_list(filename=filename)
        else:
            raise InvalidReadingMode(mode=self._mode, values=['default', 'tuple_list'])

    def read_tuple_list(self, filename: Path) -> list:

        with open(filename, 'r', newline='\n') as fh:
            reader = csv.reader(fh, delimiter=self._delimiter)
            result = []

            for line in reader:
                if len(line) != 3:
                    raise InvalidFileFormat(filename=str(filename) + "offending line={}".format(line))

                result.append([line[0], int(line[1].strip()), int(line[2].strip())])

            return result



class NuclOutFileReader(DeaultReader):

    def __init__(self, exclude_seqs: list=["NO_REPEATS"],
                 delimiter: str='\t', strip: bool=True) -> None:
        super(NuclOutFileReader, self).__init__()

        self._delimiter = delimiter
        self._exclude_seqs = exclude_seqs
        self._strip = strip

    def __call__(self, filename: Path) -> List:
        """
        Returns either a list of strings when self._strip = False
        or a list of lists when self._strip = True
        """

        if not self._strip:
            return self.read_default(filename=filename)
        else:
            return self._read_strip(filename=filename)

    def _read_strip(self, filename: Path) -> List[List]:

        with open(filename, 'r', newline="\n") as fh:
            lines = []

            for line in fh:
                line_data = line.split("\t")

                for i in range(len(line_data)):
                    line_data[i] = line_data[i].strip()

                if line_data [3] not in self._exclude_seqs:
                    lines.append(line_data)
            return lines



class NuclOutSeqFileReader(object):

    def __init__(self, exclude_seqs: list, delimiter: str='\t') -> None:
        self._delimiter = delimiter
        self._exclude_seqs = exclude_seqs

    def __call__(self, filename: Path) -> list:
        return read_sequence_from_nucl_out_file(filename=filename,
                                                exclude_seqs=self._exclude_seqs,
                                                delimiter=self._delimiter)

class NuclMissingOutFileReader(CsvFileReader):

    def __init__(self, delimiter: str=',', strip: bool=False) -> None:
        super(NuclMissingOutFileReader, self).__init__(delimiter)
        self._strip = strip

    def __call__(self, filename: Path) -> list:

        if not self._strip:
            return super(NuclMissingOutFileReader, self).__call__(filename=filename)
        else:
            lines = super(NuclMissingOutFileReader, self).__call__(filename=filename)

            stripped_lines = []

            for line in lines:
                line_data = line

                assert len(line_data) == 8, f"Invalid file format length " \
                                            f"of line is {len(line_data)} should have been 8"

                line_data[1] = int(line_data[1])
                line_data[2] = int(line_data[2])
                line_data[5] = float(line_data[5])
                line_data[6] = float(line_data[6]) if line_data[6] != 'NA' else line_data[5]
                line_data[7] = float(line_data[7]) if line_data[7] != 'NA' else line_data[5]
                stripped_lines.append(line_data)
            return stripped_lines


class GQuadsFileReader(DeaultReader):

    def __init__(self, read_as_dict: bool=False) -> None:
        super(GQuadsFileReader, self).__init__()
        self._read_as_dict = read_as_dict

    def __call__(self, filename: Path):
        """
        Returns either a list of strings self._read_as_dict = False
        or a dictionary with key (chromosome, start, end) when
        self._read_as_dict = True
        """

        if not self._read_as_dict:
            return self.read_default(filename=filename)
        else:
            return self.read_as_dict(filename=filename)

    def read_as_dict(self, filename: Path) -> dict:
        with open(filename, 'r', newline='\n') as fh:

            data_dir = dict()
            for line in fh:
                data = line.split(":")
                region = data[1].split("\t")
                has_gcquad = False
                if 'True' in region[1]:
                    has_gcquad = True

                region_data = region[0].split('_')
                start_end = region_data[0].split('-')

                chromosome = str(data[0])
                start = int(start_end[0])
                end = int(start_end[1])

                gc_avg = float(region_data[2])
                gc_min = region_data[3]
                gc_max = region_data[4]

                if gc_min == 'NA':
                    gc_min = gc_avg
                else:
                    gc_min = float(gc_min)

                if gc_max == 'NA':
                    gc_max = gc_avg
                else:
                    gc_max = float(gc_max)

                if (chromosome, start, end) in data_dir:
                    values = data_dir[(chromosome, start, end)]
                    if values[0] != gc_avg or values[1] != gc_min or values[2] != gc_max:
                        raise ValueError("key {0} already exists but values not equal")
                    else:
                        continue
                else:
                    data_dir[(chromosome, start, end)] = [gc_avg, gc_min, gc_max, has_gcquad]

            return data_dir

class RepeatsInfoFileReader(DeaultReader):

    def __init__(self, read_as_dict: bool=False) -> None:
        self._read_as_dict = read_as_dict

    def __call__(self, filename: Path) -> list:

        if not self._read_as_dict:
            return self.read_default(filename=filename)
        else:
            return self.read_as_dict(filename=filename)

    def read_as_dict(self, filename: Path) -> dict:
        with open(filename, 'r', newline='\n') as fh:

            data_dir = dict()
            for line in fh:
                data = line.split("\t")

                chromosome = str(data[0])
                start = int(data[1])
                end = int(data[2])

                key = (chromosome, start, end)
                n_repeats = int(data[3])
                seq1 = str(data[4].strip())
                seq2 = str(data[5].strip())

                if key in data_dir:
                    data_dir[key].append([n_repeats, seq1, seq2])
                else:
                    data_dir[key] = [[n_repeats, seq1, seq2]]

            return data_dir
            
            
class TufFileReader(DeaultReader):

    def __init__(self, mode: str='default', delimiter: str="\t") -> None:
        super(TufFileReader, self).__init__()
        self._mode = mode
        self._delimiter = delimiter
		
    def __call__(self, filename: Path) -> list:

        if self._mode == 'default':
            return self.read_default(filename=filename)
        elif self._mode == 'strip':
            return self.read_with_delimiter_strip(filename=filename, delimiter=self._delimiter)
        else:
            raise InvalidReadingMode(mode=self._mode, values=['default', 'strip'])
		

class DeletionFileReader(TufFileReader):
    def __init__(self, mode: str='default', delimiter="\t") -> None:
        super(DeletionFileReader, self).__init__(mode=mode, delimiter=delimiter)


class DuplicationFileReader(TufFileReader):
    def __init__(self, mode: str='default', delimiter="\t") -> None:
        super(DuplicationFileReader, self).__init__(mode=mode)


class GapFileReader(TufFileReader):
    def __init__(self, mode: str='default') -> None:
        super(GapFileReader, self).__init__(mode=mode)


class NormalFileReader(TufFileReader):
    def __init__(self, mode: str='default', delimiter="\t") -> None:
        super(NormalFileReader, self).__init__(mode=mode)


class TdtFileReader(TufFileReader):
    def __init__(self, mode: str='default') -> None:
        super(TdtFileReader, self).__init__(mode=mode)


class QuadFileReader(TufFileReader):
    def __init__(self, mode: str='default') -> None:
        super(QuadFileReader, self).__init__(mode=mode)


class RepFileReader(TufFileReader):
    def __init__(self, mode: str='default') -> None:
        super(RepFileReader, self).__init__(mode=mode)


class ViterbiBedGraphReader(TufFileReader):
    def __init__(self, mode: str='default') -> None:
        super(ViterbiBedGraphReader, self).__init__(mode=mode)


class JsonReader(object):
    def __init__(self) -> None:
        pass

    def __call__(self, filename: Path) -> dict:
        """
        Read the json configuration file and
        return a map with the config entries
        """
        with open(filename) as json_file:
            json_input = json.load(json_file)
            return json_input


class FileReaderFactory(object):
    def __init__(self, reader_type: FileReaderType, mode: str) -> None:
        self._reader_type = reader_type
        self._mode = mode

    def __call__(self, filename: Path, **kwargs):

        if self._reader_type == FileReaderType.TUF_BED:
            reader = TufFileReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.DELETION_BED:
            reader = DeletionFileReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.DUPLICATION_BED:
            reader = DuplicationFileReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.GAP_BED:
            reader = GapFileReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.NORMAL_BED:
            reader = NormalFileReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.TDT_BED:
            reader = TdtFileReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.VITERBI_BED_GRAPH:
            reader = ViterbiBedGraphReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.QUAD_BED:
            reader = QuadFileReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.REP_BED:
            reader = RepFileReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.REPEATS_INFO_BED:
            reader = RepeatsInfoFileReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.GQUADS:
            reader = GQuadsFileReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.NUCL_OUT:
            reader = NuclOutFileReader(mode=mode, exclude_seqs=kwargs["exclude_seqs"] if "exclude_seqs" in kwargs else [])
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.VITERBI_PATH:
            reader = ViterbiPathReader(mode=mode)
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.NUCL_OUT_MISSING:
            reader = NuclMissingOutFileReader()
            return reader(filename=filename)
        else:
            raise ValueError("Unknown FileReaderType={0}".format(self._reader_type))





