import csv
import numpy as np
from pathlib import Path
import os

from compute_engine.src.constants import INFO
from compute_engine.src.file_readers import NuclOutFileReader, GQuadsFileReader, RepeatsInfoFileReader
from compute_engine.src.file_readers import FileReaderFactory
from compute_engine.src.enumeration_types import FileReaderType


def tuf_bed_files(dir_list: list, infile_dir: Path, outfile: Path) -> None:

    with open(outfile, 'a', newline="\n") as fh:
        writer = csv.writer(fh, delimiter="\t")

        for directory in dir_list:
            directory_path = infile_dir / directory
            if os.path.isdir(directory_path) and 'chr' in directory:

                directory_files = os.listdir(directory_path)

                if directory in directory_files and not 'tuf.bed' in directory_files:

                    new_directory_path = directory_path / directory


                    print("{0} processing directory {1}".format(INFO, new_directory_path))

                    # read the file
                    factory = FileReaderFactory(reader_type=FileReaderType.TUF_BED)
                    lines = factory(filename=new_directory_path / 'tuf.bed')

                    for line in lines:
                        line_data = line.split("\t")
                        data = [item.strip("\n") for item in line_data]
                        writer.writerow(data)

                else:
                    raise ValueError("Invalid directory stucture")




def main(infile_dir: Path, input_filename: str,
         output_file_dir: Path, output_filename: str,
         file_reader: FileReaderType, filename: str, **options) -> None:


    print("{0} file_reader={1}".format(INFO, file_reader.name))

    # get the directories
    dir_list = os.listdir(infile_dir)

    def clean_list(dir_list: list) -> list:

        new_list = []
        for item in dir_list:
            if item.startswith('chr'):
                new_list.append(item)

        return new_list

    dir_list = clean_list(dir_list=dir_list)

    def key_func(chr_name: str) -> int:
        return int(chr_name.split('chr')[1])

    # sort the directories
    dir_list.sort(key=key_func)
    reader = FileReaderFactory(reader_type=file_reader)

    with open(output_file_dir / output_filename, 'a', newline="\n") as fh:
        writer = csv.writer(fh, delimiter="\t")

        for directory in dir_list:
            directory_path = infile_dir / directory
            if os.path.isdir(directory_path) and 'chr' in directory:

                directory_files = os.listdir(directory_path)

                if directory in directory_files and not filename in directory_files:

                    new_directory_path = directory_path / directory

                    print("{0} processing directory {1}".format(INFO, new_directory_path))

                    # reade the file
                    lines = reader(filename=new_directory_path / input_filename)

                    for line in lines:
                        line_data = line.split("\t")
                        data = [item.strip("\n") for item in line_data]
                        writer.writerow(data)

                else:
                    raise ValueError("Invalid directory stucture")



if __name__ == '__main__':

    print("{0} Start combine bed files app...".format(INFO))

    INPUT_FILE_DIR = Path("/home/alex/qi3/hmmtuf/computations/viterbi_paths/")
    OUTPUT_FILE_DIR = Path("/home/alex/qi3/hmmtuf/computations/viterbi_paths/")
    input_filenames = {"deletion.bed": FileReaderType.DELETION_BED,
                       "duplication.bed": FileReaderType.DUPLICATION_BED, "gap.bed": FileReaderType.GAP_BED,
                       "gquads.txt": FileReaderType.GQUADS, "normal.bed": FileReaderType.NORMAL_BED,
                       "nucl_out.bed": FileReaderType.NUCL_OUT, "quad.bed": FileReaderType.QUAD_BED,
                       "rep.bed": FileReaderType.REP_BED, "repeates_info_file.bed": FileReaderType.REPEATS_INFO_BED,
                       "tdt.bed": FileReaderType.TDT_BED, "tuf.bed": FileReaderType.TUF_BED,
                       "viterbi.bedgraph": FileReaderType.VITERBI_BED_GRAPH}

    for filename in input_filenames:

        items = filename.split('.')
        input_filename = filename
        output_file_name = items[0] + '_out'+ '.' + items[1]

        main(infile_dir=INPUT_FILE_DIR, input_filename=input_filename,
            output_file_dir=OUTPUT_FILE_DIR, output_filename=output_file_name,
            file_reader=input_filenames[filename],
             filename=filename)

    print("{0} Finished...".format(INFO))
