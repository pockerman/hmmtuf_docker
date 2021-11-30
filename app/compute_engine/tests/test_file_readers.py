import unittest
from pathlib import Path
from compute_engine.src.file_readers import GQuadsFileReader, RepeatsInfoFileReader, CsvFileReader


class TestFileReaders(unittest.TestCase):

    def test_read_from_file_1(self):

        filename = Path("data/gquads.txt")
        data_loader = GQuadsFileReader()
        seqs = data_loader(filename=filename)

        self.assertEqual(len(seqs), 5)
        self.assertEqual(seqs[('chr2', 10301, 10400)], [59., -999.0, -999.0,	False])
        self.assertEqual(seqs[('chr2', 10401, 10500)], [72., -999.0, -999.0,	True])
        self.assertEqual(seqs[('chr2', 196311, 197311)], [45., 28., 66.,	False])

    def test_read_from_file_2(self):

        filename = Path("data/repeates_info_file.bed")
        data_loader = RepeatsInfoFileReader()
        seqs = data_loader(filename=filename)

        self.assertEqual(len(seqs), 2)
        self.assertEqual((seqs[0][0], seqs[0][1], seqs[0][2], seqs[0][3], seqs[0][4], seqs[0][5]),
                         ('chr7',	132085020,132086020,6,	'tatatctatatctatatctatatctatatctatatc',	'TATATCTATATCTATATCTATATCTATATCTATATC'))

        self.assertEqual((seqs[1][0], seqs[1][1], seqs[1][2], seqs[1][3], seqs[1][4], seqs[1][5]),
                         ('chr7',132559400,132561499,7,	'TCTCTTCCTGCTGCTTCCTCCTCTGCCTCTTCCTCCTCCTCCTTCTTCTCCTCCTCCTCTTCCTCCTTGTCCTCTTCCTCCTCCTTCTCCTCCTCCT',
                         'CCTCTTCCTCCTCCTCCTCTTCCTCCTCCTCCTCTTCCTCCTCCTCCTCTTCCTCCTCCTCCTCTTCCTCCCCCT'))

    def test_read_from_file_3(self):
        filename = Path("data/nucl_out.csv")
        data_loader = CsvFileReader()
        seqs = data_loader(filename=filename)

        self.assertEqual(len(seqs), 4)
        self.assertEqual((seqs[0][0], seqs[0][1], seqs[0][2], seqs[0][3], seqs[0][4], seqs[0][5],
                          seqs[0][6], seqs[0][7], seqs[0][8]),
                         ('chr7', '1022187', '1023187','NO_REPEATS','Normal', '57.0', '33.0', '74.0','False'))


if __name__ == '__main__':
    unittest.main()