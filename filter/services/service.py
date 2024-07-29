import numpy as np
from ..daos import dao
from datetime import datetime
import requests
import configparser
import os
from src.filter.models import model
from src.utils.logs import CustomLogger


logger_instance = CustomLogger(log_level='DEBUG', log_file_name='filter.log', log_path='logs')
logger = logger_instance.get_logger()

# Folder path for the secure.ini file
folder_path = "D:/DataMatter_Tech/Backend_datamatter/secure.ini" 
absolute_path = os.path.abspath(folder_path)

# Read configurations from the secure.ini file
config = configparser.ConfigParser()
config.read(absolute_path)


# Class to handle the business logic for the filter
class Filter:
    def __init__(self):
        self.dao = dao.Dao()

    # Function to create a new filter
    def create_filter(self, filter_data,current_user,db):
        try:
            logger.info("Creating a new filter")
            filter_data_dict={}
            filter_data_dict['object_id']=filter_data.object_id
            filter_data_dict['type']=filter_data.type
            filter_data_dict['field']=filter_data.field
            filter_data_dict['order']=filter_data.order

            #check if type is date then only apply logic that will check from_date is less than to_date
            if filter_data_dict['type'] == 'date' :
                if filter_data.from_date < filter_data.to_date:
                    filter_data_dict['from_date']=filter_data.from_date
                    filter_data_dict['to_date']=filter_data.to_date
                else:
                    raise ValueError("from_date should be less than to_date")
            
            #check if type is range then only apply logic that will check from_range is less than to_range
            if  filter_data_dict['type'] == "range":
                if filter_data.from_range < filter_data.to_range:
                    filter_data_dict['from_range']=filter_data.from_range
                    filter_data_dict['to_range']=filter_data.to_range
                else:
                    raise ValueError("from_range should be less than to_range")
            
            if filter_data_dict['type'] == 'reference':
                    filter_data_dict['ref_obj_id']=filter_data.ref_obj_id
                    filter_data_dict['ref_field']=filter_data.ref_field
                    filter_data_dict['ref_type']=filter_data.ref_type
            
            
            if filter_data_dict['type'] == 'values':
                    if filter_data.values:
                         filter_data_dict['values'] = ','.join(filter_data.values)
                    else:
                        raise ValueError("values should not be empty")
            
            filter_data_dict['created_date'] = datetime.now()
            filter_data_dict['modified_date'] = datetime.now()
            # filter_data_dict['created_by'] = current_user
            # filter_data_dict['modified_by'] = current_user
            filter_data_dict['created_by'] = current_user['username']  # Extract username
            filter_data_dict['modified_by'] = current_user['username']  # Extract username
            filter_data = self.dao.create_filter(filter_data_dict,db)
            return filter_data 
        except Exception as e:
            logger.error("Error creating a new filter")
            raise e
    



    # Function to update an existing filter
    def update_filter(self, filter_id, filter_data,current_user,db):#object_id
        try:
            logger.info("Updating an existing filter")
            filter_data_dict={}
            filter_data_dict['object_id']=filter_data.object_id
            filter_data_dict['type']=filter_data.type
            filter_data_dict['field']=filter_data.field
            filter_data_dict['order']=filter_data.order

            #check if type is date then only apply logic that will check from_date is less than to_date
            if filter_data_dict['type'] == 'date' :
                if filter_data.from_date < filter_data.to_date:
                    filter_data_dict['from_date']=filter_data.from_date
                    filter_data_dict['to_date']=filter_data.to_date
                else:
                    raise ValueError("from_date should be less than to_date")
            
            #check if type is range then only apply logic that will check from_range is less than to_range
            if  filter_data_dict['type'] == "range":
                if filter_data.from_range < filter_data.to_range:
                    filter_data_dict['from_range']=filter_data.from_range
                    filter_data_dict['to_range']=filter_data.to_range
                else:
                    raise ValueError("from_range should be less than to_range")
            
            if filter_data_dict['type'] == 'reference':
                    filter_data_dict['ref_obj_id']=filter_data.ref_obj_id
                    filter_data_dict['ref_field']=filter_data.ref_field
                    filter_data_dict['ref_type']=filter_data.ref_type
            
            
            if filter_data_dict['type'] == 'values':
                    if filter_data.values:
                         filter_data_dict['values'] = ','.join(filter_data.values)
                    else:
                        raise ValueError("values should not be empty")
            filter_data_dict['modified_date'] = datetime.now()
            #filter_data_dict['modified_by'] = current_user
            filter_data_dict['modified_by'] = current_user['username']  # Extract username

            filter_data = self.dao.update_filter(filter_id,filter_data_dict,db)
            return filter_data
        except Exception as e:
            logger.error("Error updating an existing filter")
            raise e

    # Function to get a filter by its id
    def get_filter(self, object_id,db):
        try:
            logger.info("Getting a filter by its id")
            filter_data = self.dao.get_filter(object_id,db)
            return filter_data
        except Exception as e:
            logger.error("Error getting a filter by its id")
            raise e
        
    def get_picklist_values(self, field: str,db):
        try:
            picklist_values = self.dao.get_picklist_values(field,db)
            if not picklist_values:
                return []

            # Process the results to create a unique list of values
            values_list = set()
            for value in picklist_values:
                if value[0]:  # Check if value is not None
                    values_list.update(value[0].split(','))  # value is a tuple
            # Sort the list before returning
            return sorted(values_list, key=lambda x: int(x) if x.isdigit() else x)        
        except Exception as e:
            raise Exception(f"Error fetching picklist values: {e}")   

    # Function to delete a filter by its id
    def delete_filter(self, filter_ids,db):
        try:
            logger.info("Deleting a filter by its id")
            filter_data = self.dao.delete_filters(filter_ids,db)
            return filter_data
        except Exception as e:
            logger.error("Error deleting a filter by its id")
            raise e        

    def get_auto_filter(self,object_id):
        try:
            logger.info("Getting auto filter status for an object")
            autofilter = self.dao.get_auto_filter(object_id)
            return autofilter
        except Exception as e:
            logger.error("Error getting auto filter status for an object")
            raise e
    def update_auto_filter(self,object_id,flag):
        try:    
            autofilter= self.dao.update_auto_filter(object_id,flag)
            return autofilter
        except Exception as e:
            logger.error("Error updating an auto filter")
            raise e
        
    