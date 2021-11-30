import unittest
import sys
import os
from compute_engine.src.tufdel import gcpercent
from compute_engine.src.tuf_core_helpers import concatenate_bed_files

class TestUtils(unittest.TestCase):

    def test_gc_percent_1(self):

        array = "tactgaggtg"
        out = gcpercent(cseq=array, chunk_size=100)
        self.assertEqual(out, "50_NA_NA")

    def test_gc_percent_2(self):

        array = "tactgaggtg"
        out = gcpercent(cseq=array, chunk_size=2)
        self.assertEqual(out, "50_0_100")

    def test_gc_percent_3(self):

        array = "tactgaggtg"*11
        out = gcpercent(cseq=array, chunk_size=100)
        self.assertEqual(out, "50_50_50")

    def test_concatenate_bed_files(self):

        infiles = ["data/nucl_out_test_file_1.bed", "data/nucl_out_test_file_1.bed"]
        outfile = "data/test_file_diffs.bed"
        concatenate_bed_files(bedfiles=infiles, outfile=outfile)

        with open(outfile, 'r') as of:

            counter_lines = 0
            lines = []
            with open(infiles[0], 'r') as f1:

                for line in f1:
                    counter_lines += 1
                    lines.append(line)

            with open(infiles[1], 'r') as f2:

                for line in f2:
                    counter_lines += 1
                    lines.append(line)

            counter = 0;
            for line in of:
                self.assertEqual(line,lines[counter])
                counter += 1

            self.assertEqual(counter_lines, counter)

            # remove the file
            os.remove(outfile)


if __name__ == '__main__':
    unittest.main()


