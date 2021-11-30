"""
Extract the repeat sequence having a specified state
"""

import os
import csv
from compute_engine.src.constants import INFO
from compute_engine.src.utils import extract_sequences_from_bed_file_with_state


def extract_state_sequences_app_main(file_dir, file_pattern, state_name,
                                     delimiter, outfile_dir, outfilename):

    dir_list = os.listdir(file_dir)

    with open(outfile_dir + outfilename, 'w', newline='\n') as fh:

        file_writer = csv.writer(fh, delimiter=",")

        for directory_name in dir_list:

            if os.path.isdir(file_dir + directory_name):
                print("{0} processing directory {1}".format(INFO, directory_name))
                filenames = os.listdir(file_dir + directory_name)

                for i in range(len(filenames)):
                    filenames[i] = file_dir + directory_name + '/' + filenames[i] + '/' + file_pattern

                    print("{0} Working with filename={1}".format(INFO, filenames[i]))
                    seqs = extract_sequences_from_bed_file_with_state(filename=filenames[i], state_name=state_name,
                                                                      delimiter=delimiter)

                    print("{0} Number of sequences extracted={1}".format(INFO, len(seqs)))

                    for seq in seqs:
                        file_writer.writerow([seq])


if __name__ == '__main__':

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "tuf_sequences.csv"
    FILE_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/data/"
    FILE_PATTERN = 'nucl_out.bed'
    SEQUENCE_POSITION = 3
    STATE_NAME = 'TUF'
    STATE_POSITION = 4

    extract_state_sequences_app_main(file_dir=FILE_DIR, state_name=STATE_NAME,
                                     file_pattern=FILE_PATTERN, delimiter='\t',
                                     outfile_dir=OUTPUT_DIR,
                                     outfilename=OUTPUT_FILE)
