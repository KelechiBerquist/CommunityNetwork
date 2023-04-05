"""
Purpose: Manages SkipLevels pairings

"""

import os

import pandas as pd

from app.settings import COLUMN_MAPPING, JOB_FAMILY_LEVELS
from app.wrangler import Wranglers as Wr


class Pairings:
    """Defines logic for pairings
    """
    db = None
    root_dir = None
    
    @classmethod
    def load_prohibitions(cls, args: dict):
        pass
    
    @classmethod
    def get_pairings_from_file(cls, iteration: str, filename: str, sheet_name: str):
        """Get pairings from file

        Parameters:
            iteration: current SkipLevels iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with interest information

        Returns:
        """
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
    def get_pairings_from_database(cls, args: dict):
        pass
