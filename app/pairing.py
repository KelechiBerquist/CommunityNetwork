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

    @staticmethod
    def get_pairings_from_database(cls, iteration: str, conn_obj):
        data = cls.get_pairings_data_from_database(iteration, conn_obj)
    
        # TODO: Check for unmatched interested candidates and attempt to manually match them.
        # to_match_data = Wr.get_assignment_data(data)

        # to_match_data = [
        #     {
        #         "emp": i["emp"]["emp_email"],
        #         "probables": {j["emp"]["emp_email"] for j in i["valid_match"]}
        #     } for i in data].sort(key=lambda i: len(i["probables"]))
        
        to_match_data = [
            {
                "emp": i["emp"]["emp_email"],
                "probables": [j["emp"]["emp_email"] for j in i["valid_match"]]
            } for i in data].sort(key=lambda i: len(i["probables"]))
        
        
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
    def assign_pairings(cls, probables: list, matches: list):
        """Assign pairings and populate a list of matches
            
            Parameters:
                probables: list of employees and possible matches
                matches: list of assigned matches
        """
        if not len(probables):
            return matches
        record = probables.pop(0)
        party_a = record["emp"]
        prob_bs = record["probables"]
        
        if len(prob_bs):
            party_b = prob_bs[0]
            matches.append((party_a, party_b))
            probables = cls.purge_matched(probables, party_a)
            probables = cls.purge_matched(probables, party_b)
        return cls.assign_pairings(probables, matches)

    @staticmethod
    def purge_matched(data: list, person) -> list:
        a = [
            {
                "emp": i["emp"],
                "probables": [j for j in i["probables"] if j != person]
            } for i in data if i["emp"] != person]
        # a = a.sort(key=lambda _: len(_["probables"]))
        
        return a

    @staticmethod
    def purge_person(data: list, person):
        new_data = [_ for _ in data if _["emp"] != person]

        new_data = [
            {
                "emp": i["emp"],
                "probables": {j for j in i["probables"] if j != person}
            } for i in data if i["emp"] != person].sort(key=lambda i: len(i["probables"]))
        
        
        for _ in data:
            if _["emp"] == person:
                data.remove(_)
            else:
                try:
                    _["probables"].remove(person)
                except ValueError:
                    pass
                except Exception:
                    raise
        return data

    @staticmethod
    def purge_party_a(data: list, person_a: str):
        for _ in data:
            try:
                _["probables"].remove(purge_value)
            except ValueError:
                pass
            except Exception:
                raise
            try:
                _["probables"].remove(purge_value)
            except ValueError:
                pass
            except Exception:
                raise
        return data

    @classmethod
    def enrich_connection_pair(cls, data: list, matches: list, enriched: list):
        if not len(matches):
            return enriched

        record = matches.pop(0)
        party_a, party_b = record.items()
        
        to_enrich = {}
        for i in data:
            if i["emp"]["emp_email"] == party_a:
                to_enrich["party_a"] = i["emp"]
            if i["emp"]["emp_email"] == party_b:
                to_enrich["party_b"] = i["emp"]
            if "party_a" in to_enrich and "party_b" in to_enrich:
                enriched.append(to_enrich)
                break
        return cls.enrich_connection_pair(data, matches, enriched)
