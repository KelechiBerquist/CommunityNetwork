"""
Purpose: Creates and updates CSE roster

"""

from app.settings import COLUMN_MAPPING, JOB_FAMILY_LEVELS, ROSTER_COLLECTION, \
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
        try:
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
            cls.db.upsert_items(conn_obj, loaded_items)
            APP_LOGGER.info("Upserting values into roster collection completed"
                            " for iteration: %s" % iteration)
        except Exception:
            APP_LOGGER.error("Exception while upserting roster for iteration: %s" % iteration,
                             exc_info=True)
    
    @classmethod
    def inactivate_roster(cls, iteration) -> None:
        """Set the status of everyone on the roster to inactive.
            This ensures that when the new roster data is updated, the most recent records can be
            inserted, particularly in the case of separations.
            
        Parameters:
            iteration: current CommunityNetwork iteration. Expected format YYYY-MM
        """
        try:
            APP_LOGGER.info("Begin invalidating roster for iteration: %s" % iteration)
            # Get DB connection
            APP_LOGGER.debug("Create db connection for upserting values into roster "
                             "collection for iteration: %s" % iteration)
            conn_obj = cls.db.get_collection_conn(ROSTER_COLLECTION)

            # Prepare items for loading
            APP_LOGGER.debug("Getting all roster records for iteration: %s" % iteration)
            current_roster = cls.db.find_items(conn_obj)

            APP_LOGGER.debug("Preparing updated roster records for iteration: %s" % iteration)
            upsert_items = [
                {
                    "key": {"emp_email": _["emp_email"]},
                    "updates": {i: _[i] for i in _ if i != "emp_email"} |
                               {"emp_status": 0}
                } for _ in current_roster
            ]

            # Insert data into DB
            APP_LOGGER.debug("Upserting invalidated roster status into roster collection begins"
                             " for iteration: %s" % iteration)
            cls.db.upsert_items(conn_obj, upsert_items)
            APP_LOGGER.info("Upserting invalidated roster status completed for iteration: %s" %
                            iteration)
        except Exception:
            APP_LOGGER.error("Exception while invalidated roster status for iteration: %s" %
                             iteration, exc_info=True)

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
        APP_LOGGER.debug("Passed arguments are filename: %s \t sheet_name: %s \t iteration: %s" %
                         (filename, sheet_name, iteration))

        APP_LOGGER.debug("Begin reading file from path '%s' for iteration: %s" %
                         (filename, iteration))
        data = Wr.read_file(filename, sheet_name)

        APP_LOGGER.debug("Begin fixing date column for iteration: %s" % iteration)
        data = Wr.fix_date_columns(data, ROSTER_DATE_COLUMNS)

        APP_LOGGER.debug("Begin fixing column names for iteration: %s" % iteration)
        data = Wr.fix_column_names(data, COLUMN_MAPPING)
        
        data["job_level"] = data["job_family"].apply(lambda _: JOB_FAMILY_LEVELS[_])
        data["emp_status"] = 1
        
        key_cols = ["emp_email"]
        update_cols = [_ for _ in data.columns if _.lower() != "emp_email"]

        APP_LOGGER.debug("Defining keys and update columns for meeting upsert "
                         "for iteration: %s" % iteration)
        keys_list = data[key_cols].to_dict(orient="records")
        updates_list = data[update_cols].to_dict(orient="records")

        return [
            {
                "key": keys_list[_],
                "updates": updates_list[_]
            }
            for _ in range(data.shape[0])
        ]
