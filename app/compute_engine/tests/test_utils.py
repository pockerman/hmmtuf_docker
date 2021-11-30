import unittest
from pathlib import Path
from compute_engine.src.utils import min_size_partition_range
from compute_engine.src.utils import load_data_file
from compute_engine.src.utils import type_converter
from compute_engine.src.utils import make_data_array
from compute_engine.src.utils import get_sequence_chunks
from compute_engine.src.utils import get_range_chunks
from compute_engine.src.utils import unzip_files
from compute_engine.src.exceptions import Error


class TestUtils(unittest.TestCase):

    def test_min_size_partition_range_1(self):
        start = 0
        end = 0
        minsize = 1
        self.assertRaises(Error, min_size_partition_range, start, end, minsize)

    def test_min_size_partition_range_2(self):
        start = 0
        end = 1
        minsize = 1
        chuncks = min_size_partition_range(start, end, minsize)
        self.assertEqual(len(chuncks), 1)
        self.assertEqual(chuncks[0][0], 0)
        self.assertEqual(chuncks[0][1], 1)

    def test_min_size_partition_range_3(self):
        start = 0
        end = 10
        minsize = 2
        chuncks = min_size_partition_range(start, end, minsize)
        self.assertEqual(len(chuncks), 5)

        self.assertEqual(chuncks[0][0], 0)
        self.assertEqual(chuncks[0][1], 2)

        self.assertEqual(chuncks[1][0], 2)
        self.assertEqual(chuncks[1][1], 4)

        self.assertEqual(chuncks[2][0], 4)
        self.assertEqual(chuncks[2][1], 6)

        self.assertEqual(chuncks[3][0], 6)
        self.assertEqual(chuncks[3][1], 8)

        self.assertEqual(chuncks[4][0], 8)
        self.assertEqual(chuncks[4][1], 10)

    def test_min_size_partition_range_4(self):
        start = 0
        end = 10
        minsize = 1
        chuncks = min_size_partition_range(start, end, minsize)
        self.assertEqual(len(chuncks), 10)

        self.assertEqual(chuncks[0][0], 0)
        self.assertEqual(chuncks[0][1], 1)

        self.assertEqual(chuncks[1][0], 1)
        self.assertEqual(chuncks[1][1], 2)

        self.assertEqual(chuncks[2][0], 2)
        self.assertEqual(chuncks[2][1], 3)

        self.assertEqual(chuncks[3][0], 3)
        self.assertEqual(chuncks[3][1], 4)

        self.assertEqual(chuncks[4][0], 4)
        self.assertEqual(chuncks[4][1], 5)

        self.assertEqual(chuncks[5][0], 5)
        self.assertEqual(chuncks[5][1], 6)

        self.assertEqual(chuncks[6][0], 6)
        self.assertEqual(chuncks[6][1], 7)

        self.assertEqual(chuncks[7][0], 7)
        self.assertEqual(chuncks[7][1], 8)

        self.assertEqual(chuncks[8][0], 8)
        self.assertEqual(chuncks[8][1], 9)

        self.assertEqual(chuncks[9][0], 9)
        self.assertEqual(chuncks[9][1], 10)

    def test_min_size_partition_range_4(self):
        start = 0
        end = 10
        minsize = 3
        chuncks = min_size_partition_range(start, end, minsize)
        self.assertEqual(len(chuncks), 3)

        self.assertEqual(chuncks[0][0], 0)
        self.assertEqual(chuncks[0][1], 3)

        self.assertEqual(chuncks[1][0], 3)
        self.assertEqual(chuncks[1][1], 6)

        self.assertEqual(chuncks[2][0], 6)
        self.assertEqual(chuncks[2][1], 10)

    def test_type_converter_fail(self):
        self.assertRaises(ValueError, type_converter, 20.0, "MY_DATA")

    def test_load_data_file(self):
        DATA_PATH = "../../data/train/wga_windows_mean_0_DUPLICATION_CHR_1_MEAN_CUTOFF.txt"
        data = load_data_file(filename=DATA_PATH, type_convert="FLOAT")
        self.assertEqual(len(data), 5025)

    def test_make_data_array_fail_1(self):
        wga_mu=[1.0, 2.0]
        no_wga_mu=[1.0]
        gc=None
        use_ratio=False
        use_gc=False
        self.assertRaises(ValueError, make_data_array,
                          wga_mu, no_wga_mu, gc, use_ratio, use_gc)

    def test_make_data_array_fail_2(self):
        wga_mu=[1.0, 2.0]
        no_wga_mu=[1.0, 2.0]
        gc=None
        use_ratio=False
        use_gc=True
        self.assertRaises(ValueError, make_data_array,
                          wga_mu, no_wga_mu, gc, use_ratio, use_gc)

    def test_make_data_array_fail_3(self):
        wga_mu=[1.0, 2.0]
        no_wga_mu=[1.0, 2.0]
        gc=[1.0]
        use_ratio=False
        use_gc=True
        self.assertRaises(ValueError, make_data_array,
                          wga_mu, no_wga_mu, gc, use_ratio, use_gc)

    def test_get_chunks_1(self):
        seq = "AAAA"
        chunk_size = 4
        chunks = get_sequence_chunks(cseq=seq, chunk_size=chunk_size)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 4)

    def test_get_chunks_2(self):
        seq = "AAAA"
        chunk_size = 2
        chunks = get_sequence_chunks(cseq=seq, chunk_size=chunk_size)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 2)

    def test_get_chunks_3(self):
        seq = "AAAA"
        chunk_size = 3
        chunks = get_sequence_chunks(cseq=seq, chunk_size=chunk_size)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 3)
        self.assertEqual(len(chunks[1]), 1)

    def test_get_range_chunks_1(self):

        start = 0
        end = 10
        c_size = 2

        chunks = get_range_chunks(start=start, end=end, chunk_size=c_size)
        self.assertEqual(len(chunks), 5)

        for item in chunks:
            self.assertEqual(len(item), 2)

    def test_get_range_chunks_2(self):

        start = 0
        end = 11
        c_size = 2

        chunks = get_range_chunks(start=start, end=end, chunk_size=c_size)
        self.assertEqual(len(chunks), 6)

        for i, item in enumerate(chunks):
            self.assertEqual(len(item), 2)

    def test_unzip_files(self):
        data_dir = Path("/home/alex/qi3/hmmtuf/computations/distances/sor/")
        unzip_files(data_dir=data_dir, output_dir=Path("/home/alex/qi3/hmmtuf/computations/unzipped_dists/sor/"))




if __name__ == '__main__':
    unittest.main()