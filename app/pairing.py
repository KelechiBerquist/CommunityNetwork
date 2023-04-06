"""
Purpose: Manages SkipLevels pairings

"""

import os
from copy import deepcopy

import pandas as pd

from app.settings import COLUMN_MAPPING, JOB_FAMILY_LEVELS
from app.wrangler import Wranglers as Wr
from app.queries import POTENTIAL_CONNECTIONS


class Pairings:
    """Defines logic for pairings
    """
    db = None
    root_dir = None
    
    @classmethod
    def get_pairings_from_file(cls, iteration: str, filename: str, sheet_name: str):
        """Get pairings from file

        Parameters:
            iteration: current SkipLevels iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with interest information

        Returns:
        """
        # print("In Pairing: Filename: {0}, Sheet: {1}".format(filename, sheet_name))
        file_path = os.path.join(cls.root_dir, "data", "input", iteration, filename)
        
        data = Wr.read_file(file_path, sheet_name)
        data = Wr.fix_column_names(data, COLUMN_MAPPING)
        data["job_level"] = data["job_family"].apply(lambda _: JOB_FAMILY_LEVELS[_])
        iteration_number = Wr.get_iteration_number(iteration)
        
        # Filter out relevant parties
        data = data[pd.notnull(data["pair_email"])]
        
        # To prevent duplication from searching both halves of the pair, put results in a set.
        pair_levels = set([Wr.get_pairing_level(data, _)
                           for _ in data[["emp_email", "pair_email"]].to_numpy()])

        # Define pair list.
        pair_list = [{"iteration_name": iteration, "iteration_number": iteration_number,
                      "junior": _.junior, "senior": _.senior} for _ in pair_levels]

        return pair_list

    @classmethod
    def get_possible_pairings_from_database(cls, iteration: str, conn_obj):
        lookup = deepcopy(POTENTIAL_CONNECTIONS)
        lookup[1]["$match"]["iteration_name"] = \
            lookup[1]["$match"]["iteration_name"].format(current_iteration=iteration)
        connection_list = [
            {
                "emp": item["employee"][0],
                "invalid_match": list(set(
                        [_['emp_email'] for _ in item["counsellee"]] +
                        [_['emp_email'] for _ in item["pml"]] +
                        [_['senior'] for _ in item["junior_in_meeting"]] +
                        [_['junior'] for _ in item["senior_in_meeting"]])),
                "valid_match": [
                    _ for _ in item["potential_connection"] if (
                            _["emp_email"] not in [_['emp_email'] for _ in item["counsellee"]] and
                            _["emp_email"] not in [_['emp_email'] for _ in item["pml"]] and
                            _["emp_email"] not in [_['senior'] for _ in
                                                   item["junior_in_meeting"]] and
                            _["emp_email"] not in [_['junior'] for _ in item["senior_in_meeting"]]
                    )
                ]
        
            }
            for item in conn_obj.aggregate(lookup)
        ]

        valid_matches = [
            {
                **item["emp"],
                "valid_match": [
                    _ for _ in item["valid_match"] if
                    (item["emp"]["job_level"] < 2 and 3 <= _["job_level"] <= 4) or
                    (item["emp"]["job_level"] == 3 and _["job_level"] != item["emp"][
                        "job_level"]) or
                    (item["emp"]["job_level"] > 3 and _["job_level"] <= 3)
                ]
        
            }
            for item in connection_list
        ]
        return valid_matches
