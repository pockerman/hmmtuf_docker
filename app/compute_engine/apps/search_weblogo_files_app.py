import json
import os
from pathlib import Path
import csv

from compute_engine.src.file_readers import NuclOutFileReader
from compute_engine.src.tuf_core_helpers import get_statistics_from_weblogo

def main(input_path_dir: Path) -> None:

    directories = os.listdir(input_path_dir)

    repeats_statistics = {}
    for directory in directories:

        if 'chr' in directory and len(directory) <= 5:
            # this is a directory of interest
            directory += '/' + directory
            directory_path =  input_path_dir / directory

            # loop over the regions in the director

            regions = os.listdir(directory_path)

            for region in regions:
                if 'region' in region:

                    region_path = directory_path / region
                    print(region_path)

                    spade_output = region_path / 'spade_output'

                    regions_spade_dirs = os.listdir(spade_output)

                    # open the nucl_out file
                    nucl_out_file = region_path / 'nucl_out.bed'

                    nucl_data_reader = NuclOutFileReader(exclude_seqs=["NO_REPEATS"], strip=True)
                    nucl_data = nucl_data_reader(filename=nucl_out_file)
                    total_region_repeats = len(nucl_data)
                    print(f"Number of region repeats...{total_region_repeats}")
                    repeats_counter = 0
                    for item in nucl_data:

                        # we only have the coordinates that have repeats
                        chromo = item[0]
                        start_idx = int(item[1])
                        end_idx = int(item[2])
                        repeat = item[3].strip()
                        state = item[4]

                        if (chromo, start_idx, end_idx) in repeats_statistics:
                            raise ValueError(f"Key {(chromo, start_idx, end_idx, repeat)} already present in statistics ")

                        # open the directory in the spade output
                        spade_dir_nucl_name = chromo + '_' + \
                                          str(start_idx) + '-' + \
                                          str(end_idx) + '_' + state

                        names_to_proc = []
                        for name in regions_spade_dirs:


                            if spade_dir_nucl_name in name:
                                names_to_proc.append(name)

                        assert len(names_to_proc) == 1, f"Should have found one " \
                                                    f"dir but found {len(names_to_proc)} Indexes {start_idx}/{end_idx}"


                        weblogo_path = spade_output / names_to_proc[0]

                        # get the nucl files
                        nucl_files = [dirname for dirname in os.listdir(weblogo_path) if dirname.startswith('nucl_')]

                        if len(nucl_files) == 0:
                            raise ValueError("A repeat was found but no weblogo files")


                        for nucl_dir_name in nucl_files:

                            # open the weblogo.txt file and do computations
                            found, statistics = get_statistics_from_weblogo(weblogo_dir=weblogo_path / nucl_dir_name,
                                                                            repeat=repeat)

                            if found:
                                print("Constructed statistics...")
                                repeats_counter += 1
                                repeats_statistics[(chromo, start_idx, end_idx, repeat)] = statistics
                                break

                    if repeats_counter != total_region_repeats:
                        raise ValueError(f"The region repeats {repeats_counter} is not equal "
                                         f"to total region repeats {total_region_repeats}")


    return repeats_statistics


if __name__ == '__main__':

    INPUT_PATH_DIR = Path('/home/alex/qi3/hmmtuf/computations/viterbi_paths')
    OUTPUT_PATH_DIR = Path('/home/alex/qi3/hmmtuf/computations/viterbi_paths/tmp/out')
    repeats_statistics = main(input_path_dir=INPUT_PATH_DIR)

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