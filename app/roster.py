"""
Purpose: Creates and updates CSE roster

"""

import os

from app.db_client import DatabaseClient as Dc
from app.settings import COLUMN_MAPPING, JOB_FAMILY_LEVELS, ROSTER_COLLECTION, ROSTER_DATE_COLUMNS
from app.wrangler import Wranglers as Wr


class Roster:
    """Creates and updates CSE roster
    """
    db = None
    root_dir = None
    
    @classmethod
    def upsert_roster(cls, iteration: str, roster_filename: str, sheet_name: str) -> None:
        """Load data for CSE roster

        Parameters:
            iteration: current SkipLevels iteration. Expected format YYYY-MM
            roster_filename: path to file containing roster
            sheet_name: name of sheet with roster information
        """
        # Prepare items for loading
        loaded_items = cls.prepare_roster(iteration, roster_filename, sheet_name)
        
        # Get DB connection to collection
        conn_obj = cls.db.get_collection_conn(ROSTER_COLLECTION)
        
        # Insert data into DB
        Dc.upsert_items(conn_obj, loaded_items)
    
    @classmethod
    def prepare_roster(cls, iteration: str, filename: str, sheet_name: str) -> list:
        """Prepare data to be loaded into the roster
        
        Parameters:
            iteration: current SkipLevels iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with roster information
            
        Returns:
        """
        file_path = os.path.join(cls.root_dir, "data", "input", iteration, filename)
        
        data = Wr.read_file(file_path, sheet_name)
        
        data = Wr.fix_date_columns(data, ROSTER_DATE_COLUMNS)
        data = Wr.fix_column_names(data, COLUMN_MAPPING)
        
        data["job_level"] = data["job_family"].apply(lambda _: JOB_FAMILY_LEVELS[_])
        
        key_cols = ["emp_email"]
        update_cols = [_ for _ in data.columns if _.lower() != "emp_email"]

        keys_list = data[key_cols].to_dict(orient="record")
        updates_list = data[update_cols].to_dict(orient="record")

        return [
            {
                "key": keys_list[_],
                "updates": updates_list[_]
            }
            for _ in range(data.shape[0])
        ]
