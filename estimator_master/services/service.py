from fastapi import HTTPException
from src.estimator_master.daos import dao
import uuid
from src.utils.logs import CustomLogger

# Create an instance of CustomLogger with desired configuration
logger_instance = CustomLogger(log_level='DEBUG', log_file_name='estimator_master.log', log_path='logs')

# Get the logger from the instance
logger = logger_instance.get_logger()

class Estimator:
    def __init__(self):
        try:
            # configure_logging()
            self.db=dao.DatabaseOperations()
        except Exception as e:
            logger.error("Error Occured while connecting estimator:%s",e)
            
    def create_estimator(self,estimator,current_user,db):
        try:
            # Attempt to add a estimator 
            estimator.id = uuid.uuid4()
            estimator.tenant_key=current_user['tenant_id']
            estimator.created_by = current_user['user_id']
            estimator.modified_by = current_user['user_id']
            result=self.db.create_estimator(estimator,db)
            logger.info("estimator added successfully: %s",estimator)
            return result
        except Exception as e:
            # return str(e)
            # Log an error message if an exception occurs
            logger.error("Error Occured while adding estimator:%s",e)
            raise HTTPException(status_code=500, detail=f"Error Occurred: {e}")


    def read_estimators(self,current_user,db):
        try:
            # Attempt to read  estimators 
            result=self.db.read_estimators(current_user,db)
            logger.info("estimator retrived successfully: %s")
            return result
        except Exception as e:
            # Log an error message if an exception occurs
            logger.error("Error Occured while reading estimator:%s",e)
            return str(e)
    
    async def update_estimator(self,activity,estimator,current_user,db):
        try:
            # Attempt to update a estimator 
            estimator.modified_by = current_user
            result=self.db.update_estimator(activity, estimator,db)
            logger.info("estimator updated successfully: %s",estimator)
            return result
        except Exception as e:
            # Log an error message if an exception occurs
            logger.error("Error Occured while updating estimator:%s",e)
            return str(e)

    async def delete_estimator(self,activity,db):
        try:
            # Attempt to delete a estiator 
            result=self.db.delete_estimator(activity,db)
            logger.info("estimator deleted successfully: %s",activity)
            return result
        except Exception as e:
            # Log an error message if an exception occurs
            logger.error("Error Occured while deleting estimator:%s",e)        
            return str(e)