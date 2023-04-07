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
        matched = Pr.assign_pairings(ASSIGNMENT_DATA, [])
        match_file = os.path.join(ROOT_DIR, "unit_test", "test_data", "matches.json")
        for filepath in [match_file]:
            try:
                os.makedirs(os.path.dirname(filepath))
            except FileExistsError:
                pass
        with open(match_file, "w") as writer:
            json.dump(matched, writer)
