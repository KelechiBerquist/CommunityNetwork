"""
Purpose: Manages interest in current SkipLevels initiative

"""

import os

import pandas as pd

from app.db_client import DatabaseClient as Dc
from app.settings import COLUMN_MAPPING, INTEREST_COLLECTION, INTEREST_COLUMN_NAME, \
    JOB_FAMILY_LEVELS
from app.wrangler import Wranglers as Wr

pd.set_option('display.max_rows', 999)
pd.set_option('display.max_columns', 999)
pd.set_option('display.max_colwidth', 500)
pd.set_option('display.expand_frame_repr', True)


class Interest:
    """Manages interest in current SkipLevels initiative
    """
    db = None
    root_dir = None
    
    @classmethod
    def upsert_interest(cls, iteration: str, filename: str, sheet_name: str) -> None:
        """Load data for CSE roster

        Parameters:
            iteration: current SkipLevels iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with interest information
        """
        # Prepare items for loading
        loaded_items = cls.prepare_interest(iteration, filename, sheet_name)
        
        # Get DB connection
        conn_obj = cls.db.get_collection_conn(INTEREST_COLLECTION)
        
        # Insert data into DB
        Dc.upsert_items(conn_obj, loaded_items)
    
    @classmethod
    def prepare_interest(cls, iteration: str, filename: str, sheet_name: str) -> list:
        """Prepare data to be loaded into the roster
        
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
        data["iteration_name"] = iteration
        data["iteration_number"] = Wr.get_iteration_number(iteration)
        
        # Filter out interested parties
        data = data[(data["job_level"] >= 3) | pd.notnull(data[INTEREST_COLUMN_NAME])]
        
        key_cols = ["iteration_name", "emp_email"]
        update_cols = ["iteration_number"]
        
        keys_list = data[key_cols].to_dict(orient="record")
        updates_list = data[update_cols].to_dict(orient="record")

        return [
            {
                "key": keys_list[_],
                "updates": updates_list[_]
            }
            for _ in range(data.shape[0])
        ]
