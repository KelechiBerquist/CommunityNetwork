"""
Purpose: Manages interest in current CommunityNetwork initiative

"""

import os

import pandas as pd

from app.db_client import DatabaseClient as Dc
from app.settings import APP_LOGGER, COLUMN_MAPPING, INTEREST_COLLECTION, INTEREST_COLUMN_NAME, \
    JOB_FAMILY_LEVELS, ROOT_DIR
from app.wrangler import Wranglers as Wr


class Interest:
    """Manages interest in current CommunityNetwork initiative
    """
    db = None
    
    @classmethod
    def upsert_interest(cls, iteration: str, filename: str, sheet_name: str) -> None:
        """Load data for CSE interest

        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
            filename: path to file containing interest
            sheet_name: name of sheet with interest information
        """
        APP_LOGGER.info("Begin meeting upsert for iteration: %s" % iteration)
        # Prepare items for loading
        loaded_items = cls.prepare_interest(iteration, filename, sheet_name)

        # Get DB connection
        APP_LOGGER.debug("Create db connection for upserting values into interest "
                         "collection for iteration: %s" % iteration)
        conn_obj = cls.db.get_collection_conn(INTEREST_COLLECTION)

        # Insert data into DB
        APP_LOGGER.debug("Upserting values into interest collection begins "
                         "for iteration: %s" % iteration)
        Dc.upsert_items(conn_obj, loaded_items)
        APP_LOGGER.info("Upserting values into interest collection completed "
                        "for iteration: %s" % iteration)

    @classmethod
    def prepare_interest(cls, iteration: str, filename: str, sheet_name: str) -> list:
        """Prepare data to be loaded into the interest
        
        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
            filename: path to file containing interest
            sheet_name: name of sheet with interest information
            
        Returns:
        """
        APP_LOGGER.info("Begin preparing data for interest upsert for iteration: %s" % iteration)
        file_path = os.path.join(ROOT_DIR, "data", "input", iteration, filename)

        APP_LOGGER.debug("Begin reading file from path for iteration: %s" % iteration)
        data = Wr.read_file(file_path, sheet_name)

        APP_LOGGER.debug("Begin fixing column names for iteration: %s" % iteration)
        data = Wr.fix_column_names(data, COLUMN_MAPPING)

        APP_LOGGER.debug("Performing additional transformations for iteration: %s" % iteration)
        data["job_level"] = data["job_family"].apply(lambda _: JOB_FAMILY_LEVELS[_])
        data["iteration_name"] = iteration
        data["iteration_number"] = Wr.get_iteration_number(iteration)
        
        # Filter out interested parties
        APP_LOGGER.debug("Filtering interested parties for iteration: %s" % iteration)
        data = data[(data["job_level"] >= 3) | pd.notnull(data[INTEREST_COLUMN_NAME])]

        APP_LOGGER.debug("Defining keys and update columns for meeting "
                         "upsert for iteration: %s" % iteration)
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
