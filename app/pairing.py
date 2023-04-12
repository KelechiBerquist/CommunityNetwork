"""
Purpose: Manages CommunityNetwork pairings

"""
import copy
import json
import os
from copy import deepcopy

import pandas as pd

from app.queries import POTENTIAL_CONNECTIONS
from app.settings import APP_LOGGER, COLUMN_MAPPING, EXPLORATION_DEPTH, JOB_FAMILY_LEVELS, \
    LEVEL_MATCH_MAP, OUTPUT_FILES, ROOT_DIR
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
        file_path = os.path.join(ROOT_DIR, "data", "input", iteration, filename)

        data = Wr.read_file(file_path, sheet_name)
        data = Wr.fix_column_names(data, COLUMN_MAPPING)
        
        APP_LOGGER.debug("Perform transformation on data for iteration: %s" % iteration)
        data["job_level"] = data["job_family"].apply(lambda _: JOB_FAMILY_LEVELS[_])
        iteration_number = Wr.get_iteration_number(iteration)
        
        # Filter out relevant parties
        data = data[pd.notnull(data["pair_email"])]

        APP_LOGGER.debug("Mapping iteration participants to level for iteration: %s" % iteration)
        # To prevent duplication from searching both halves of the pair, put results in a set.
        pair_levels = set([Wr.get_pairing_level(data, _)
                           for _ in data[["emp_email", "pair_email"]].to_numpy()])

        APP_LOGGER.info("Defined meeting collection information for iteration: %s" % iteration)
        # Define pair list.
        return [{"iteration_name": iteration, "iteration_number": iteration_number,
                 "junior": _.junior, "senior": _.senior} for _ in pair_levels]

    @classmethod
    def get_pairings_from_database(cls, iteration: str, conn_obj) -> list:
        """Get pairings from database

        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
            conn_obj: connection object to database collection

        Returns: list of pairings
        """
        # TODO: Check for unmatched interested candidates and attempt to manually match them.
        APP_LOGGER.info("Get pairing data for iteration: %s" % iteration)
        data = cls.get_pairings_data(iteration, conn_obj)
        
        iteration_number = Wr.get_iteration_number(iteration)
        level_list = Wr.get_leveled_list(data)
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
        # TODO: Check for unmatched interested candidates and attempt to manually match them.
        APP_LOGGER.info("Get pairing information from database for iteration: %s" % iteration)
        lookup = deepcopy(POTENTIAL_CONNECTIONS)
        lookup[1]["$match"]["iteration_name"] = \
            lookup[1]["$match"]["iteration_name"].format(current_iteration=iteration)

        APP_LOGGER.debug("Set up data for pairing for iteration: %s" % iteration)
        
        return Wr.get_connections_data([_ for _ in conn_obj.aggregate(lookup)])

    @classmethod
    def assign_pairs(cls, juniors: set[str], seniors: set[str], connected: dict[str, set],
                     matches: list[dict], iteration: str, iteration_number: int):
        """Assign pairings and populate a list of matches

            Parameters:
                juniors: set of potential juniors in connection
                seniors: set of potential seniors in connection
                connected: dict of parties and their existing connections
                matches: list of assigned matches
                iteration: current networking iteration
                iteration_number: numerical representation of iteration
        """
        if (not len(juniors)) or (not len(seniors)):
            return matches
        
        jun = juniors.pop()
        sen = seniors.pop()

        if sen not in connected[jun]:
            matches.append({"junior": jun, "senior": sen,
                            "iteration_name": iteration,
                            "iteration_number": iteration_number})
        else:
            juniors.add(jun)
            seniors.add(sen)
        return cls.assign_pairs(juniors, seniors, connected, matches, iteration, iteration_number)

    @classmethod
    def assign_pairs_per_level(cls, levels: dict[str, set], connections: dict[str, set],
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
        for j_lev in levels:
            s_lev_list = LEVEL_MATCH_MAP[j_lev]
            for s_lev in s_lev_list:
                matched.extend(cls.assign_pairs(levels[j_lev], levels[s_lev], connections, [],
                                                iteration, iteration_number))
        cls.record_unassigned(levels, iteration)
        cls.record_assigned(matched, iteration)
        return matched

    @classmethod
    def record_unassigned(cls, unmatched: dict[str, set], iteration: str) -> None:
        """Assign pairings and populate a list of matches

            Parameters:
                unmatched: set of unmatched connectors
                iteration: current networking iteration
            
        """
        unmatched_list = {k: list(v) for k, v in unmatched.items()}
        unmatch_file = OUTPUT_FILES["unmatched"].format(iteration=iteration)
        create_dirs(unmatch_file)
        with open(unmatch_file, "w") as writer:
            json.dump(unmatched_list, writer)

    @classmethod
    def record_assigned(cls, match: list[dict[str, set]], iteration: str) -> None:
        """Assign pairings and populate a list of matches

            Parameters:
                match: set of matched connectors
                iteration: current networking iteration
            
        """
        match_file = OUTPUT_FILES["matched"].format(iteration=iteration)
        create_dirs(match_file)
        with open(match_file, "w") as writer:
            json.dump(match, writer)
