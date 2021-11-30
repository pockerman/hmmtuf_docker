import json
from functools import wraps
import time
import os
from pathlib import Path
from zipfile import ZipFile

from compute_engine.src.constants import INFO, WARNING
from compute_engine.src.exceptions import Error

def timefn(fn):
    @wraps(fn)
    def measure(*args, **kwargs):
        time_start = time.perf_counter()
        result = fn(*args, **kwargs)
        time_end = time.perf_counter()
        print("{0} Done. Execution time"
              " {1} secs".format(INFO, time_end - time_start))
        return result

    return measure


def min_size_partition_range(start, end, minsize):

    if end <= start:
        raise Error("Range end cannot be smaller than start: {0} < {1}".format(end, start))

    if end - start <= minsize:
        return [(start, end)]

    chunks = []
    npieces = (end - start) // minsize

    start_c = start
    end_p = start_c + minsize
    for p in range(npieces - 1):
        chunks.append((start_c, end_p))
        start_c = end_p
        end_p += minsize

    chunks.append((start_c, end))
    return chunks

def partition_range(start, end, npieces):

    if npieces == 0:
        raise Error("Zero number of partitions")

    load = (end - start) // npieces

    chunks = []
    start_p = start
    end_p = start_p + load

    for p in range(npieces - 1):
        chunks.append((start_p, end_p))
        start_p = end_p
        end_p += load

    chunks.append((start_p, end))
    return chunks


def read_json(filename: Path) -> dict:

    """
    Read the json configuration file and
    return a map with the config entries
    """
    with open(filename) as json_file:
        json_input = json.load(json_file)
        return json_input

def find_smallest_sequence(seqs):

    min_size = len(seqs[list(seqs.keys())[0]])
    sequence = seqs[list(seqs.keys())[0]]
    for seq in seqs:
        if len(seqs[seq]) < min_size:
            min_size = len(seqs[seq])
            sequence = seqs[seq]
    return min_size, sequence

def chunck_sequence(seq, size):

    chuncks = []
    chunck_items = min_size_partition_range(start=0, end=len(seq), minsize=size)

    for chunck_item in chunck_items:
        start = chunck_item[0]
        end = chunck_item[1]

        cseq = ""
        for i in range(start, end, 1):
            cseq += seq[i]
        chuncks.append(cseq)
    return chuncks

def bisect_seqs(seqs, size):

    sequences = []
    for s in seqs:
        seq = seqs[s]

        if len(seq) > size:
            # break up the sequence into size chuncks
            sequences.extend(chunck_sequence(seq=seq, size=size))
        else:
            sequences.append(seq)

    return sequences


def sequence_length(seq):
    return len(seq)


def read_sequences_csv_file_line(line, delimiter=","):
    line_data = line.split(delimiter)
    return line_data[0], line_data[1]


def read_bed_file_line(line, extract_state=False, delimiter='\t'):
    """
    Read the given line and return the entries in a tuple
    (chromosome, start, end, seq)
    """
    line_data = line.split(delimiter)
    chromosome = line_data[0]
    start = int(line_data[1])
    end = int(line_data[2])
    seq = line_data[3]
    state = line_data[4]

    if extract_state:
        return chromosome, start, end, seq, state

    return chromosome, start, end, seq


def extract_sequences_from_bed_file_with_state(filename, state_name, delimiter):
    """
    Extract the sequence from the given file that has the
    state_name label
    """

    with open(filename, 'r') as fh:

        seqs = []
        for line in fh:
            chromosome, start, end, seq, state = read_bed_file_line(line=line, extract_state=True, delimiter=delimiter)

            state = state.strip("\n")
            if state == state_name:
                seqs.append(seq)

        return seqs


def read_bed_file(filename, concatenate):

    with open(filename, 'r') as fh:

        if concatenate:
            raise ValueError("Concatenation not implemented")
        else:
            seqs = dict()
            for line in fh:
                chromosome, start, end, seq = read_bed_file_line(line=line)

                if chromosome in seqs.keys():
                    seqs[chromosome].append((start, end, seq))
                else:
                    seqs[chromosome] = [(start, end, seq)]

            return seqs


def read_bed_files(file_dir, filenames, concatenate):

    dir_folder = Path(file_dir)

    if len(filenames) == 0:
        # get all filenames in the path
        filenames = os.listdir(path=dir_folder)

    if len(filenames) == 0:
        raise ValueError("Empty bed files list")

    print("{0} Processing bed files in {1}".format(INFO, file_dir))
    print("{0} Number of bed files given {1}".format(INFO, len(filenames)))

    if not concatenate:

        seqs_dict = dict()

        for filename in filenames:

            print("{0} Processing {1}".format(INFO, filename))

            seqs = read_bed_file(filename=dir_folder / filename, concatenate=concatenate)

            if len(seqs.keys()) == 0:
                print("{0} filename is empty".format(WARNING, filename))
                continue

            chr_key = list(seqs.keys())[0]
            seqs = seqs[chr_key]

            for seq in seqs:
                counter = 0
                save_name = filename + '_' + chr_key + '_' + str(seq[0]) + '_' + str(seq[1]) + '_' + str(counter)

                if save_name not in seqs_dict:
                    seqs_dict[save_name] = seq[2]
                else:
                    counter += 1
                    save_name = filename + '_' + chr_key + '_' + str(seq[0]) + '_' + str(seq[1]) + '_' + str(counter)
                    while save_name in seqs_dict:
                        print("WEIRD: ", filename, save_name)

                        counter += 1
                        save_name = filename + '_' + chr_key + '_' + \
                                    str(seq[0]) + '_' + \
                                    str(seq[1]) + '_' + str(counter)

                    seqs_dict[save_name] = seq[2]

        return seqs_dict
    else:
        raise ValueError("Concatenation not implemented")


def compute_textdistances(sequences, distance_type,
                          build_from_factory, compute_self_distances):
    """
    Compute the the pair-wise distance of the given sequences using
    the given distance type. If compute_self_distances=True it also
    computes the self distance
    """

    if build_from_factory:
        #calculator = build_calculator(distance_type=distance_type)
        raise ValueError("Building from factory not implemented")
    else:
        calculator = distance_type

    similarity_map = dict()
    if isinstance(sequences, dict):

        seq_names = sequences.keys()

        for i, name1 in enumerate(seq_names):
            for j, name2 in enumerate(seq_names):

                if compute_self_distances:

                    if (name1, name2) not in similarity_map and (name2, name1) not in similarity_map:
                        result = calculator.similarity(sequences[name1], sequences[name2])
                        similarity_map[name1, name2] = result
                else:

                    if (name1, name2) not in similarity_map and (name2, name1) not in similarity_map and i != j:
                        result = calculator.similarity(sequences[name1], sequences[name2])
                        similarity_map[name1, name2] = result

    else:

        for i, name1 in enumerate(sequences):
            for j, name2 in enumerate(sequences):

                if compute_self_distances:
                    if (name1, name2) not in similarity_map and (name2, name1) not in similarity_map:
                        result = calculator.similarity(name1, name2)
                        similarity_map[name1, name2] = result
                else:

                    if (name1, name2) not in similarity_map and (name2, name1) not in similarity_map and i != j:
                        result = calculator.similarity(name1, name2)
                        similarity_map[name1, name2] = result

    return similarity_map


def get_sequence_chunks(cseq, chunk_size):
    """
    Given a sequence split it into chunks of
    size chunk_size each
    """
    return [cseq[i:i + chunk_size] for i in range(0, len(cseq), chunk_size)]

def get_range_chunks(start, end, chunk_size):
    """
    Given a range [start, end) partition it
    into chunks for chunk_size
    """

    if end - start <= chunk_size:
        return [(start, end)]

    chunks = [[i, i + chunk_size] for i in range(0, end, chunk_size)]

    chunks[-1][1] -= 1
    return chunks

def extract_file_names(configuration):
    """
    Given the configuration map extract the
    filenames related to the reference file
    the WGA files and the non WGA files
    """

    reference_files_names = []
    wga_files_names = []
    nwga_files_names = []
    files = configuration["sequence_files"]["files"]

    for idx in range(len(files)):
        map = files[idx]
        ref_files = map["ref_files"]
        reference_files_names.extend(ref_files)

        wga_files = map["wga_files"]
        wga_files_names.extend(wga_files)

        nwga_files = map["no_wga_files"]
        nwga_files_names.extend(nwga_files)

    return reference_files_names, wga_files_names, nwga_files_names


def extract_path(configuration, ref_file):
    files = configuration["sequence_files"]["files"]

    for idx in range(len(files)):
        map = files[idx]
        ref_files = map["ref_files"]

        if ref_file in ref_files:
            return map["path"]
    return None


def get_sequence_name(configuration, seq):
    return configuration["sequences_names"][seq]


def get_tdf_file(configuration, seq):
    return configuration["tdf_files"][seq]


def read_sequence_bed_file(filename, delim='\t'):

    sequence = ''
    with open(filename, 'r') as f:
        for line in f:
            line = line.split(delim)
            sequence += line[-1].strip('\n')

    return sequence


def to_csv_line(data):
    """
    Convert the data to comma separated string
    """

    if isinstance(data, float):
        return str(data)

    if isinstance(data, int):
        return str(data)

    return ','.join(str(d) for d in data)


def count_kmers(sequence, k):
    """
    This function is taken from:
    http://claresloggett.github.io/python_workshops/improved_kmers.html
    see also
    http://claresloggett.github.io/python_workshops/kmer_counting.html
    Count kmer occurrences in a given read.

    Parameters
    ----------
    read : string
        A single DNA sequence.
    k : int
        The value of k for which to count kmers.

    Returns
    -------
    counts : dictionary, {'string': int}
        A dictionary of counts keyed by their individual kmers (strings
        of length k).

    Examples
    --------
    >>> count_kmers("GATGAT", 3)
    {'ATG': 1, 'GAT': 2, 'TGA': 1}
    """
    # Start with an empty dictionary
    counts = {}

    # Calculate how many kmers of length k there are
    num_kmers = len(sequence) - k + 1

    # Loop over the kmer start positions
    for i in range(num_kmers):
        # Slice the string to get the kmer
        kmer = sequence[i:i+k]

        # Add the kmer to the dictionary if it's not there
        if kmer not in counts:
            counts[kmer] = 0
        # Increment the count for this kmer
        counts[kmer] += 1
    # Return the final counts
    return counts


def get_max_kmers(kmers, min_count):
    """
    Returns the min_count max kmers.
    If min_count is 'all' all the
    soreted kmers is returned. If as_percentage is True
    then it returns the max_kmers in terms of percentages
    """

    # sort the dictionary
    sorted_kmers = {k: v for k, v in sorted(kmers.items(), key=lambda item: item[1], reverse=True)}

    if min_count == 'all':
        return sorted_kmers

    # the returned top kmers
    top_kmers = dict()

    counter = 0
    for item in sorted_kmers:

        if counter < min_count:
            top_kmers[item] = sorted_kmers[item]
            counter += 1
        else:
            break

    return top_kmers

def type_converter(data, type_converter):
    """
    Return the data converted into the type
    denoted by the string type_converter
    """

    if type_converter == "FLOAT":
        return float(data)
    elif type_converter == "INT":
        return int(data)
    elif type_converter == "STRING":
        return str(data)

    raise ValueError("Unknown type_converter={0}".format(type_converter))


def load_data_file(filename, type_convert):
    """
    Loads a .txt data file into an array. Every
    item is converted according to type_convert
    """
    with open(filename) as file:
        context = file.read()
        size = len(context)
        arraystr= context[1:size-1]
        arraystr = arraystr.split(',')
        region_means = [type_converter(data=item, type_converter="FLOAT") for item in arraystr]
        return region_means


def make_data_array(wga_mu, no_wga_mu, gc, use_ratio, use_gc):
    """
    Using the two data arrays returns an array as pairs.

    If gc array is also supplied and use_gc=True then
    returns a array containing the tripplets.

    If use_ratio=True then it returns the trippler
    [no_wga, wga, (wga + 1) / (no_wga + 1)]

    if use_ratio=True and use_gc=True
    it returns the quatruplet
    [no_wga_val, wga_val, (wga_val + 1) / (no_wga_val + 1), gc_val]
    in this case gc should not be None

    """

    if len(no_wga_mu) != len(wga_mu):
        raise ValueError("Invalid data size")

    data = []

    if use_ratio and use_gc:

        if gc is None or len(gc) == 0:
            raise  ValueError("GC array is either None or empty")

        if len(gc) != len(no_wga_mu):
            raise ValueError("GC array size={0} is not equal to {1}".format(len(gc), len(no_wga_mu)))

        for no_wga_val, wga_val, gc_val in zip(no_wga_mu, wga_mu, gc):
            data.append([no_wga_val, wga_val, (wga_val + 1) / (no_wga_val + 1), gc_val])
    elif use_ratio:
        for no_wga, wga in zip(no_wga_mu, wga_mu):
            data.append([no_wga, wga, (wga + 1) / (no_wga + 1)])
    elif use_gc:

        if gc is None:
            raise ValueError("GC array is None")

        if gc is None or len(gc) != len(no_wga_mu):
            raise ValueError("GC array size={0} is not equal to {1}".format(len(gc), len(no_wga_mu)))

        for no_wga_val, wga_val, gc_val in zip(no_wga_mu, wga_mu, gc):
            data.append([no_wga_val, wga_val, gc_val])
    else:

        for no_wga, wga in zip(no_wga_mu, wga_mu):
            data.append([no_wga, wga])

    return data

def unzip_file(input_dir: Path, member: str, output_dir: Path) -> None:
    """
    Extract a member from the archive to the current working directory;
    """

    with ZipFile(input_dir / member, 'r') as zip:
        zip.extractall(path=output_dir)

def unzip_files(data_dir: Path, output_dir: Path) -> None:

    # get all the directories in the path
    data_directories = os.listdir(path=data_dir)

    for member in data_directories:
        if member.endswith(".zip"):
            unzip_file(input_dir=data_dir, member=member, output_dir=output_dir)

def file_chunks(data_file, rows: int=10000):
    """
    Divides the data into 10000 rows each
    """

    for i in range(0, len(data_file), rows):
        yield data_file[i:i+rows]










