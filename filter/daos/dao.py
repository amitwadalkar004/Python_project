import logging
from src.filter.models.model import DataModel
# from src.db_session import SessionLocal
from sqlalchemy import update
from sqlalchemy.orm.exc import NoResultFound
from src.utils.logs import CustomLogger

logger_instance = CustomLogger(log_level='DEBUG', log_file_name='filter.log', log_path='logs')

class Dao:
    def __init__(self):
        self.logger = logger_instance.get_logger()
        # self.db = SessionLocal()

    def create_filter(self, filter_data_dict,db):
        try:
            self.logger.info("Creating a new filter")
            data = DataModel(**filter_data_dict)
            db.add(data)
            db.commit()
            db.refresh(data)
            return data
        except Exception as e:
            self.logger.error("Error creating a new filter %s", e)
            db.rollback()
            raise e

    def update_filter(self, filter_id, filter_data_dict,db):
        try:
            self.logger.info("Updating an existing filter")
            existing_filter = db.query(DataModel).filter(DataModel.filter_id == filter_id, DataModel.is_deleted == False).first()
            if existing_filter is None:
                raise NoResultFound(f"No filter found with object_id '{filter_id}'")
            
            data = DataModel(**filter_data_dict)
            stmt = update(DataModel).where(
                DataModel.filter_id == filter_id,
                DataModel.type == filter_data_dict['type'],
                DataModel.is_deleted == False
            ).values(**filter_data_dict)
            db.execute(stmt)
            db.commit()
            return data
        except Exception as e:
            self.logger.error("Error updating an existing filter %s", e)
            db.rollback()
            raise e

    def get_filter(self, object_id,db):
        try:
            self.logger.info("Getting a filter by its object id")
            filter_data = db.query(DataModel).filter(DataModel.object_id == object_id, DataModel.is_deleted == False).order_by(DataModel.order.asc()).all()
            if not filter_data:
                raise NoResultFound(f"No filter found with object_id '{object_id}'")
            return filter_data
        except Exception as e:
            self.logger.error("Error getting a filter by its object id %s", e)
            db.rollback()
            raise e
        
    def get_picklist_values(self, field,db):
        try:
            self.logger.info("Getting a picklist_values by its field")
            #picklist_values = self.db.query(DataModel.values).filter_by(field=field).all()
            picklist_values = db.query(DataModel.values).filter_by(field=field).filter(DataModel.is_deleted == False).order_by(DataModel.order.asc()).all()
            if not picklist_values:
                raise NoResultFound(f"No picklist_values found with field '{field}'")
            return picklist_values
        except Exception as e:
            self.logger.error("Error getting a picklist_values by its field %s", e)
            db.rollback()
            raise e
            

    def delete_filters(self, filter_ids,db):
        try:
            self.logger.info("Deleting filters by their ids")
            # Query for all filters that match the given IDs
            filters_to_delete = db.query(DataModel).filter(DataModel.filter_id.in_(filter_ids)).all()
            
            if not filters_to_delete:
                raise NoResultFound(f"No filters found with the given ids: {filter_ids}")

            # Perform the deletion
            stmt = update(DataModel).where(DataModel.filter_id.in_(filter_ids)).values(is_deleted=True)
            db.execute(stmt)
            db.commit()
        except Exception as e:
            self.logger.error("Error deleting filters by their ids: %s", e)
            db.rollback()
            raise e

    def get_auto_filter(self, object_id,db):
        try:
            self.logger.info("Getting auto filter")
            filter_data = self.db.query(DataModel.autofilter).filter(DataModel.object_id == object_id, DataModel.is_deleted == False, DataModel.autofilter == True).first()
            return filter_data
        except Exception as e:
            self.logger.error("Error getting auto filter %s", e)
            db.rollback()
            raise e    
    
    def update_auto_filter(self, object_id, flag,db):
        try:
            self.logger.info("Updating auto filter")
            stmt = update(DataModel).where(DataModel.object_id == object_id, DataModel.is_deleted == False).values(autofilter=flag)
            db.execute(stmt)
            db.commit()
        except Exception as e:
            self.logger.error("Error updating auto filter %s", e)
            db.rollback()
            raise e
