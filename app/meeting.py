"""
Purpose: Creates and updates SkipLevels Meetings

"""
import logging
import os
import copy
import sys
import json

from datetime import datetime

import pandas as pd
import numpy as np

from app.pairing import Pairings
from app.db_client import DatabaseClient as Dc
from app.settings import APP_LOGGER, MEETING_COLLECTION
from app.wrangler import Wranglers as Wr


class Meetings:
    """Creates and updates SkipLevels Meetings
    """
    db = None
    root_dir = None
    
    @classmethod
    def upsert_meeting(cls, iteration: str=None, filename: str=None, sheet_name: str=None):
        """Load data for meeting

        Parameters:
            iteration: current SkipLevels iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with interest information

        """
        APP_LOGGER.info("Begin meeting upsert")
        # Prepare items for loading
        loaded_items = cls.prepare_meeting(iteration, filename, sheet_name)

        # Get DB connection
        APP_LOGGER.debug("Create db connection for upserting values into meeting collection")
        conn_obj = cls.db.get_collection_conn(MEETING_COLLECTION)

        # Insert data into DB
        APP_LOGGER.debug("Upserting values into meeting collection begins")
        Dc.upsert_items(conn_obj, loaded_items)
        APP_LOGGER.info("Upserting values into meeting collection completed")

    @classmethod
    def prepare_meeting(cls, iteration: str=None, filename: str=None, sheet_name: str=None):
        """Prepare data for meeting

        Parameters:
            iteration: current SkipLevels iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with interest information

        """
        # TODO: Check for unmatched interested candidates and attempt to manually match them.
        APP_LOGGER.info("Begin preparing data for meeting upsert")
        # print("Filename: {0}, Sheet: {1}".format(filename, sheet_name))
        if filename is not None and filename != "" and not \
                (filename.endswith("xlsx") and sheet_name == ""):
            APP_LOGGER.debug("Preparing data for meeting upsert from file")
            paired = Pairings.get_pairings_from_file(iteration, filename, sheet_name)
        else:
            APP_LOGGER.debug("Preparing data for meeting upsert from database")
            paired = []

        APP_LOGGER.debug("Defining keys and update columns for meeting upsert")
        
        key_cols = ["iteration_name", "junior", "senior"]
        update_cols = ["iteration_number"]

        return [
            {
                "key": {i: _[i] for i in key_cols},
                "updates": {i: _[i] for i in update_cols},
            }
            for _ in paired
        ]
