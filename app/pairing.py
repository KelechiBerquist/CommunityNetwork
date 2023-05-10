"""
Purpose: Manages CommunityNetwork pairings

"""
import json
import os
from copy import deepcopy

import pandas as pd

from app.queries import CONNECTIONS
from app.settings import APP_LOGGER, COLUMN_MAPPING, JOB_FAMILY_LEVELS, \
    LEVEL_MATCH_MAP, MATCH_ORDER, OUTPUT_FILES, ROOT_DIR
from app.utils import create_dirs
from app.wrangler import Wranglers as Wr


class Pairings:
    """Defines logic for pairings
    """
    db = None
    
    @classmethod
    def get_pairings_from_file(cls, iteration: str, filename: str, sheet_name: str) -> list:
        """Get pairings from file

        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with interest information

        Returns:
        """
        APP_LOGGER.info("Get pairing information from file for iteration: %s" % iteration)
        APP_LOGGER.debug("Passed arguments are filename: %s \t sheet_name: %s \t iteration: %s" %
                         (filename, sheet_name, iteration))

        APP_LOGGER.debug("Begin reading file from path '%s' for iteration: %s" %
                         (filename, iteration))
        data = Wr.read_file(filename, sheet_name)
        data = Wr.fix_column_names(data, COLUMN_MAPPING)
        
        APP_LOGGER.debug("Perform transformation on data for iteration: %s" % iteration)
        data["job_level"] = data["job_family"].apply(lambda _: JOB_FAMILY_LEVELS[_])
        iteration_number = Wr.get_iteration_number(iteration)
        
        # Filter out relevant parties
        data = data[pd.notnull(data["pair_email"])]
        data["pair_number"] = list(range(1, data.shape[0] + 1))

        APP_LOGGER.debug("Mapping iteration participants to level for iteration: %s" % iteration)
        # To prevent duplication from searching both halves of the pair, put results in a set.
        pair_levels = set([Wr.get_pairing_level(data, _)
                           for _ in data[["emp_email", "pair_email"]].to_numpy()])

        APP_LOGGER.info("Defined meeting collection information for iteration: %s" % iteration)
        # Define pair list.
        return [
            {
                "iteration_name": iteration, "iteration_number": iteration_number,
                "junior": v.junior, "senior": v.senior, "pair_number": 1+i
            } for i, v in enumerate(pair_levels)]

    @classmethod
    def get_pairings_from_database(cls, iteration: str, conn_obj) -> list:
        """Get pairings from database

        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
            conn_obj: connection object to database collection

        Returns: list of pairings
        """
        APP_LOGGER.info("Get pairing data for iteration: %s" % iteration)
        data = cls.get_pairings_data(iteration, conn_obj)
        
        iteration_number = Wr.get_iteration_number(iteration)
        level_list = Wr.get_leveled_preconnectors(data)
        connect_list = Wr.get_existing_connections(data)

        APP_LOGGER.debug("Generate a list of possible matches for iteration: %s" % iteration)
        matches = cls.assign_pairs_per_level(level_list, connect_list, iteration, iteration_number)

        APP_LOGGER.debug("Get data for defining meeting pairs for iteration: %s" % iteration)
        return matches

    @classmethod
    def get_pairings_data(cls, iteration: str, conn_obj) -> list:
        """Get pairings from database

        Parameters:
            iteration: current iteration. Expected format YYYY-MM
            conn_obj: connection object to database collection

        Returns: list of data used for pairings
        """
        APP_LOGGER.info("Get pairing information from database for iteration: %s" % iteration)
        lookup = deepcopy(CONNECTIONS)
        lookup[0]["$match"]["iteration_name"] = \
            lookup[0]["$match"]["iteration_name"].format(current_iteration=iteration)

        APP_LOGGER.debug("Set up data for pairing for iteration: %s" % iteration)
        
        return Wr.get_preconnections_data([_ for _ in conn_obj.aggregate(lookup)])

    @classmethod
    def assign_pairs(cls, l0s: list[dict], l1s: list[dict], connected: dict[str, set],
                     matches: list[tuple], iteration: str,
                     iteration_number: int) -> list[tuple]:
        """Assign pairings and populate a list of matches

            Parameters:
                l0s: set of potential party 1 in connection
                l1s: set of potential party 2 in connection
                connected: dict of parties and their existing connections
                matches: list of assigned matches
                iteration: current networking iteration
                iteration_number: numerical representation of iteration
        """
        
        if (not len(l0s)) or (not len(l1s)):
            return matches
        
        for l1 in l1s:
            if l1["emp_email"] not in connected[l0s[0]["emp_email"]]:
                matches.append((l0s[0], l1))
                l0s.remove(l0s[0])
                l1s.remove(l1)
                break
        
        return cls.assign_pairs(l0s, l1s, connected, matches, iteration, iteration_number)

    @classmethod
    def assign_pairs_per_level(cls, levels: dict[str, list], connections: dict[str, set],
                               iteration: str, iteration_number: int) -> list:
        """Assign pairings and populate a list of matches

            Parameters:
                levels: set of potential connectors
                connections: dict of parties and their existing connections
                iteration: current networking iteration
                iteration_number: numerical representation of iteration
            
            Returns: list of connections
        """
        matched = []
        # Loop through each level in the levelled dict. For this doc, this is level 0
        for lev_0 in MATCH_ORDER:
            # Find the list of levels that are appropriate to match with level 0
            for lev_1 in LEVEL_MATCH_MAP[lev_0]:
                # Attempt to match all individuals in level 0 with someone in level 1.
                # If a match is successful, pop individual from level 0 and level 1 list.
                # Append successful level 0 and level 1 matches to matched list
                matched.extend(cls.assign_pairs(levels[lev_0], levels[lev_1], connections, [],
                                                iteration, iteration_number))
        
        # Enrich match pairs
        enriched_pairs = [
            {
                **Wr.get_pair_level_enrichment(*v), "iteration_name": iteration,
                "iteration_number": iteration_number, "pair_number": 1+i
            } for i, v in enumerate(matched)]
        # Write records of matches and unmatches
        cls.record_unassigned(levels, iteration)
        cls.record_assigned(enriched_pairs, iteration)
        return [
            {
                **v, "junior": v["junior"]["emp_email"], "senior": v["senior"]["emp_email"],
                "pair_number": 1+i
            } for i, v in enumerate(enriched_pairs)]

    @classmethod
    def record_unassigned(cls, unmatched: dict[str, list], iteration: str) -> None:
        """Assign pairings and populate a list of matches

            Parameters:
                unmatched: set of unmatched connectors
                iteration: current networking iteration
            
        """
        unmatched_list = {k: list(v) for k, v in unmatched.items()}
        unmatch_file = OUTPUT_FILES["algo_unmatched"].format(iteration=iteration)
        create_dirs(unmatch_file)
        with open(unmatch_file, "w") as writer:
            json.dump(unmatched_list, writer)

    @classmethod
    def record_assigned(cls, match: list[dict[str, str]], iteration: str) -> None:
        """Assign pairings and populate a list of matches

            Parameters:
                match: set of matched connectors
                iteration: current networking iteration
            
        """
        match_file = OUTPUT_FILES["algo_matched"].format(iteration=iteration)
        create_dirs(match_file)
        with open(match_file, "w") as writer:
            json.dump(match, writer)
