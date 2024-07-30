import json
import logging
from src.estimator_master.models.model import DataModel
from src.db_session import SessionLocal
from sqlalchemy import update
import uuid

class DatabaseOperations:
    # def __init__(self):
    #     self.session=SessionLocal()

    def create_estimator(self,estimator,db):
        try:
            existing_estimator = db.query(DataModel).filter(DataModel.name==estimator.name).first() 
            if existing_estimator is None:
                db.add(DataModel(**(estimator.dict())))
                db.commit()
                logging.info('Added successfully.')
                return "Successfully Added"
            else:
                return "Estimator already Exist" 
        except Exception as e:
            db.rollback()
            # Log an error message if adding estimator fails
            logging.error("Error Occurred while adding estimator: %s", e)
            return str(e)

    def read_estimators(self,current_user,db):
        try:
            estimators = db.query(DataModel).filter(DataModel.tenant_key==current_user['tenant_id'],DataModel.is_deleted==False).all()
            #estimators = self.session.query(DataModel).filter(DataModel.is_deleted==False).all()
            return estimators
        except Exception as e:
            # Log an error message if reading estimator fails
            logging.error("Error Occurred while reading estimator: %s", e)
            return str(e)

    def update_estimator(self,activity,estimator,db):
        try:
            existing_estimator = db.query(DataModel).filter(DataModel.activity==activity).first() 
            if existing_estimator is not None:
                update_values = estimator.dict(exclude={"activity"})
                if 'modified_by' in update_values:
                    update_values['modified_by'] = json.dumps(update_values['modified_by'])
                update_query = update(DataModel).where(DataModel.activity == activity).values(**update_values)
                db.execute(update_query)
                db.commit()
                logging.info('Updated successfully.')
                return "Successfully Updated"
            else:
                return "Estimator doesn't Exist" 
        except Exception as e:
            db.rollback()
            # Log an error message if Updating estimator fails
            logging.error("Error Occurred while Updating estimator: %s", e)
            return str(e)

    def delete_estimator(self,activity,db):
        try:
            existing_estimator = db.query(DataModel).filter(DataModel.activity==activity).first() 
            if existing_estimator is not None:
                delete_query = update(DataModel).where(DataModel.activity == activity).values(is_deleted=True)
                db.execute(delete_query)
                db.commit()
                logging.info('Deleted successfully.')
                return "Successfully Deleted"
            else:
                return "Estimator doesn't Exist" 
        except Exception as e:
            db.rollback()
            # Log an error message if deleting estimator fails
            logging.error("Error Occurred while deleting estimator: %s", e)
            return str(e)