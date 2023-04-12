"""
Purpose: Creates and updates CSE roster

"""

import os

from app.db_client import DatabaseClient as Dc
from app.settings import COLUMN_MAPPING, JOB_FAMILY_LEVELS, ROOT_DIR, ROSTER_COLLECTION, \
    ROSTER_DATE_COLUMNS, APP_LOGGER
from app.wrangler import Wranglers as Wr


class Roster:
    """Creates and updates CSE roster
    """
    db = None
    
    @classmethod
    def upsert_roster(cls, iteration: str, filename: str, sheet_name: str) -> None:
        """Load data for CSE roster

        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with roster information
        """
        # TODO: Set all records in roster as inactive before performing upserts
        
        APP_LOGGER.info("Begin roster upsert for iteration: %s" % iteration)
        # Prepare items for loading
        loaded_items = cls.prepare_roster(iteration, filename, sheet_name)
    
        # Get DB connection
        APP_LOGGER.debug("Create db connection for upserting values into roster "
                         "collection for iteration: %s" % iteration)
        conn_obj = cls.db.get_collection_conn(ROSTER_COLLECTION)
    
        # Insert data into DB
        APP_LOGGER.debug("Upserting values into roster collection begins"
                         " for iteration: %s" % iteration)
        Dc.upsert_items(conn_obj, loaded_items)
        APP_LOGGER.info("Upserting values into roster collection completed"
                        " for iteration: %s" % iteration)

    @classmethod
    def prepare_roster(cls, iteration: str, filename: str, sheet_name: str) -> list:
        """Prepare data to be loaded into the roster
        
        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with roster information
            
        Returns:
        """
        APP_LOGGER.info("Begin preparing data for roster upsert for iteration: %s" % iteration)
        file_path = os.path.join(ROOT_DIR, "data", "input", iteration, filename)

        APP_LOGGER.debug("Begin reading file from path ""for iteration: %s" % iteration)
        data = Wr.read_file(file_path, sheet_name)

        APP_LOGGER.debug("Begin fixing date column for iteration: %s" % iteration)
        data = Wr.fix_date_columns(data, ROSTER_DATE_COLUMNS)

        APP_LOGGER.debug("Begin fixing column names for iteration: %s" % iteration)
        data = Wr.fix_column_names(data, COLUMN_MAPPING)
        
        data["job_level"] = data["job_family"].apply(lambda _: JOB_FAMILY_LEVELS[_])
        
        key_cols = ["emp_email"]
        update_cols = [_ for _ in data.columns if _.lower() != "emp_email"]

        APP_LOGGER.debug("Defining keys and update columns for meeting upsert "
                         "for iteration: %s" % iteration)
        keys_list = data[key_cols].to_dict(orient="record")
        updates_list = data[update_cols].to_dict(orient="record")

        return [
            {
                "key": keys_list[_],
                "updates": updates_list[_]
            }
            for _ in range(data.shape[0])
        ]
