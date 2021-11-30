import csv
import numpy as np
import pysam
import random

from compute_engine.src.utils import INFO
from compute_engine.apps.kde_approximation_app import app_kde_main


def extract_sequnece(fasta_file, chromosomes, length, chromosomes_lengths):

    # make a random choice for chromosome
    # and length
    chromosome = random.choice(chromosomes)
    #length = random.choice(lengths)

    end_points = chromosomes_lengths[chromosome]

    # select which bit to work on
    item = random.choice([0, 1])

    local_range = end_points[item]

    start = random.randint(local_range[0], local_range[1])
    end = start + length

    while end > local_range[1]:
        start = random.randint(local_range[0], local_range[1])
        end = start + length

    seq = fasta_file.fetch(chromosome, start, end)

    return seq


def extract_random_dna_sequences_app(data, kernel, bandwidth, chromosomes,
                                     chromosomes_lengths, fasta_file_name, save_sequence_file):

        kde_model = app_kde_main(data=data, kernel=kernel, bandwidth=bandwidth)

        print("{0} data shape={1}".format(INFO, data.shape))
        lengths = kde_model.sample(n_samples=data.shape[0]).flatten()

        # open the reference sequence file
        fasta_file = pysam.FastaFile(fasta_file_name)

        with open(save_sequence_file, 'w', newline='\n') as fh:

            filewriter = csv.writer(fh, delimiter=",")

            for i in range(len(lengths)):

                print("{0} Working with length index {1} out of {2}".format(INFO, i, len(lengths)))
                length = int(lengths[i]) #random.choice(lengths)
                seq = extract_sequnece(fasta_file=fasta_file,
                                       chromosomes=chromosomes, length=int(length),
                                       chromosomes_lengths=chromosomes_lengths)

                while seq == " " or len(seq) == 0 or "N" in seq or "n" in seq or len(seq) != int(length):
                    print("{0} Sequence={1} has length={2} and need {3}".format(INFO, seq, len(seq), int(length)))
                    seq = extract_sequnece(fasta_file=fasta_file,
                                           chromosomes=chromosomes, length=length,
                                           chromosomes_lengths=chromosomes_lengths)

                if seq == " " or len(seq) == 0 or "N" in seq or "n" in seq or len(seq) != int(length):
                    raise ValueError("Empty sequence string or sequence contains N")

                string_seq = ""
                for s in seq:
                    string_seq += s
                filewriter.writerow([string_seq])


if __name__ == '__main__':

    #OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/lengths/"
    #OUTPUT_FILE = "part-00000"

    INPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    INPUT_FILE = "deletion_sequences.csv"

    with open(INPUT_DIR + INPUT_FILE, 'r') as fh:
        reader = csv.reader(fh, delimiter=",")

        x = []

        counter = 0
        for line in reader:
            x.append(int(len(line[0])))
            counter += 1

        print("Number of items {0}".format(counter))

        new_data = np.array(x, dtype='U')
        new_data = new_data.reshape(-1, 1)

        chromosomes = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5',
                       'chr6', 'chr7', 'chr8', 'chr9', 'chr10',
                       'chr11', 'chr12']
        chromosomes_lengths = {"chr1": [(1, 119000000), (126000000, 248950000)],
                               "chr2": [(1, 90000000), (100000000, 242000000)],
                               "chr3": [(1, 87000000), (95000000, 198000000)],
                               "chr4": [(1, 47000000), (53000000, 190000000)],
                               "chr5": [(1, 45000000), (52000000, 181000000)],
                               "chr6": [(1, 57000000), (63000000, 170000000)],
                               "chr7": [(1, 57000000), (63000000, 159000000)],
                               "chr8": [(1, 42000000), (48000000, 145000000)],
                               "chr9": [(1, 41000000), (46000000, 138000000)],
                               "chr10": [(1, 37000000), (43000000, 133000000)],
                               "chr11": [(1, 50000000), (57000000, 135000000)],
                               "chr12": [(1, 33000000), (39000000, 133000000)],}

        extract_random_dna_sequences_app(data=new_data, kernel='gaussian',
                                         bandwidth=0.7, chromosomes=chromosomes,
                                         chromosomes_lengths=chromosomes_lengths,
                                         fasta_file_name="/home/alex/qi3/hmmtuf/data/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna",
                                         save_sequence_file="/home/alex/qi3/hmmtuf/computations/sequence_clusters/input/random_sequences_deletion.csv")
