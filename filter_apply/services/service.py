from http.client import HTTPException
import json
import logging
import configparser
from fastapi import Path
from fastapi.responses import FileResponse
import requests
import pandas as pd
from src.utils.logs import CustomLogger
import numpy as np
import pandas as pd
from datetime import datetime
import requests
import configparser
from src.utils.config import config
import os
from src.filter_apply.daos import dao
from src.filter_apply.models import model
import src.config.conf as cf
from src.config.storage import read_csv_from_s3,upload_dataframe_to_s3
import os

# Initialize logger
logger_instance = CustomLogger(log_level='DEBUG', log_file_name='filterapply.log', log_path='logs')
logger = logger_instance.get_logger()

# Load configuration
config = configparser.ConfigParser()
config.read("secure.ini")
base_url = config['GENERAL']['base_url']
dabase_url = config['GENERAL']['dabase_url']
data_file_path_template = config['GENERAL']['data_file_path']

class Filter:
    def __init__(self):
        self.filter_criteria = None
        self.db = dao.dao()


        
    def filter_apply(self, object_id,token,db):
        """
        Apply filters to the data associated with the given object ID.

        This method retrieves filter criteria from an API, applies these filters 
        to the data in a corresponding CSV file, and updates the server about the 
        applied filter.

        Args:
            object_id (uuid.UUID): The unique identifier of the object to which filters will be applied.

        Returns:
            str: A message indicating whether the filter was successfully applied or was already applied.

        Raises:
            Exception: If there is an error during the filter application process.
        """
        try:
            headers = {
                "Authorization": f"Bearer {token}"
            }
            logger.debug(f"Applying filter for object ID: {object_id}")
            response = requests.get(f"{base_url}filter/{object_id}",headers=headers)
            filter_data = response.json() #if response.ok else []
            self.filter_criteria = filter_data

            # Serialize filter_criteria to a JSON string
            filter_criteria_json = json.dumps(self.filter_criteria)
            logger.info(filter_criteria_json)
            
            #logger.info(self.filter_criteria)
            result = self.apply_filter(object_id,db)
            logger.info(result)
            print(result)
            return result
        except Exception as e:
            logger.error(f"Error in filter_apply: {e}")
            raise e
        



     
    def apply_filter(self, object_id,db):
        """
        Applies filter criteria to the data of a given object by reading the data from a file,
        filtering the data based on the criteria, and then saving the filtered data back to the file.

        Args:
            object_id (UUID): The unique identifier of the object whose data needs to be filtered.

        Returns:
            str: A message indicating the success or failure of the filter application process.

        Raises:
            Exception: If there is an error during the filter application process.
        """
        try:
        
            # Load configuration    
            script_dir = os.path.dirname(__file__)
            relative_path = os.path.join(script_dir, '..','..','..', 'projects', 'datamatter.conf.ini')

            logger.info(f"Relative path to config: {relative_path}")
            inifile = os.path.abspath(relative_path)
            logger.info(f"Absolute path to config: {inifile}")

            cf.loadConfig(config_file=inifile)

            # Get file path from config
            base_path = cf.getBasePath()
            
            logger.info(f"Base path obtained from config: {base_path}")
            
            file_path=cf.getObjectFilePath("users")            
            logger.info(f"file_path is : {file_path}accounts.csv")
            file=read_csv_from_s3("datamatter-qa",file_path+"accounts.csv")   
            logger.info(f"filepath is :{file}")
            

            object_data = file
            # Querying filter info from API
            logger.debug(f"Querying filter info for object ID: {object_id}")
            request_url = f"{base_url}filtered_info/"        
            parameters = {"object_id": object_id}
            logger.debug(f"Request URL: {request_url}")
            logger.debug(f"Parameters: {parameters}")
            response = requests.get(request_url, params=parameters)
            logger.info(f"Response: {response.status_code} - {response.text}")
            is_filtered = response.json() #if response.ok else False
            if is_filtered:
                logger.info("Filter is already applied on this file")
                return "Filter is already applied on this file"

            logger.debug("Applying filter criteria")
            for filter_item in self.filter_criteria:
                filtered_indices = slice(None)  # Initialize with all indices

                if filter_item['type'] == 'date':
                    filtered_indices = (
                        (pd.to_datetime(object_data[config['filter']['date']], errors='coerce') >= pd.to_datetime(
                            filter_item['from_date'], format='%Y-%m-%d')) &
                        (pd.to_datetime(object_data[config['filter']['date']], errors='coerce') <= pd.to_datetime(
                            filter_item['to_date'], format='%Y-%m-%d'))
                    )
                    filter_id = filter_item.get("filter_id")
                    if filter_id is not None:
                        object_data.loc[filtered_indices, 'filter_id'] = filter_id
                elif filter_item['type'] == 'range':
                    filtered_indices = (
                        (object_data[config['filter']['range']].astype(float) >= filter_item['from_range']) &
                        (object_data[config['filter']['range']].astype(float) <= filter_item['to_range'])
                    )
                    filter_id = filter_item.get("filter_id")
                    if filter_id is not None:
                        object_data.loc[filtered_indices, 'filter_id'] = filter_id
                elif filter_item['type'] == 'values':
                    filtered_indices = (
                        object_data[config['filter']['field']].isin(filter_item['values'].split(','))
                    )
                    filter_id = filter_item.get("filter_id")
                    if filter_id is not None:
                        object_data.loc[filtered_indices, 'filter_id'] = filter_id
                elif filter_item['type'] == 'reference':
                    ref_obj_data = pd.read_csv("src/filter_apply/kasdasj.csv")
                    object_data = object_data.merge(ref_obj_data, left_on=filter_item["ref_field"],
                                                    right_on=filter_item["ref_field"], how="inner")
                    filter_id = filter_item.get("filter_id")
                    if filter_id is not None:
                        object_data.loc[:, 'filter_id'] = filter_id
                else:
                    logger.error(f"Invalid filter type: {filter_item['type']}")
                    raise Exception(f"Invalid filter type: {filter_item['type']}")

            logger.debug(f"Saving filtered data:{object_data}")
            #object_data.to_csv(file, index=False)
            object_data=upload_dataframe_to_s3(object_data,"datamatter-qa",file_path+"accounts.csv")
            

            logger.debug("Updating filtered info on server")
            request_url = f"{base_url}update/filtered_info/"
            parameters = {"object_id": object_id}
            response = requests.put(request_url, params=parameters)

            logger.info("Filter is applied successfully.")
            return "Filter is applied successfully."

        except Exception as e:
            logger.error(f"Error in apply_filter: {str(e)}", exc_info=True)
            raise e

    def get_filter_fields(self, object_id):

        """
        Retrieve and categorize filter fields for the given object ID.

        This method fetches metadata about an object from a database, and 
        categorizes the fields into date fields, numeric fields, picklist fields, 
        and other fields based on their attributes.

        Args:
            object_id (str): The unique identifier of the object whose fields 
            are to be retrieved and categorized.

        Returns:
            dict: A dictionary containing lists of categorized field names:
                - date_fields (List[str]): Fields identified as date fields.
                - numeric_fields (List[str]): Fields identified as numeric fields.
                - picklist_fields (List[str]): Fields identified as picklist fields.
                - other_fields (List[str]): Fields that do not match the above categories.

        Raises:
            Exception: If there is an error during the retrieval or categorization process.
        """
        try:
            logger.debug(f"Getting filter fields for object ID: {object_id}")

            date_fields = []
            numeric_fields = []
            picklist_fields = []
            other_fields = []
            request_url = f"{dabase_url}v1/metadata/{object_id}"
            request_url = request_url.format(object_id=object_id)
            response = requests.get(request_url)
            data = response.json() if response.ok else []

            for field_info in data:
                for field_name, attributes in field_info.items():
                    if attributes.get("is_integer") == "true" or attributes.get("is_picklist") == "true" or \
                            attributes.get("is_date") == "true":
                        if attributes.get("is_integer") == "true":
                            numeric_fields.append(field_name)
                        if attributes.get("is_picklist") == "true":
                            picklist_fields.append(field_name)
                        if attributes.get("is_date") == "true":
                            date_fields.append(field_name)
                    else:
                        other_fields.append(field_name)

            result = {
                "date_fields": date_fields,
                "numeric_fields": numeric_fields,
                "picklist_fields": picklist_fields,
                "other_fields": other_fields
            }

            logger.info("Retrieved filter fields successfully.")
            return result

        except Exception as e:
            logger.error(f"Error in get_filter_fields: {e}")
            raise e
        
        
    # def apply_filter(self, file_name):
    #     try:
    #         object_data = pd.read_csv("src/filter_apply/main.csv")
    #         for filter_item in self.filter_criteria:
    #             if filter_item['type'] == 'date':
    #                 object_data = object_data[
    #                     (pd.to_datetime(object_data[config['filter']['date']], errors='coerce') >= pd.to_datetime(filter_item['from_date'], format='%Y-%m-%d')) &
    #                     (pd.to_datetime(object_data[config['filter']['date']], errors='coerce') <= pd.to_datetime(filter_item['to_date'], format='%Y-%m-%d'))
    #                 ]
    #             elif filter_item['type'] == 'range':
    #                 object_data = object_data[
    #                     (object_data[config['filter']['range']].astype(float) >= filter_item['from_range']) &
    #                     (object_data[config['filter']['range']].astype(float) <= filter_item['to_range'])
    #                 ]
    #             elif filter_item['type'] == 'values':
    #                 object_data = object_data[
    #                     object_data[config['filter']['field']].isin(filter_item['values'].split(','))
    #                 ]
    #             elif filter_item['type'] == 'reference':
    #                 ref_obj_data = pd.read_csv("src/filter_apply/kasdasj.csv")
    #                 object_data = object_data.merge(ref_obj_data, left_on=filter_item["ref_field"], right_on=filter_item["ref_field"], how="inner")
    #             else:
    #                 logger.error(f"Invalid filter type: {filter_item['type']}")
    #                 raise Exception(f"Invalid filter type: {filter_item['type']}")

    #         self.save_filtered_data(filtered_data=object_data, file_name=file_name)
    #         return "filtered_data successfully applied."
    #     except Exception as e:
    #         logger.error(f"Error in apply_filter: {e}")
    #         raise e

    # def save_filtered_data(self, filtered_data, file_name):
    #     try:
    #         filtered_data.to_csv(f'{file_name}_filtered.csv', index=False)
    #         return "filtered_data successfully saved."
    #     except Exception as e:
    #         logger.error(f"Error in save_filtered_data: {e}")
    #         raise e
    
    
    