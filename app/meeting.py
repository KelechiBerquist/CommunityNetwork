"""
Purpose: Creates and updates CommunityNetwork Meetings
"""
import copy
import json
import os

from app.pairing import Pairings
from app.queries import PAIRED, UNPAIRED
from app.settings import APP_LOGGER, INTEREST_COLLECTION, MEETING_COLLECTION, OUTPUT_FILES
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
        try:
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
            cls.db.upsert_items(conn_obj, loaded_items)
            APP_LOGGER.info("Upserting values into meeting collection completed "
                            "for iteration: %s" % iteration)
            
            APP_LOGGER.info("Pairing completed for iteration: %s" % iteration)
        except Exception:
            APP_LOGGER.error("Exception while upserting meeting for iteration: %s" % iteration,
                             exc_info=True)

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
        # TODO: Prioritise the people that have not been paired
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
    def get_paired_interested_parties(cls, iteration: str = None):
        """Retrieve enriched information for meeting

        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM

        """
        APP_LOGGER.info("Begin writing information about paired parties for iteration: %s"
                        % iteration)
        # Get DB connection
        APP_LOGGER.debug("Create interest connection for iteration: %s" % iteration)
        conn_obj = cls.db.get_collection_conn(MEETING_COLLECTION)

        paired_file = OUTPUT_FILES["paired"].format(iteration=iteration)
        create_dirs(paired_file)

        paired = copy.deepcopy(PAIRED)
        paired[0]["$match"]['iteration_name'] = \
            paired[0]["$match"]['iteration_name'].format(current_iteration=iteration)
        
        APP_LOGGER.debug("Querying paired parties for iteration: %s" % iteration)
        wrangled_paired = [
            {
                "iteration_number": item["iteration_number"],
                "senior": item["senior_in_meeting"][0],
                "junior": item["junior_in_meeting"][0],
            } for item in conn_obj.aggregate(paired)]

        APP_LOGGER.debug("Writing information about paired parties for iteration: %s" % iteration)
        with open(paired_file, "w") as writer:
            json.dump(wrangled_paired, writer)
        APP_LOGGER.info("Completed writing information about paired parties for iteration: %s"
                        % iteration)

    @classmethod
    def get_unpaired_interested_parties(cls, iteration: str = None):
        """Retrieve list of interested parties that were not paired

        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM

        """
        APP_LOGGER.info("Begin writing information about unpaired parties for iteration: %s"
                        % iteration)
        # Get DB connection
        APP_LOGGER.debug("Create interest connection for iteration: %s" % iteration)
        conn_obj = cls.db.get_collection_conn(INTEREST_COLLECTION)

        unpaired_file = OUTPUT_FILES["unpaired"].format(iteration=iteration)
        create_dirs(unpaired_file)
        unpaired = copy.deepcopy(UNPAIRED)

        unpaired[0]["$match"]['iteration_name'] = \
            unpaired[0]["$match"]['iteration_name'].format(current_iteration=iteration)
        unpaired[2]["$lookup"]["pipeline"][0]["$match"]['iteration_name'] = \
            unpaired[2]["$lookup"]["pipeline"][0]["$match"]['iteration_name'].format(
                current_iteration=iteration)
        unpaired[3]["$lookup"]["pipeline"][0]["$match"]['iteration_name'] = \
            unpaired[3]["$lookup"]["pipeline"][0]["$match"]['iteration_name'].format(
                current_iteration=iteration)

        APP_LOGGER.debug("Querying unpaired parties for iteration: %s" % iteration)
        wrangled_unpaired = [{
            "iteration_number": item["iteration_number"],
            "employee": item["employee"][0]} for item in conn_obj.aggregate(unpaired)]

        APP_LOGGER.debug("Writing information about unpaired parties for iteration: %s" % iteration)
        with open(unpaired_file, "w") as writer:
            json.dump(wrangled_unpaired, writer)
        APP_LOGGER.info("Completed writing information about unpaired parties for iteration: %s"
                        % iteration)
