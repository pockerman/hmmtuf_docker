import os
from pathlib import Path

from compute_engine.src.constants import INFO

def main(tabix_path: Path,
         input_file: Path, outfile:Path) -> None:

    if tabix_path:
        # system cmd to execute
        str_cmd = str(tabix_path) + '/bgzip' + ' {0} '.format(input_file)
        str_cmd += ' && ' + str(tabix_path) + '/tabix' + ' -p vcf {0}.gz '.format(input_file)
    else:
        # use system wide if it exisst
        str_cmd = 'bgzip' + ' {0} '.format(input_file)
        str_cmd += ' && ' + 'tabix' + ' -p vcf {0} '.format(input_file)


    print("Excuting cmd {0}".format(str_cmd))
    os.system(str_cmd)

if __name__ == '__main__':

    tabix_path = Path('/home/alex/MySoftware/htslib/htslib-1.12/install/bin/')
    input_filepath = Path("/home/alex/qi3/hmmtuf/computations/viterbi_paths/")

    input_filenames = ["tuf.bed", "deletion.bed",
                       "duplication.bed", "gap.bed",
                       "normal.bed",
                       "nucl_out.bed", "quad.bed",
                       "rep.bed", "repeates_info_file.bed",
                       "tdt.bed", "viterbi.bedgraph"]

    for filename in input_filenames:
        items = filename.split('.')
        new_filename = items[0]  + '_out.{0}'.format(items[1])
        input_filename = input_filepath / new_filename

        print("{0} Working with file {1}".format(INFO, input_filename))
        main(tabix_path=tabix_path,
             input_file=input_filename, outfile=None)
        print("{0} Done....".format(INFO))

    print("{0} Finished...".format(INFO))



