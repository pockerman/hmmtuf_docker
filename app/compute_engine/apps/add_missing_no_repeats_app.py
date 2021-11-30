import json
import os
from pathlib import Path
import csv

from compute_engine.src.file_readers import NuclOutFileReader
from compute_engine.src.tuf_core_helpers import is_contributing_weblogo

def main(input_path_dir: Path, outfile: str = 'nucl_out_missing.bed') -> None:

    # get th directories in the path
    directories = os.listdir(input_path_dir)

    repeats_statistics = {}
    for directory in directories:

        # only work if pattern is 'chr**'
        if 'chr' in directory and len(directory) <= 5:

            # this is a directory of interest
            directory += '/' + directory
            directory_path =  input_path_dir / directory

            # loop over the regions in the director
            regions = os.listdir(directory_path)

            with open(directory_path / 'nucl_out_missing.bed', 'a', newline="\n") as fh:
                writer = csv.writer(fh)

                for region in regions:
                    if 'region' in region:

                        region_path = directory_path / region
                        print(region_path)

                        # spade output path
                        spade_output = region_path / 'spade_output'

                        # get all the directories in spade
                        regions_spade_dirs = os.listdir(spade_output)

                        # loop over the directories and if they
                        # have nucl_ directory check the weblogo.txt file

                        for spade_dir in regions_spade_dirs:

                            spade_dir_path = spade_output / spade_dir

                            nucl_dirs = [dirname for dirname in os.listdir(spade_dir_path) if dirname.startswith('nucl_')]

                            if len(nucl_dirs) == 0:
                                continue

                            if len(nucl_dirs) == 1:

                                nucl_dir = nucl_dirs[0]
                                nucl_dir_path = spade_dir_path / nucl_dir

                                is_contibuting = is_contributing_weblogo(weblogo_dir=nucl_dir_path)

                                if not is_contibuting:
                                    print(spade_dir_path)
                                    split_spade_dir_path = str(spade_dir_path).split('/')[-1].split('_')

                                    # this is missing repeats
                                    row = [split_spade_dir_path[0], split_spade_dir_path[1].split('-')[0],
                                           split_spade_dir_path[1].split('-')[1], 'NO_REPEATS', split_spade_dir_path[2],
                                           split_spade_dir_path[3], split_spade_dir_path[4], split_spade_dir_path[5]]
                                    writer.writerow(row)
                            else:

                                # we want to record only once the region
                                # so loop
                                nucl_counter = 0

                                found = False
                                while nucl_counter < len(nucl_dirs):
                                    nucl_dir = nucl_dirs[nucl_counter]

                                    is_contibuting = is_contributing_weblogo(weblogo_dir=nucl_dir_path)

                                    if is_contibuting:
                                        found = True
                                        break

                                    nucl_counter += 1

                                if not found:
                                    print(spade_dir_path)
                                    split_spade_dir_path = str(spade_dir_path).split('/')[-1].split('_')

                                    # this is missing repeats
                                    row = [split_spade_dir_path[0], split_spade_dir_path[1].split('-')[0],
                                           split_spade_dir_path[1].split('-')[1], 'NO_REPEATS', split_spade_dir_path[2],
                                           split_spade_dir_path[3], split_spade_dir_path[4], split_spade_dir_path[5]]
                                    writer.writerow(row)


if __name__ == '__main__':

    INPUT_PATH_DIR = Path('/home/alex/qi3/hmmtuf/computations/viterbi_paths')
    OUTPUT_PATH_DIR = Path('/home/alex/qi3/hmmtuf/computations/viterbi_paths/tmp/out')
    main(input_path_dir=INPUT_PATH_DIR)

    """
    keys = ['chr' + str(idx) for idx in range(1, 23)]
    unique_dirs = set()
    for item in repeats_statistics:


        if item[0] not in keys:
            raise ValueError(f"{item[0]} not found")
        else:
            unique_dirs.add(item[0])


    assert len(unique_dirs) == 22, "Invalid number of unique dirs"

    with open(OUTPUT_PATH_DIR / 'repeats_stats.csv', 'w', newline="\n") as fh:
        writer = csv.writer(fh)

        columns = ["chromosome", "start_idx", "end_idx", "repeat", 'A', 'C', 'G', 'T']
        writer.writerow(columns)

        for item in repeats_statistics:
            row = [*item, repeats_statistics[item]]
            writer.writerow(row)
    """