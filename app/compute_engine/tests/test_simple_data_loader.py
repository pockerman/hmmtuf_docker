import unittest
from pathlib import Path
from compute_engine.src.classification.data_loader import SimpleDataLoader


class TestSimpleDataLoader(unittest.TestCase):

    def test_read_from_csv_1(self):

        data_loader = SimpleDataLoader()

        filename = Path("data/test_data_loader.csv")
        data_loader.read_from_csv(filename=filename, label_idx=-1)
        self.assertEqual(data_loader.get_data_set.shape[0], 4)
        self.assertEqual(data_loader.get_data_set.shape[1], 2)

    def test_read_from_csv_2(self):

        data_loader = SimpleDataLoader()

        filename = Path("data/test_data_loader.csv")
        data_loader.read_from_csv(filename=filename, label_idx=0)
        self.assertEqual(data_loader.get_data_set.shape[0], 4)
        self.assertEqual(data_loader.get_data_set.shape[1], 2)

if __name__ == '__main__':
    unittest.main()