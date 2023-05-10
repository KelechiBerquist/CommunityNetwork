#!/bin/bash


WORK_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")"  &> /dev/null && pwd )"
DB_URL="$1"
DB_NAME="$2"
ITERATION="$3"

echo  "WORK_DIR:          $WORK_DIR"
echo  "DB_URL             $DB_URL"
echo  "DB_NAME            $DB_NAME"
echo  "ITERATION          $ITERATION"


cd "$WORK_DIR" || exit
echo -e "\nCurrent working directory:   $(pwd)"

echo -e "\nSetting up virtual environment"
python3 -m venv venv
source venv/bin/activate
#python -m pip install --upgrade pip
#python -m pip install -r requirements.txt


echo -e "\nRun application\n"
python -m app.main \
    --db_url "$DB_URL"  \
    --db_name "$DB_NAME"  \
    --iteration "$ITERATION"
