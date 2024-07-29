from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
import uuid

from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.filter_apply.services.service import Filter
from src.filter_apply.models.model import FilterapplyModel
from src.auth import get_current_user, get_current_access_token
from src.rbac.services.check_permission import check_permission
from src.utils.logs import CustomLogger
from src.db_session import get_db


logger_instance = CustomLogger(log_level='DEBUG', log_file_name='filter.log', log_path='logs')
logger = logger_instance.get_logger()
filter_service = Filter()

class FilterApplyAPI:
    
    version="/v2"

    router = APIRouter()

    @router.post("/filter_apply")
    #@check_permission("filter_apply.post")
    def filter_apply(object_id: uuid.UUID, current_user: str = Depends(get_current_user),current_token: str = Depends(get_current_access_token),db : Session = Depends(get_db)):
        """
        Apply filters to the data associated with the given object ID.

        This method retrieves filter criteria from an API, applies these filters 
        to the data in a corresponding CSV file, and updates the server about the 
        applied filter.

        Args:
            object_id (str): The unique identifier of the object to which filters will be applied.

        Returns:
            str: A message indicating whether the filter was successfully applied or was already applied.

        Raises:
            Exception: If there is an error during the filter application process.
        """
        try:    
            filter_id = filter_service.filter_apply(object_id,current_token,db)
            return  filter_id
        except Exception as e:
            logger.error(f"Error in filter_apply: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        



    
    @router.get("/filter_fields/{object_id}")
    #@check_permission("filter_apply.get")
    def get_filter_fields(object_id: uuid.UUID, current_user: str = Depends(get_current_user)):
        
        """
        Retrieve and categorize fields for the given object ID.

        Args:
            object_id (UUID): The object's unique identifier.

        Returns:
            dict: Categorized field names:
                - date_fields (List[str]): Date fields.
                - numeric_fields (List[str]): Numeric fields.
                - picklist_fields (List[str]): Picklist fields.
                - other_fields (List[str]): Other fields.

        Raises:
            HTTPException: If an error occurs during retrieval or categorization.
        """
        
        try:
            filter_fields = filter_service.get_filter_fields(object_id)
            return  filter_fields
        except Exception as e:
            logger.error(f"Error in get_filter_fields: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        





        
        
    '''    
    @router.get("/display-file")
    async def display_file(file_name: str, current_user: str = Depends(get_current_user)):
        try:
            file_path = Path("src/object/data") / file_name
            if not file_path.is_file():
                raise HTTPException(status_code=404, detail="File not found")
            logger.info(f"File displayed: {file_name}")
            return FileResponse(file_path)
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    '''        