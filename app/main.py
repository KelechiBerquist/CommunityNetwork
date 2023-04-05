"""
App entry point
"""
import argparse
import pprint

from app.db_client import DatabaseClient
from app.roster import Roster
from app.interest import Interest
from app.pairing import Pairings
from app.meeting import Meetings
from app.wrangler import Wranglers as Wr

# from app.pairing import Pairing
# from app.meeting import Meeting

# from src.loader import Loaders
# from src.mailer import Mailer

DB_NAME = "SkipLevels"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Assigns SkipLevels meetings given "\
                                                 "Rooster and Interest files.")
    parser.add_argument('--db_url', help="Url for connection to MongoDB instance")
    parser.add_argument('--root_dir', help="Root directory of project")
    parser.add_argument('--iteration', help="Current iteration. Expected format YYYY-MM")
    parser.add_argument('--roster_file', help="Filename of CSE roster file.")
    parser.add_argument('--roster_sheet', help="Name of sheet within roster file that"\
                                               " contains CSE roster information")
    parser.add_argument('--interest_file', help="Filename of interest in SkipLevel.")
    parser.add_argument('--interest_sheet', help="Name of sheet within interest file that "\
                                                 "contains interested parties ")
    parser.add_argument('--pairing_file', help="Filename of pairings in SkipLevel.")
    parser.add_argument('--pairing_sheet', help="Name of sheet within interest file that "\
                                                "contains pairing.")
    args = vars(parser.parse_args())

    pprint.pprint(args)
    # print(args)

    db_conn = DatabaseClient(args["db_url"], DB_NAME)

    for item in [Interest, Roster, Pairings, Meetings]:
        setattr(item, "root_dir", args['root_dir'])
        setattr(item, "db", db_conn)
        setattr(item, "stm_file", "skip_levels_stm.json")

    # # Insert into Roster and Interest collections
    Roster.upsert_roster(args["iteration"], args["roster_file"], args["roster_sheet"])
    Interest.upsert_interest(args["iteration"], args["interest_file"], args["interest_sheet"])
    Meetings.upsert_meeting(args["iteration"], args["pairing_file"], args["pairing_sheet"])
