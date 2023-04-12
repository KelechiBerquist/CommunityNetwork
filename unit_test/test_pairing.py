"""
Purpose: Manages SkipLevels pairings

"""
import json
import os
import unittest
from unittest.mock import patch

from app.pairing import Pairings as Pr
from app.settings import ROOT_DIR
from app.utils import create_dirs


EMP_MAP = [
    {"emp": {"emp_email": "a", "job_level": 1}, "invalid_match": ["k"]},
    {"emp": {"emp_email": "b", "job_level": 1}, "invalid_match": ["l"]},
    {"emp": {"emp_email": "c", "job_level": 2}, "invalid_match": ["e"]},
    {"emp": {"emp_email": "d", "job_level": 2}, "invalid_match": ["f"]},
    {"emp": {"emp_email": "e", "job_level": 4}, "invalid_match": ["c"]},
    {"emp": {"emp_email": "f", "job_level": 4}, "invalid_match": ["d"]},
    {"emp": {"emp_email": "g", "job_level": 5}, "invalid_match": ["m"]},
    {"emp": {"emp_email": "h", "job_level": 5}, "invalid_match": ["n"]},
    {"emp": {"emp_email": "i", "job_level": 6}, "invalid_match": ["o"]},
    {"emp": {"emp_email": "j", "job_level": 6}, "invalid_match": ["p"]},
    {"emp": {"emp_email": "k", "job_level": 3}, "invalid_match": ["a"]},
    {"emp": {"emp_email": "l", "job_level": 3}, "invalid_match": ["b"]},
    {"emp": {"emp_email": "m", "job_level": 3}, "invalid_match": ["g"]},
    {"emp": {"emp_email": "n", "job_level": 3}, "invalid_match": ["h"]},
    {"emp": {"emp_email": "o", "job_level": 3}, "invalid_match": ["i"]},
    {"emp": {"emp_email": "p", "job_level": 3}, "invalid_match": ["j"]},
]

CONNECTION_MAP = {
    "a": {"k"}, "b": {"l"}, "c": {"e"}, "d": {"f"}, "e": {"c"},
    "f": {"d"}, "g": {"m"}, "h": {"n"}, "i": {"o"}, "j": {"p"},
    "k": {"a"}, "l": {"b"}, "m": {"g"}, "n": {"h"}, "o": {"i"},
    "p": {"j"},
}

LEVEL_MAP = {
    1: {"a", "b"},
    2: {"c", "d"},
    4: {"e", "f"},
    5: {"g", "h"},
    6: {"i", "j"},
    3: {"k", "l", "m", "n", "o", "p"},
}


class TestPairings(unittest.TestCase):
    """Defines logic for pairings
    """
    
    def test_get_pairings_from_database(self):
        """
        """
        with patch.object(Pr, 'get_pairings_data', return_value=EMP_MAP) as mock_method:
            matched = Pr.get_pairings_from_database("2023-03", "")
            match_file = os.path.join(ROOT_DIR, "unit_test", "test_result", "mocked_meetings.json")
            create_dirs(match_file)
            with open(match_file, "w") as writer:
                json.dump(matched, writer)

    def test_assign_pairings(self):
        """
        """
        level_1_junior = LEVEL_MAP[1]
        level_1_senior = LEVEL_MAP[3]
        
        matched = Pr.assign_leveled_pairings(level_1_junior, level_1_senior,
                                             CONNECTION_MAP, [], 0)
        match_file = os.path.join(ROOT_DIR, "unit_test", "test_result", "matches.json")
        create_dirs(match_file)
        with open(match_file, "w") as writer:
            json.dump(matched, writer)
