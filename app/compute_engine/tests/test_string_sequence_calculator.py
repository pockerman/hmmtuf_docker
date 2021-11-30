import unittest
from compute_engine.src.string_sequence_calculator import TextDistanceCalculator
from compute_engine.src.exceptions import Error


class TestUtils(unittest.TestCase):

    def test_calculate(self):

        method = 'all'
        calculator = TextDistanceCalculator(dist_type=method)
        dists = calculator.calculate(txt1="AAAA", txt2='BBBB')
        print(len(dists))
        print(len(TextDistanceCalculator.NAMES))
        self.assertEqual(len(dists), len(TextDistanceCalculator.NAMES) - 2)



if __name__ == '__main__':
    unittest.main()