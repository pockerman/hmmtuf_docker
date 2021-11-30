from pathlib import Path
from compute_engine.src.file_readers import ViterbiPathReader, CoordsBedFile


def search_with_step_size(viterbi_filename: Path, bed_file: Path, step_size: int) -> None:

    if step_size < 1:
        raise ValueError("Invalid step size")

    viterbi_reader = ViterbiPathReader(mode='dict_coords_state')
    values = viterbi_reader(filename=viterbi_filename)
    bed_coords_reader = CoordsBedFile(mode='tuple_list')
    bed_coords = bed_coords_reader(filename=bed_file)

    state_counters = dict()
    state_counters['TUF'] = 0
    state_counters['OTHER'] = 0
    not_found = []

    for item in bed_coords:

        chromosome = item[0]
        start = item[1]
        end = item[2]

        if start >= end:
            raise ValueError("Invalid start/end indexes {0}/{1}".format(start, end))

        ranges = [(i, i + step_size -1 ) for i in range(start, end + 1 , step_size)]

        if start == 2124100:
            print(ranges)

        if len(ranges) == 0:
            raise ValueError("Empty ranges")

        for item in ranges:

            if tuple((chromosome, item[0], item[1])) in values:
                if values[(chromosome, item[0], item[1])] == 'TUF':
                    state_counters['TUF'] += 1
                else:
                    state_counters['OTHER'] += 1
            else:
                not_found.append((chromosome, item[0], item[1]))

    print(state_counters)
    print(len(not_found))
    print(not_found)


def search_default(viterbi_filename: Path, bed_file: Path) -> None:
    viterbi_reader = ViterbiPathReader(mode='dict_coords_state')
    values = viterbi_reader(filename=viterbi_filename)
    bed_coords_reader = CoordsBedFile(mode='tuple_list')
    bed_coords = bed_coords_reader(filename=bed_file)

    state_counters = dict()
    state_counters['TUF'] = 0
    state_counters['OTHER'] = 0

    not_found = []

    for item in bed_coords:

        if tuple(item) in values:
            if values[tuple(item)] == 'TUF':
                state_counters['TUF'] += 1
            else:
                state_counters['OTHER'] += 1
        else:
            not_found.append(item)

    print(state_counters)
    print(len(not_found))

def main(viterbi_filename: Path, bed_file: Path, step_size: int) -> None:

    if step_size <=0:
        search_default(viterbi_filename=viterbi_filename, bed_file=bed_file)
    else:
        search_with_step_size(viterbi_filename=viterbi_filename,
                              bed_file=bed_file, step_size=step_size)



if __name__ == '__main__':

    viterbi_filename = Path('/home/alex/qi3/hmmtuf/computations/viterbi_paths/chr1/chr1/region_1_chr1/viterbi_path.csv')
    bed_filename = Path('/home/alex/qi3/hmmtuf/computations/viterbi_paths/chr1/chr1/region_1_chr1/tuf.bed')
    step_size = 100
    main(viterbi_filename=viterbi_filename, bed_file=bed_filename, step_size=step_size)