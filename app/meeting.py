"""
Purpose: Creates and updates SkipLevels Meetings

"""

import os
import copy
import sys
import json

from datetime import datetime

import pandas as pd
import numpy as np

from app.pairing import Pairings
from app.db_client import DatabaseClient as Dc
from app.settings import MEETING_COLLECTION
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
        # Prepare items for loading
        loaded_items = cls.prepare_meeting(iteration, filename, sheet_name)

        # Get DB connection
        conn_obj = cls.db.get_collection_conn(MEETING_COLLECTION)

        # Insert data into DB
        Dc.upsert_items(conn_obj, loaded_items)

    @classmethod
    def prepare_meeting(cls, iteration: str=None, filename: str=None, sheet_name: str=None):
        """Prepare data for meeting

        Parameters:
            iteration: current SkipLevels iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with interest information

        """
        if filename is not None:
            paired = Pairings.get_pairings_from_file(iteration, filename, sheet_name)
        else:
            paired = []

        key_cols = ["iteration_name", "junior", "senior"]
        update_cols = ["iteration_number"]

        return [
            {
                "key": {i: _[i] for i in key_cols},
                "updates": {i: _[i] for i in update_cols},
            }
            for _ in paired
        ]
