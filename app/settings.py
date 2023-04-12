import logging
import os

APPLICATION_NAME = "CommunityNetwork"
ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
LOG_FILENAME = os.path.join(ROOT_DIR, "log", "app.log")

# Create logger
APP_LOGGER = logging.getLogger(APPLICATION_NAME)
APP_LOGGER.setLevel(logging.DEBUG)
# Create file handler which logs even debug messages
APP_LOGGER_FILE_HANDLER = logging.FileHandler(os.path.abspath(LOG_FILENAME))
APP_LOGGER_FILE_HANDLER.setLevel(logging.DEBUG)
# Create console handler with a higher log level
APP_LOGGER_CONSOLE_HANDLER = logging.StreamHandler()
APP_LOGGER_CONSOLE_HANDLER.setLevel(logging.ERROR)
# Create formatter and add it to the handlers
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s '
                              '- %(funcName)s - %(lineno)d - %(message)s')
APP_LOGGER_FILE_HANDLER.setFormatter(FORMATTER)
APP_LOGGER_CONSOLE_HANDLER.setFormatter(FORMATTER)
# Add the handlers to the logger
APP_LOGGER.addHandler(APP_LOGGER_FILE_HANDLER)
APP_LOGGER.addHandler(APP_LOGGER_CONSOLE_HANDLER)


# Set other app constants
ROSTER_COLLECTION = "roster"
MEETING_COLLECTION = "meetings"
INTEREST_COLLECTION = "interest"
INTEREST_COLUMN_NAME = "indicated_interest"
BASE_ITERATION_NAME = "2023-03"
BASE_ITERATION_NUMBER = 1
CONNECTION_RESET = 8
UPPER_PAIR_PERCENT = 0.9
LOWER_PAIR_PERCENT = 0.8
EXPLORATION_DEPTH = 2
OUTPUT_FILES = {
    "enriched_matched": os.path.join(ROOT_DIR, "data", "output", "{iteration}",
                                     "enriched_matched_{iteration}.json"),
    "matched": os.path.join(ROOT_DIR, "data", "output", "{iteration}",
                            "matched_{iteration}.json"),
    "unmatched": os.path.join(ROOT_DIR, "data", "output", "{iteration}",
                              "unmatched_{iteration}.json")
}
INPUT_FILES = {
    "roster": {
        "file": os.path.join(ROOT_DIR, "data", "input", "{iteration}", "{iteration}_Roster.xlsx"),
        "sheet": "Roster"
    },
    "pairs": {
        "file": os.path.join(ROOT_DIR, "data", "input", "{iteration}", "{iteration}_Pairs.xlsx"),
        "sheet": "Pairs"
    },
    "interest": {
        "file": os.path.join(ROOT_DIR, "data", "input", "{iteration}", "{iteration}_Interest.xlsx"),
        "sheet": "Interest"
    }
}


# Level order represents pair preference
LEVEL_MATCH_MAP = {
    1: [3],
    2: [4, 3, 5],
    3: [1, 6, 2, 5, 4],
    4: [2, 3],
    5: [3, 2],
    6: [3],
}

JOB_FAMILY_LEVELS = {"6-Associates": 1, "4-Sr. Associates": 2, "3-Managers": 3,
                     "2-Directors/Sr. Managers": 4, "0-MDs": 5, "1-Partners/Principals": 6}

COLUMN_MAPPING = {"NAME": "emp_name", "PREF NAME": "emp_pref_name", "EMAIL ADDRESS": "emp_email"}

ROSTER_DATE_COLUMNS = ["HIRE DATE", "REHIRE DATE", "ADJ SERV DATE"]

EMAIL_TEMPLATE = "Hello {senior} and {junior}," \
                 "\nI hope you are doing well and had a restful Super Bowl weekend." \
                 "\n\nAs part of our on-going effort to build a more connected C&SE " \
                 "community, you have been matched in the current {initiative_name} iteration." \
                 "\nIt is expected that you will participate in a 30- to 60-minute " \
                 "in-person or virtual 1-on-1 meeting before 2023-03-15, as your " \
                 "schedules permit.\n\n{junior}, please could you reach out to {senior}" \
                 " to schedule a meeting?\n\nI will be reaching out after {deadline} " \
                 "to gather feedback about your meeting and suggestions for subsequent " \
                 "{initiative_name} iterations.\nThank you for your effort towards building a " \
                 "better connected, inclusive, and resilient community.\n\n"
