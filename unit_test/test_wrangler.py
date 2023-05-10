"""
Purpose: Data wrangler

"""
import unittest
from collections import namedtuple

import pandas as pd

from app.wrangler import Wranglers as Wr
from unit_test.test_pair_data import DB_DATA, EXPECTED_EXISTING_CONNECTIONS, EXPECTED_LEVELLED, \
    EXPECTED_POSSIBLE


class TestWranglers(unittest.TestCase):

    def read_file(self):
        pass

    def write_file(self):
        pass

    def fix_date_columns(self):
        pass

    def fix_column_names(self):
        pass

    def test_get_iteration_number(self):
        """Test iteration retriever case
        """
        iteration_name = "2023-03"
        self.assertEqual(Wr.get_iteration_number(iteration_name), 1,
                         msg="Unexpected result from get_iteration_number")

        iteration_name = "2023-04"
        self.assertEqual(Wr.get_iteration_number(iteration_name), 2,
                         msg="Unexpected result from get_iteration_number")

        iteration_name = "2023-06"
        self.assertEqual(Wr.get_iteration_number(iteration_name), 2,
                         msg="Unexpected result from get_iteration_number")

        iteration_name = "2023-08"
        self.assertEqual(Wr.get_iteration_number(iteration_name), 3,
                         msg="Unexpected result from get_iteration_number")

        iteration_name = "2024-01"
        self.assertEqual(Wr.get_iteration_number(iteration_name), 5,
                         msg="Unexpected result from get_iteration_number")

        iteration_name = "2024-03"
        self.assertEqual(Wr.get_iteration_number(iteration_name), 5,
                         msg="Unexpected result from get_iteration_number")

    def test_get_pairing_level(self):
        """Test finding pairing level
        """
        test_data = [["1a@email.com", 1], ["1b@email.com", 1], ["1c@email.com", 1],
                     ["2a@email.com", 2], ["2b@email.com", 2], ["2c@email.com", 2],
                     ["3a@email.com", 3], ["3b@email.com", 3], ["3c@email.com", 3],
                     ["4a@email.com", 4], ["4b@email.com", 4], ["4c@email.com", 4],
                     ["5a@email.com", 5], ["5b@email.com", 5], ["5c@email.com", 5],
                     ["6a@email.com", 6], ["6b@email.com", 6], ["6c@email.com", 6]]
        test_df = pd.DataFrame(test_data, columns=["emp_email", "job_level"])
        PairLevels = namedtuple("Pairs", ["junior", "senior"])
        
        # Test case 1
        test_case = ["1a@email.com", "2a@email.com"]
        test_case_expectation = PairLevels("1a@email.com", "2a@email.com")
        self.assertTupleEqual(Wr.get_pairing_level(test_df, test_case), test_case_expectation,
                              msg="Unexpected result from get_pairing_level")

        # Test case 2
        test_case = ["2a@email.com", "4a@email.com"]
        test_case_expectation = PairLevels("2a@email.com", "4a@email.com")
        self.assertTupleEqual(Wr.get_pairing_level(test_df, test_case), test_case_expectation,
                              msg="Unexpected result from get_pairing_level")

        # Test case 3
        test_case = ["4c@email.com", "1a@email.com"]
        test_case_expectation = PairLevels("1a@email.com", "4c@email.com")
        self.assertTupleEqual(Wr.get_pairing_level(test_df, test_case), test_case_expectation,
                              msg="Unexpected result from get_pairing_level")

        # Test case 4
        test_case = ["6b@email.com", "3a@email.com"]
        test_case_expectation = PairLevels("3a@email.com", "6b@email.com")
        self.assertTupleEqual(Wr.get_pairing_level(test_df, test_case), test_case_expectation,
                              msg="Unexpected result from get_pairing_level")

        # Test case 5
        test_case = ["2a@email.com", "2b@email.com"]
        with self.assertRaises(ValueError):
            Wr.get_pairing_level(test_df, test_case)

        # Test case 6
        test_case = ["4a@email.com", "4c@email.com"]
        with self.assertRaises(ValueError):
            Wr.get_pairing_level(test_df, test_case)

    def test_get_connections_data(self):
        """
        """
        for i in range(len(DB_DATA)):
            result = Wr.get_preconnections_data(DB_DATA[i:i + 1])[0]
            expected = EXPECTED_POSSIBLE[i]
            msg = "\n\nExp: {0}\n\nGot: {1}".format(expected, result)
            self.assertDictEqual(result, expected, msg=msg)

    def test_get_existing_connections(self):
        """
        """
        result = Wr.get_existing_connections(EXPECTED_POSSIBLE)
        expected = EXPECTED_EXISTING_CONNECTIONS
        msg = "\n\nExp: {0}\n\nGot: {1}".format(expected, result)
        self.assertDictEqual(result, expected, msg=msg)

    def test_get_leveled_list(self):
        """
        """
        result = Wr.get_leveled_preconnectors(EXPECTED_POSSIBLE)
        expected = EXPECTED_LEVELLED
        msg = "\n\nExp: {0}\n\nGot: {1}".format(expected, result)
        self.assertDictEqual(result, expected, msg=msg)
