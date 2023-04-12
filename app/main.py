"""
App entry point
"""
import argparse
import warnings

from app.db_client import DatabaseClient
from app.roster import Roster
from app.interest import Interest
from app.meeting import Meetings
from app.settings import APP_LOGGER, INPUT_FILES

warnings.simplefilter(action='ignore', category=FutureWarning)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Assigns CommunityNetwork meetings given "
                                                 "Rooster, Interest files, and optionally "
                                                 "pairing file.")
    parser.add_argument('--db_url', help="Url for connection to MongoDB instance.")
    parser.add_argument('--db_name', help="Name of database.")
    parser.add_argument('--iteration', help="Current iteration. Expected format YYYY-MM")
    args = vars(parser.parse_args())

    db_conn = DatabaseClient(args["db_url"], args["db_name"])

    APP_LOGGER.info("Setting class attribute for collection classes")
    for item in [Interest, Roster, Meetings]:
        setattr(item, "db", db_conn)

    APP_LOGGER.info("Inserting roster into collection")
    Roster.upsert_roster(args["iteration"],
                         INPUT_FILES["roster"]["file"].format(iteration=args["iteration"]),
                         INPUT_FILES["roster"]["sheet"])
    
    APP_LOGGER.info("Inserting interest into collection")
    Interest.upsert_interest(args["iteration"],
                             INPUT_FILES["interest"]["file"].format(iteration=args["iteration"]),
                             INPUT_FILES["interest"]["sheet"])
    
    APP_LOGGER.info("Update meetings info in collection")
    Meetings.upsert_meeting(args["iteration"],
                            INPUT_FILES["pairs"]["file"].format(iteration=args["iteration"]),
                            INPUT_FILES["pairs"]["sheet"])
