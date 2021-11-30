import csv
import numpy as np
import ipyparallel as ipp

from compute_engine.src.constants import INFO
from compute_engine.src.utils import to_csv_line
from compute_engine.src.string_sequence_calculator import TextDistanceCalculator
from compute_engine.src.file_readers import NuclOutSeqFileReader
from compute_engine.src.file_creator import FileCreator



def compute_sequences_cartesian_product(sequences):

    cartesian_product = []

    for i in range(len(sequences)):
        for j in range(len(sequences)):
            if i != j:
                cartesian_product.append((sequences[i], sequences[j]))
    return cartesian_product


def compute_distances(distance_type, sequences, use_partial_sums=True,
                      store_average_length=False, store_total_length=False):

    if store_average_length and store_total_length:
        raise ValueError("Cannot save both average length and total length")

    calculator = TextDistanceCalculator.build_calculator(name=distance_type)

    if distance_type == 'CPF':
        calculator._use_probability_counts_and_remove_zeros = True

    distances = []
    if store_average_length:

        for item in sequences:
            distances.append((np.mean([len(item[0]), len(item[1])]),
                              calculator.similarity(item[0], item[1])))

    else:

        for item in sequences:
            distances.append(calculator.similarity(item[0], item[1]))
    return distances


def save_distances(filename, distances):

    with open(filename, 'w', newline="\n") as fh:
        writer = csv.writer(fh, delimiter=",")
        dim = len(distances[0])
        for item in distances:

            if dim == 1:
                writer.writerow([item])
            else:
                writer.writerow(item)


def compute_distances(distance_type, input_file, outfile):
    import sys

    if "/home/alex/qi3/hmmtuf" not in sys.path:
        sys.path.append("/home/alex/qi3/hmmtuf")

    # typical import for spawned processes
    from compute_engine.src.string_sequence_calculator import TextDistanceCalculator
    from compute_engine.src.file_readers import NuclOutSeqFileReader

    # build the wrapper
    calculator = TextDistanceCalculator(dist_type=distance_type)

    filereader = NuclOutSeqFileReader(exclude_seqs=["NO_REPEATS"])
    distances = calculator.calculate_from_file(filename=input_file,
                                               file_reader=filereader,
                                               **{"print_info": True})

    with open(outfile, 'w') as fh:

        for dist in distances:
            line = dist[0] + "," + dist[1] + "," + str(float(distances[dist]))
            fh.write(line)

    return True



def compute_distances_app_main(distance_type, input_dir, filename):
    # how many processes we have available
    rc = ipp.Client()
    view = rc[:]
    view.block = False
    print("{0} # of engines used={1}".format(INFO, len(view)))
    # file_creator = FileCreator()
    # file_creator.segragate_nucl_out_file(filename=input_dir + filename,
    #                                     lines_per_file=300,
    #                                     out_file_name="temp_sequences",
    #                                     suffix=".bed",
    #                                     output_dir="/home/alex/qi3/hmmtuf/computations/tmp/")

    # view = rc.load_balanced_view()
    rs1 = view.apply_async(compute_distances,
                           distance_type,
                           "/home/alex/qi3/hmmtuf/computations/tmp/temp_sequences_300.bed",
                           "/home/alex/qi3/hmmtuf/computations/tmp/temp_sequences_300_out.bed")

    rs2 = view.apply_async(compute_distances,
                           distance_type,
                           "/home/alex/qi3/hmmtuf/computations/tmp/temp_sequences_600.bed",
                           "/home/alex/qi3/hmmtuf/computations/tmp/temp_sequences_600_out.bed")

    rs3 = view.apply_async(compute_distances,
                           distance_type,
                           "/home/alex/qi3/hmmtuf/computations/tmp/temp_sequences_900.bed",
                           "/home/alex/qi3/hmmtuf/computations/tmp/temp_sequences_900_out.bed")

    rs4 = view.apply_async(compute_distances,
                           distance_type,
                           "/home/alex/qi3/hmmtuf/computations/tmp/temp_sequences_1200.bed",
                           "/home/alex/qi3/hmmtuf/computations/tmp/temp_sequences_1200_out.bed")

    print("Block to get the result...")
    print("Process {0}  finished {1}".format(INFO, rs1.get()))
    print("Process {0}  finished {1}".format(INFO, rs2.get()))
    print("Process {0}  finished {1}".format(INFO, rs3.get()))
    print("Process {0}  finished {1}".format(INFO, rs4.get()))



if __name__ == '__main__':

    APP_NAME = "ComputeDistancesApp"
    print("{0} Running {1} application".format(INFO, APP_NAME))

    DISTANCE_TYPE = "ham"
    INPUT_DIR = "/home/alex/qi3/hmmtuf/computations/viterbi_paths/chr1/chr1/"
    FILENAME = 'nucl_out.bed'

    #file_creator = FileCreator()
    #file_creator.append_nucl_out_files("/home/alex/qi3/hmmtuf/computations/viterbi_paths/",
    #                                   "/home/alex/qi3/hmmtuf/computations/tmp/nucl_out.bed",)
    compute_distances_app_main(distance_type=DISTANCE_TYPE,
                               input_dir=INPUT_DIR,
                               filename=FILENAME)

    print("{0} Done with application {1}".format(INFO, APP_NAME))

