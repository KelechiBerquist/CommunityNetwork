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

    @classmethod
    def read_file(cls, file_path: str, sheet_name: str) -> DataFrame:
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

    @classmethod
    def write_file(cls, data, file_path: str, sheet_name: str) -> None:
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

    @classmethod
    def fix_date_columns(cls, data: DataFrame, date_cols: Union[str, list]):
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

    @classmethod
    def fix_column_names(cls, data: DataFrame, column_mapping: dict) -> DataFrame:
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

    @classmethod
    def get_iteration_number(cls, iteration) -> int:
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

    @classmethod
    def get_pairing_level(cls, data: DataFrame, record: list) -> namedtuple:
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

    @classmethod
    def get_pairings_with_levels(cls, data: DataFrame, record: list) -> dict:
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

    #
    # @classmethod
    # def prepare_roster(cls, root_dir: str, roster_file: str, sheet_name: str):
    #     """Prepare data to
    #
    #     :param root_dir:
    #     :type root_dir:
    #     :param roster_file:
    #     :type roster_file:
    #     :param sheet_name:
    #     :type sheet_name:
    #     :return:
    #     :rtype:
    #     """
    #     job_family_file = os.path.join()
    #     job_family_levels = json.load()
    #     members = pd.read_excel(file_name, sheet_name=sheet_name)
    #     members["_id"] = members["EMAIL ADDRESS"]
    #     members["HIRE DATE"] = members["HIRE DATE"].replace({np.nan: None, pd.NaT: None})
    #     members["REHIRE DATE"] = members["REHIRE DATE"].replace({np.nan: None, pd.NaT: None})
    #     members["ADJ SERV DATE"] = members["ADJ SERV DATE"].replace({np.nan: None, pd.NaT: None})
    #     members["LEVEL"] = members["JOB FAMILY"].apply(lambda _: JOB_FAMILY_LEVELS[_])
    #
    #     relevant_cols = [
    #         "NAME", "PREF NAME", "EMAIL ADDRESS", "JOB FAMILY", "REGION", "BU REGION",
    #         "PM BU SUBREGION DESCR", "Business Area Descr", "LOCATION DESCR",
    #         "PML NAME", "PML EMAIL", "SPML Name", "EMPL CLASS DESCR", "_id", "LEVEL"
    #
    #     ]
    #     update_cols_dict = {
    #         _: _.lower().replace(" ", "_")
    #         for _ in relevant_cols
    #     }
    #
    #     roster_data = members[relevant_cols].rename(columns=update_cols_dict)
    #     key_cols = ["_id"]
    #     update_cols = [_ for _ in roster_data.columns if _.lower() != "_id"]
    #
    #     cse_members_keys = roster_data[key_cols].to_dict(orient="record")
    #     cse_members_updates = roster_data[update_cols].to_dict(orient="record")
    #
    #     return [
    #         {
    #             "key": cse_members_keys[_],
    #             "updates": cse_members_updates[_]
    #         }
    #         for _ in range(roster_data.shape[0])
    #     ]
    #
    # @classmethod
    # def prepare_interest(cls, file_name: str, sheet_name: str, iteration_quarter: str):
    #     members = pd.read_excel(file_name, sheet_name=sheet_name)
    #
    #     interested = members[
    #         (members["Indicated Interest"] == "Y") |
    #         (members["JOB FAMILY"] == "3-Managers")
    #     ]
    #     interested_data = [
    #         {
    #             "key": {"iteration": iteration_quarter},
    #             "updates": {"participants": [_ for _ in interested["EMAIL ADDRESS"].to_numpy()]}
    #         }
    #     ]
    #
    #     return interested_data
