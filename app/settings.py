ROSTER_COLLECTION = "roster"
MEETING_COLLECTION = "meetings"
INTEREST_COLLECTION = "interest"
INTEREST_COLUMN_NAME = "indicated_interest"
DB_NAME = "SkipLevels"
BASE_ITERATION_NAME = "2023-03"
BASE_ITERATION_NUMBER = 1

# DONT_MATCH_COLL_NAME = "dont_match"

JOB_FAMILY_LEVELS = {"6-Associates": 1, "4-Sr. Associates": 2, "3-Managers": 3,
                     "2-Directors/Sr. Managers": 4, "0-MDs": 5, "1-Partners/Principals": 6}

COLUMN_MAPPING = {"NAME": "emp_name", "PREF NAME": "emp_pref_name", "EMAIL ADDRESS": "emp_email"}

ROSTER_DATE_COLUMNS = ["HIRE DATE", "REHIRE DATE", "ADJ SERV DATE"]

EMAIL_TEMPLATE = "Hello {senior} and {junior}," \
                 "\nI hope you are doing well and had a restful Super Bowl weekend." \
                 "\n\nAs part of our on-going effort to build a more connected C&SE " \
                 "community, you have been matched in the current SkipLevels iteration." \
                 "\nIt is expected that you will participate in a 30- to 60-minute " \
                 "in-person or virtual 1-on-1 meeting before 2023-03-15, as your " \
                 "schedules permit.\n\n{junior}, please could you reach out to {senior}" \
                 " to schedule a meeting?\n\nI will be reaching out after {deadline} " \
                 "to gather feedback about your meeting and suggestions for subsequent " \
                 "SkipLevels iterations.\nThank you for your effort towards building a " \
                 "better connected, inclusive, and resilient community.\n\n"

SIGNED_EMAIL_TEMPLATE_ = "Hello {senior} and {junior}," \
                         "\nI hope you are doing well and had a restful superbowl weekend." \
                         "\n\nAs part of our on-going effort to build a more connected C&SE " \
                         "community, you have been matched in the current SkipLevels iteration." \
                         "\nIt is expected that you will participate in a 30- to 60-minute " \
                         "in-person or virtual 1-on-1 meeting before 2023-03-15, as your " \
                         "schedules permit.\n\n{junior}, please could you reach out to {senior}" \
                         " to schedule a meeting?\n\nI will be reaching out after {deadline} " \
                         "to gather feedback about your meeting and suggestions for subsequent " \
                         "SkipLevels iterations.\nThank you for your effort towards building a " \
                         "better connected, inclusive, and resilient community." \
                         "\n\n\nKelechi Berquist (she/her/hers)" \
                         "\nManager, Data Engineering, Lighthouse" \
                         "\nKPMG LLP | 8350 Broad Street | Suite 900 | McLean, VA 22102" \
                         "\nCell: +1 267-243-6341 | kberquist@kpmg.com"
