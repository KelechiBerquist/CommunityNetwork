"""
Purpose: Creates and updates CommunityNetwork Meetings
"""
import copy
import json
import os

from app.db_client import DatabaseClient as Dc
from app.pairing import Pairings
from app.queries import ENRICHED_MEETING_INFO
from app.settings import APP_LOGGER, INTEREST_COLLECTION, MEETING_COLLECTION, OUTPUT_FILES, ROOT_DIR
from app.utils import create_dirs


class Meetings:
    """Creates and updates CommunityNetwork Meetings
    """
    db = None
    
    @classmethod
    def upsert_meeting(cls, iteration: str = None, filename: str = None, sheet_name: str = None):
        """Load data for meeting

        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with interest information

        """
        APP_LOGGER.info("Begin meeting upsert")
        # Get DB connection
        APP_LOGGER.debug("Create db connection for upserting values into meeting "
                         "collection for iteration: %s" % iteration)
        conn_obj = cls.db.get_collection_conn(MEETING_COLLECTION)
        interest_conn_obj = cls.db.get_collection_conn(INTEREST_COLLECTION)

        # Prepare items for loading
        APP_LOGGER.debug("Prepare meeting data")
        loaded_items = cls.prepare_meeting(iteration, filename, sheet_name, interest_conn_obj)

        # Insert data into DB
        APP_LOGGER.debug("Upserting values into meeting collection begins "
                         "for iteration: %s" % iteration)
        Dc.upsert_items(conn_obj, loaded_items)
        APP_LOGGER.info("Upserting values into meeting collection completed "
                        "for iteration: %s" % iteration)

        APP_LOGGER.info("Recording enriched meeting information for iteration: %s" % iteration)
        cls.retrieve_meeting_parties(iteration, conn_obj)
        APP_LOGGER.info("Pairing completed for iteration: %s" % iteration)

    @classmethod
    def prepare_meeting(cls, iteration: str = None, filename: str = None, sheet_name: str = None,
                        interest_conn = None):
        """Prepare data for meeting

        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
            filename: path to file containing roster
            sheet_name: name of sheet with interest information
            interest_conn: Interest connection object

        """
        APP_LOGGER.info("Begin preparing data for meeting upsert for iteration: %s" % iteration)
        if os.path.exists(filename):
            APP_LOGGER.debug("Preparing data for meeting upsert from file "
                             "for iteration: %s" % iteration)
            paired = Pairings.get_pairings_from_file(iteration, filename, sheet_name)
        elif interest_conn is not None:
            APP_LOGGER.debug("Preparing data for meeting upsert from database "
                             "for iteration: %s" % iteration)
            paired = Pairings.get_pairings_from_database(iteration, interest_conn)
        else:
            APP_LOGGER.error("Meeting data can be retrieved from database or file "
                             "for iteration: %s" % iteration)
            raise NotImplementedError("Meeting data can be retrieved from database or file")

        APP_LOGGER.debug("Defining keys and update columns for meeting upsert "
                         "for iteration: %s" % iteration)
        key_cols = ["iteration_name", "junior", "senior"]
        update_cols = ["iteration_number"]

        return [
            {
                "key": {i: _[i] for i in key_cols},
                "updates": {i: _[i] for i in update_cols},
            }
            for _ in paired
        ]

    @classmethod
    def retrieve_meeting_parties(cls, iteration: str = None, meeting_conn = None):
        """Retrieve enriched information for meeting

        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
            meeting_conn: meeting connection object

        """
        enriched_file = OUTPUT_FILES["enriched_matched"].format(iteration=iteration)
        create_dirs(enriched_file)
        enriched = copy.deepcopy(ENRICHED_MEETING_INFO)

        enriched[0]["$match"]['iteration_name'] = enriched[0]["$match"][
            'iteration_name'].format(iteration=iteration)
        
        with open(enriched_file, "w") as writer:
            json.dump([item for item in meeting_conn.aggregate(enriched)], writer)
