"""
Purpose: Manages SkipLevels pairings

"""

import os
from copy import deepcopy

import pandas as pd

from app.settings import COLUMN_MAPPING, JOB_FAMILY_LEVELS, LEVEL_MATCH_MAP, ROOT_DIR
from app.wrangler import Wranglers as Wr
from app.queries import POTENTIAL_CONNECTIONS

DEBUG = False

debug_match_file = os.path.join(ROOT_DIR, "unit_test", "test_data", "debug_matches.txt")
for filepath in [debug_match_file]:
    try:
        os.makedirs(os.path.dirname(filepath))
    except FileExistsError:
        pass
debug_match_file_writer = open(debug_match_file, "w")

def print_out(*args, **kwargs):
    if DEBUG:
        print(args, kwargs)

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
        # print_out("In Pairing: Filename: {0}, Sheet: {1}".format(filename, sheet_name))
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

    @staticmethod
    def get_pairings_from_database(cls, iteration: str, conn_obj):
        data = cls.get_pairings_data_from_database(iteration, conn_obj)
    
        # TODO: Check for unmatched interested candidates and attempt to manually match them.
        # to_match_data = Wr.get_assignment_data(data)
        
        to_match_data = [
            {
                "emp": i["emp"]["emp_email"],
                "probables": [j["emp"]["emp_email"] for j in i["valid_match"]]
            } for i in data]
        
        matches = cls.assign_pairings(to_match_data, [])
        # enriched_matches = cls.enrich_connection_pair(data, matches, [])

    @classmethod
    def get_pairings_data_from_database(cls, iteration: str, conn_obj):
        lookup = deepcopy(POTENTIAL_CONNECTIONS)
        lookup[1]["$match"]["iteration_name"] = \
            lookup[1]["$match"]["iteration_name"].format(current_iteration=iteration)
        
        data = [_ for _ in conn_obj.aggregate(lookup)]

        possibles = Wr.get_possible_connections(data)

        probables = Wr.get_probable_connections(possibles)

        return probables

    @classmethod
    def assign_pairings(cls, employees, matches):
        """Assign pairings and populate a list of matches
            
            Parameters:
                employees: list of employees and possible matches
                matches: list of assigned matches
        """
        if not len(employees):
            return [[("matches", len(matches))] + matches]
        
        all_matches = []
        record = employees.pop(0)
        party_1 = record["emp"]["emp_email"]
        level_1 = record["emp"]["job_level"]
        possible_level_2 = LEVEL_MATCH_MAP[level_1]
        possible_matches = [emp["emp"]["emp_email"] for emp in employees if (
                emp["emp"]["job_level"] in possible_level_2 and
                emp["emp"]["emp_email"] not in record["invalid_match"])]

        for party_2 in possible_matches:
            l1_employees = cls.purge_matched(employees, party_2)
            new_matches = matches + [(party_1, party_2)]
            all_matches += cls.assign_pairings(l1_employees, new_matches)
        
        return all_matches + cls.assign_pairings(employees, matches)

    @staticmethod
    def purge_matched(data: list, person) -> list:
        return [i for i in data if i["emp"] != person]

    @classmethod
    def enrich_connection_pair(cls, data: list, matches: list, enriched: list):
        if not len(matches):
            return enriched

        record = matches.pop(0)
        party_1, party_2 = record.items()
        
        to_enrich = {}
        for i in data:
            if i["emp"]["emp_email"] == party_1:
                to_enrich["party_1"] = i["emp"]
            if i["emp"]["emp_email"] == party_2:
                to_enrich["party_2"] = i["emp"]
            if "party_1" in to_enrich and "party_2" in to_enrich:
                enriched.append(to_enrich)
                break
        return cls.enrich_connection_pair(data, matches, enriched)
