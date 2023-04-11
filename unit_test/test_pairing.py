"""
Purpose: Manages SkipLevels pairings

"""
import json
import os
import unittest
from copy import deepcopy

import pandas as pd

from app.settings import COLUMN_MAPPING, JOB_FAMILY_LEVELS, ROOT_DIR
from app.pairing import Pairings as Pr
from app.queries import POTENTIAL_CONNECTIONS
from unit_test.test_pair_data import EXPECTED_POSSIBLE, EXPECTED_PROBABLE, DB_DATA, ASSIGNMENT_DATA


class TestPairings(unittest.TestCase):
    """Defines logic for pairings
    """

    def test_assign_pairings(self):
        """
        """
        emp_map = [
            {"emp": {"emp_email": "a", "job_level": 1}, "invalid_match": ["k"]},
            {"emp": {"emp_email": "b", "job_level": 1}, "invalid_match": ["l"]},
            {"emp": {"emp_email": "c", "job_level": 2}, "invalid_match": ["e"]},
            {"emp": {"emp_email": "d", "job_level": 2}, "invalid_match": ["f"]},
            {"emp": {"emp_email": "e", "job_level": 4}, "invalid_match": ["c"]},
            # {"emp": {"emp_email": "f", "job_level": 4}, "invalid_match": ["d"]},
            # {"emp": {"emp_email": "g", "job_level": 5}, "invalid_match": ["m"]},
            # {"emp": {"emp_email": "h", "job_level": 5}, "invalid_match": ["n"]},
            # {"emp": {"emp_email": "i", "job_level": 6}, "invalid_match": ["o"]},
            # {"emp": {"emp_email": "j", "job_level": 6}, "invalid_match": ["p"]},
            {"emp": {"emp_email": "k", "job_level": 3}, "invalid_match": ["a"]},
            {"emp": {"emp_email": "l", "job_level": 3}, "invalid_match": ["b"]},
            {"emp": {"emp_email": "m", "job_level": 3}, "invalid_match": ["g"]},
            # {"emp": {"emp_email": "n", "job_level": 3}, "invalid_match": ["h"]},
            # {"emp": {"emp_email": "o", "job_level": 3}, "invalid_match": ["i"]},
            # {"emp": {"emp_email": "p", "job_level": 3}, "invalid_match": ["j"]},
        ]

        matched = Pr.assign_pairings(emp_map, [])
        match_file = os.path.join(ROOT_DIR, "unit_test", "test_data", "matches.json")
        for filepath in [match_file]:
            try:
                os.makedirs(os.path.dirname(filepath))
            except FileExistsError:
                pass
        with open(match_file, "w") as writer:
            json.dump(matched, writer)
