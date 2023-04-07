"""
Purpose: Data wrangler

"""
import copy
from typing import Union
from collections import namedtuple

import pandas as pd
import numpy as np
from pandas import DataFrame

from app.settings import APP_LOGGER, BASE_ITERATION_NAME, BASE_ITERATION_NUMBER


PairLevels = namedtuple("Pairs", ["junior", "senior"])


class Wranglers:

    @staticmethod
    def read_file(file_path: str, sheet_name: str) -> DataFrame:
        """Read provided file and return data frame

            Parameters:
                file_path: path to file to be read into dataframe.
                sheet_name: name of sheet within file to be read into dataframe.
            Returns: pandas DataFrame of data contained within file (and sheet if given)
        """
        # print("In Wrangler: Filename: {0}, Sheet: {1}".format(file_path, sheet_name))
        APP_LOGGER.debug("Reading file from path")
        if file_path.endswith(".xlsx"):
            return pd.read_excel(file_path, sheet_name=sheet_name)
        elif file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        else:
            msg = "Provided file '{0}' has unknown file extension".format(file_path)
            raise ValueError(msg)

    @staticmethod
    def write_file(data, file_path: str, sheet_name: str) -> None:
        """Read provided file and return data frame

            Parameters:
                data: DataFrame to be written to file
                file_path: path to file to be read into dataframe.
                sheet_name: name of sheet within file to be read into dataframe.
            Returns: pandas DataFrame of data contained within file (and sheet if given)
        """
        APP_LOGGER.debug("Writing file to path")
        if file_path.endswith(".xlsx"):
            data.to_excel(file_path, sheet_name=sheet_name, index=False)
        elif file_path.endswith(".csv"):
            data.to_csv(file_path, index=False, header=True)
        else:
            msg = "Provided file '{0}' has unknown file extension".format(file_path)
            raise ValueError(msg)

    @staticmethod
    def fix_date_columns(data: DataFrame, date_cols: Union[str, list]):
        """Prepare data to be loaded into the roster

        Parameters:
            data: DataFrame with date columns to be fixed
            date_cols: column or list of columns that have data values
            
        Returns: DataFrame with date columns fixed
        """
        
        date_columns = [date_cols] if isinstance(date_cols, str) else date_cols[:]
        frame = copy.deepcopy(data)
        for col in date_columns:
            frame[col] = frame[col].replace({np.nan: None, pd.NaT: None})
        APP_LOGGER.debug("Fixed date column")
        return frame

    @staticmethod
    def fix_column_names(data: DataFrame, column_mapping: dict) -> DataFrame:
        """Prepare data to be loaded into the roster

        Parameters:
            data: DataFrame with column to be fixed
            column_mapping: column rename mapping

        Returns: DataFrame with fixed columns
        """
        frame = copy.deepcopy(data)
        # Perform intentional column mapping
        if column_mapping is not None:
            frame = frame.rename(columns=column_mapping)
    
        # Perform naive column mapping
        update_cols_dict = {
            _: _.lower().replace(" ", "_")
            for _ in frame.columns
        }

        APP_LOGGER.debug("Fixed column names")
        return frame.rename(columns=update_cols_dict)

    @staticmethod
    def get_iteration_number(iteration) -> int:
        """Prepare data to be loaded into the roster

        Parameters:
            iteration: current SkipLevels iteration

        Returns: DataFrame with fixed columns
        """
        
        first_iteration = "{0}-01".format(BASE_ITERATION_NAME)
        current_iteration = "{0}-01".format(iteration)
        quarters = pd.date_range(first_iteration, current_iteration, freq="Q")
        APP_LOGGER.debug("Calculated iteration number")
        return BASE_ITERATION_NUMBER + len(quarters)

    @staticmethod
    def get_pairing_level(data: DataFrame, record: list) -> namedtuple:
        """Determine the junior and senior within the pairs in the meeting

        Parameters:
            data: DataFrame with content to be searched
            record: list with emails of the participants in the pair
        Returns: tuple of junior and senior emails
        """
        search_criterion = (data["emp_email"] == record[0]) | (data["emp_email"] == record[1])
        persons = data[search_criterion].to_dict(orient="record")
        
        # print(record, persons, sep="\n\n", end="\n\n\n")
        
        if persons[0]["job_level"] == persons[1]["job_level"]:
            msg = "Level between the pair in the meeting are equal. "\
                  "Level provided: {0}".format(persons[0]["job_level"])
            # raise ValueError(msg)
        junior = persons[0] if persons[0]["job_level"] < persons[1]["job_level"] else persons[1]
        senior = persons[0] if persons[0]["job_level"] > persons[1]["job_level"] else persons[1]
        
        # APP_LOGGER.debug("Retrieved pair level")
        return PairLevels(junior["emp_email"], senior["emp_email"])

    @staticmethod
    def get_pairings_with_levels(data: DataFrame, record: list) -> dict:
        """Determine the junior and senior within the pairs in the meeting

        Parameters:
            data: DataFrame with content to be searched
            record: list with emails of the participants in the pair
        Returns: DataFrame with fixed columns
        """
        search_criterion = (data["emp_email"] == record[0]) | (data["emp_email"] == record[1])
        persons = data[search_criterion].to_dict(orient="record")
        
        if persons[0]["job_level"] == persons[1]["job_level"]:
            msg = "Level between the pair in the meeting are equal. "\
                  "Level provided: {0}".format(persons[0]["job_level"])
            raise ValueError(msg)
        junior = persons[0] if persons[0]["job_level"] < persons[1]["job_level"] else persons[1]
        senior = persons[0] if persons[0]["job_level"] > persons[1]["job_level"] else persons[1]
        
        return {"junior": junior, "senior": senior}

    @staticmethod
    def get_possible_connections(data: list) -> list:
        """Parse data from database to get list of potential connections

        Parameters:
            data: list of employees with most recent connections, and
                  embedded list of possible connections
        Returns: list of employees with potential connections and invalid connections
        """
        return [
            {
                "emp": item["employee"][0],
                "potential_connection": item["potential_connection"],
                "invalid_match": set(
                        [_['emp_email'] for _ in item["counselee"]] +
                        [_['emp_email'] for _ in item["pml"]] +
                        [_['senior'] for _ in item["junior_in_meeting"]] +
                        [_['junior'] for _ in item["senior_in_meeting"]]),
            } for item in data]

    @staticmethod
    def get_probable_connections(data: list) -> list:
        """Parse data from database to get list of valid connections

        Parameters:
            data: list of employees with most recent connections, and lists
                  of invalid and possible connections
        Returns: list of employees with embedded list of only valid connections
        """
        # TODO: Check for unmatched interested candidates and attempt to manually match them.
        return [
            {
                "emp": i["emp"],
                "valid_match": [
                    _ for _ in i["potential_connection"]
                    if (_["emp_email"] not in i["invalid_match"]) and (
                        (i["emp"]["job_level"] == 1 and _["job_level"] == 3) or
                        (i["emp"]["job_level"] == 2 and 3 <= _["job_level"] <= 4) or
                        (i["emp"]["job_level"] == 3 and _["job_level"] != i["emp"]["job_level"]) or
                        (i["emp"]["job_level"] == 4 and 2 <= _["job_level"] <= 3) or
                        (i["emp"]["job_level"] >= 5 and _["job_level"] == 3))
                ]
            } for i in data]

    @staticmethod
    def get_assignment_data(data: list) -> list:
        """Parse data from database to get list of valid connections

        Parameters:
            data: list of employees with most recent connections, and lists
                  of invalid and possible connections
        Returns: list of employees with embedded list of only valid connections
        """
        # TODO: Sort data for matches so the parties with the fewest possible
        #  options get matched first
        a = [
            {
                "emp": i["emp"]["emp_email"],
                "probables": [j["emp"]["emp_email"] for j in i["valid_match"]]
            } for i in data]
        a = a.sort(key=lambda i: len(i["probables"]))
        return a
