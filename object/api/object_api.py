from src.object.models.object import ObjectV2
from src.rbac.services.check_permission import check_permission
from src.db_session import SessionLocal,get_db
from sqlalchemy.orm import Session
from src.object.services.create_object import ObjManagement
from src.auth import get_current_user
import uuid
from fastapi import APIRouter, Depends, HTTPException
        
class ObjectAPIV2:
    
    version="/v2"
    
    router = APIRouter()
    
            
    @router.post("/object")
    # @check_permission("object.create")        
    def create_object(obj_data:ObjectV2, current_user: str = Depends(get_current_user),db:Session=Depends(get_db)):
        """
        API endpoint to create a new object.

        Args:
            obj_data (ObjectV2): Data for the new object.
            current_user (Dict[str, Any]): Current user details from dependency injection.
            db (Session): Database session from dependency injection.

        Returns:
            The created object.

        Raises:
            HTTPException: If any field in obj_data is None or an unexpected error occurs.
        """
        dic = obj_data.__dict__
        if None in dic.values():
            raise HTTPException(status_code=403,detail="Empty Value Error")
        else:
            return ObjManagement.create(obj_data,current_user)
        

    
    @router.get("/object/{id}")
    # @check_permission("object.get")
    def get_object(id:str, current_user: str = Depends(get_current_user),db:Session=Depends(get_db)):
        """
        API endpoint to retrieve an object by its ID.

        Args:
            id (str): The ID of the object to retrieve.
            current_user (dict): Current user details from dependency injection.

        Returns:
            The retrieved object.

        Raises:
            HTTPException: If the object is not found or an unexpected error occurs.
        """
        return ObjManagement.get(id,current_user,db)
    


    @router.get("/system/{system}/object")
    # @check_permission("object.get.system")
    def get_system(system:str,current_user: str = Depends(get_current_user),db:Session=Depends(get_db)):
        """
        API endpoint to retrieve objects related to a specific system for the current user.

        Args:
            system (str): The system ID to filter objects by.
            current_user (dict): Current user details from dependency injection.

        Returns:
            list: A list of objects related to the specified system.

        Raises:
            HTTPException: If the objects are not found or an unexpected error occurs.
        """
        return ObjManagement.get_system(system,current_user,db)



    @router.get("/project/{project}/objects")
    # @check_permission("object.get.system")
    def get_project(project:uuid.UUID,current_user: str = Depends(get_current_user),db:Session=Depends(get_db)):
        """
        API endpoint to retrieve objects related to a specific project for the current user.

        Args:
            project (uuid.UUID): The project ID to filter objects by.
            current_user (dict): Current user details from dependency injection.

        Returns:
            list: A list of objects related to the specified project.

        Raises:
            HTTPException: If the objects are not found or an unexpected error occurs.
        """
        return ObjManagement.get_project(project,current_user,db)

     
    
        
    @router.delete("/object/{id}")
    @check_permission("object.delete")
    def delete_object(id:str, current_user: str = Depends(get_current_user),db:Session=Depends(get_db)):
        """
        API endpoint to delete an object by its ID for the current user.

        Args:
            id (str): The ID of the object to delete.
            current_user (dict): Current user details from dependency injection.

        Returns:
            dict: A message indicating successful deletion.

        Raises:
            HTTPException: If the object is not found, ID is not in UUID format, or an unexpected error occurs.
        """
        return ObjManagement.delete(id,current_user,db)


    @router.put("/object/{id}")
    @check_permission("object.modify")
    def edit_object(id:str, obj_data:ObjectV2, current_user: str = Depends(get_current_user),db:Session=Depends(get_db)):
        """
        API endpoint to edit an object by its ID for the current user.

        Args:
            id (str): The ID of the object to edit.
            obj_data (ObjectV2): The new data to update the object with.
            current_user (dict): Current user details from dependency injection.

        Returns:
            ObjTable: The updated object.

        Raises:
            HTTPException: If the object is not found, ID is not in UUID format, or an unexpected error occurs.
        """
        return ObjManagement.edit(id, obj_data, current_user,db)

    
    @router.get("/object")
    # @check_permission("object.get_all")
    def get_all_object(current_user: str = Depends(get_current_user),db:Session=Depends(get_db)):
        """
        API endpoint to retrieve all objects for the current user's tenant that are not marked as deleted.

        Args:
            current_user (dict): Current user details from dependency injection.

        Returns:
            List[ObjTable]: A list of all objects for the user's tenant that are not deleted.

        Raises:
            HTTPException: If an error occurs during the retrieval process.
        """
        return ObjManagement.get_all(current_user,db)
    


    @router.get("/system/{system_id}/objects")
    # @check_permission("object.get_all")
    def get_all_objects_for_system(system_id:uuid.UUID,db:Session=Depends(get_db)):
        """
        API endpoint to retrieve all objects for a given system.

        Args:
            system_id (uuid.UUID): The ID of the system to retrieve objects for.

        Returns:
            List[ObjTable]: A list of all objects associated with the specified system.

        Raises:
            HTTPException: If an error occurs during the retrieval process.
        """
        return ObjManagement.get_all_objects_for_system(system_id,db)
