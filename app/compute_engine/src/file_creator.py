import os
from pathlib import Path

from compute_engine.src.utils import INFO

class FileCreator(object):
    """
    Helper class to manipulate files
    """
    def __init__(self):
        pass

    def segragate_nucl_out_file(self, filename: str, lines_per_file: int,
                                out_file_name: str, suffix: str,
                                output_dir: str, delimiter: str='\t'):

        with open(filename, 'r', newline='\n') as fh:

            line_counter = 0
            small_file = None

            for lineno, line in enumerate(fh):
                if lineno % lines_per_file == 0:
                    if small_file:
                        smallfile.close()
                    small_filename =   '{0}_{1}'.format(out_file_name, lineno + lines_per_file)
                    small_filename = small_filename + suffix
                    smallfile = open(output_dir + small_filename, "w")
                #line = line.split(delimiter)
                smallfile.write(line)

            if smallfile:
                smallfile.close()

    def append_nucl_out_files(self, dir_folder, ouptput_file):
        """
        Append the nucleod files in the results_dir
        into the ouptput_file
        """

        with open(ouptput_file, 'w', newline='\n') as fh:
            directories = os.listdir(path=dir_folder)

            for directory in directories:
                path = Path(dir_folder +  directory)
                local_dirs = os.listdir(path=path)

                for ldir in local_dirs:

                    local_path = path / ldir

                    if os.path.isdir(local_path):
                        print("{0} working with file {1}".format(INFO, local_path / 'nucl_out.bed'))
                        with open(local_path / 'nucl_out.bed', 'r' ) as nucl_fh:

                            for nuclu_line in nucl_fh:
                                fh.write(nuclu_line)



