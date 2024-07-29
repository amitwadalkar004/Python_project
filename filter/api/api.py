from fastapi import APIRouter, HTTPException, Depends
import uuid
from typing import List
from sqlalchemy.orm import Session
from src.filter.services.service import Filter
from src.filter.models.model import FilterModel
# from src.authentication.services.auth_services_v2 import get_current_user
from src.auth import get_current_user
from src.rbac.services.check_permission import check_permission
from src.utils.logs import CustomLogger
from src.db_session import get_db

logger_instance = CustomLogger(log_level='DEBUG', log_file_name='filter.log', log_path='logs')
logger = logger_instance.get_logger()
filter_service = Filter()
class FilterApi:
    
    version="/v2"

    router = APIRouter()
    @router.post("/filter")
    async def create_filter(filter_data: FilterModel, current_user: str = Depends(get_current_user),db : Session = Depends(get_db)):
            """
            Create a new filter.

            Args:
                filter_data (FilterModel): The data for the new filter.
                current_user (dict, optional): The current user. Defaults to Depends(get_current_user).

            Returns:
                filter_data (FilterModel): The created filter.

            Raises:
                HTTPException: If there is an error creating the filter.
            """

            try:
                filter_data = filter_service.create_filter(filter_data, current_user,db)
                return filter_data
            except Exception as e:
                logger.error("Error creating a new filter %s", e)
                raise HTTPException(status_code=500, detail=str(e))
    @router.put("/filter/{filter_id}")
    async def update_filter(filter_id: uuid.UUID,filter_data: FilterModel, current_user: str = Depends(get_current_user),db : Session = Depends(get_db)):
            """
            Update an existing filter.

            Args:
                filter_id (uuid.UUID): The ID of the filter to be updated.
                filter_data (FilterModel): The updated filter data.
                current_user (dict, optional): The current user. Defaults to Depends(get_current_user).

            Returns:
                FilterModel: The updated filter data.

            Raises:
                HTTPException: If there is an error updating the filter.
            """
            try:
                filter_data = filter_service.update_filter(filter_id, filter_data,current_user,db)
                return filter_data
            except Exception as e:
                logger.error("Error updating an existing filter %s", e)
                raise HTTPException(status_code=500, detail=str(e))
            
    @router.get("/filter/{object_id}")
    async def get_filter(object_id: uuid.UUID,current_user: str = Depends(get_current_user),db : Session = Depends(get_db) ):
            """
            Retrieve a filter by its ID.

            Args:
                filter_id (uuid.UUID): The ID of the filter to retrieve.
                current_user (dict, optional): The current user. Defaults to Depends(get_current_user).

            Returns:
                dict: The filter data.

            Raises:
                HTTPException: If there is an error retrieving the filter.
            """
            try:
                filter_data = filter_service.get_filter(object_id,db)
                return filter_data
            except Exception as e:
                logger.error("Error getting a filter by its id %s",e)
                raise HTTPException(status_code=500, detail=str(e))
            

    @router.get("/picklist_values/{field}")
    def get_picklist_values(field: str,current_user: str = Depends(get_current_user),db : Session = Depends(get_db) ):
            try:
                    picklist_values = filter_service.get_picklist_values(field,db)
                    return picklist_values
            except Exception as e:
                logger.error("Error getting a picklist_values by field %s",e)
                raise HTTPException(status_code=500, detail=str(e))
            
                 
    @router.delete("/filters")
    def delete_filters(filter_ids: List[uuid.UUID], current_user: str = Depends(get_current_user),db : Session = Depends(get_db)):
        """
        Delete multiple filters by their IDs.

        Args:
            filter_id (uuid.UUID): The ID of the filter to be deleted.
            current_user (dict, optional): The current user. Defaults to Depends(get_current_user).
            filter_ids (List[uuid.UUID]): The IDs of the filters to be deleted.
            current_user (dict, optional): The current user. Defaults to Depends(gets_current_user_2).

        Returns:
            List[uuid.UUID]: The IDs of the deleted filter.

        Raises:
            HTTPException: If there is an error deleting any filter.
        """
        try:
            #filter_service.delete_filter(filter_ids)
            filter_service.delete_filter(filter_ids,db)
            return filter_ids
        except Exception as e:
            #raise HTTPException(detail=str(e))
            raise HTTPException(status_code=500, detail=str(e))
            
    @router.get("/filter/autofilter/{object_id}")
    def get_auto_filter(object_id: uuid.UUID,current_user: str = Depends(get_current_user),db : Session = Depends(get_db)):
        """
        Retrieve the auto filter status for an object.

        Args:
            object_id (uuid.UUID): The ID of the object to retrieve the auto filter status for.

        Returns:
            bool: The auto filter status.

        Raises:
            HTTPException: If there is an error retrieving the auto filter status.
        """
        try:
            autofilter = filter_service.get_filter(object_id,db)
            return autofilter
        except Exception as e:
            logger.error("Error getting auto filter %s", e)
            raise HTTPException(status_code=500, detail=str(e))
        
    @router.put("/filter/autofilter/{object_id}/{flag}")
    def update_auto_filter(object_id: uuid.UUID, flag: bool,current_user: str = Depends(get_current_user),db : Session = Depends(get_db)):
        """
        Apply an auto filter to an object.

        Args:
            object_id (uuid.UUID): The ID of the object to apply the filter to.
            current_user (dict, optional): The current user. Defaults to Depends(get_current_user).

        Returns:
            str: A message indicating that the filter was applied successfully.

        Raises:
            HTTPException: If there is an error applying the filter.
        """
        try:
            result=filter_service.update_auto_filter(object_id,flag,db)
            return result
        except Exception as e:
            logger.error("Error applying filter %s", e)
            raise HTTPException(status_code=500, detail=str(e))
        


    