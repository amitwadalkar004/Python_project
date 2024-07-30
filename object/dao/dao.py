from sqlalchemy.orm import Session
from src.object.models.object import ObjTable
from models.auth_models_v2 import User
from src.system.models.model import SystemTable
from src.project.models.project import ProjTable
from fastapi import HTTPException
from src.db_session import SessionLocal
import uuid

# db = SessionLocal()

class ObjDAO:
    
    @staticmethod
        
    def check_obj(id,current_user,db):
        """
        Check if an object exists in the database for the given object ID and current user.

        Args:
            db (Session): Database session.
            id (uuid.UUID): Object ID.
            current_user (dict): Dictionary containing current user details, including tenant ID.

        Returns:
            Optional[ObjTable]: The object if found, else None.
        """
        # return db.query(ObjTable).filter(ObjTable.project_id == id).first()
        return db.query(ObjTable).filter(ObjTable.object_id == id, ObjTable.is_deleted==False,ObjTable.tenant_key==current_user['tenant_id']).first()
    

    @staticmethod  
    def check_sys(system_id,db):
        """
        Check if an object exists in the database for the given system ID.

        Args:
            db (Session): Database session.
            system_id (uuid.UUID): System ID.

        Returns:
            Optional[ObjTable]: The object if found, else None.
        """
        return db.query(ObjTable).filter(ObjTable.system == system_id).first()


    @staticmethod
    def create(obj_data: dict, current_user,db):
        """
        Create a new object in the database.

        Args:
            db (Session): Database session.
            obj_data (ObjectV2): Data for the new object.
            current_user (dict): Dictionary containing current user details.

        Returns:
            Optional[ObjTable]: The created object if successful, else None.
        """
        obj_data.object_id=uuid.uuid4()
        obj_data.owner=current_user['user_id']
        obj_data.tenant_key=current_user['tenant_id']
        obj_data.created_by=current_user['user_id']
        obj_data.modified_by=current_user['user_id']
        obj_data.is_deleted=False
        obj_data=obj_data.dict()
        db_obj=ObjTable(**obj_data)
        print(db_obj)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    


    @staticmethod    
    def get(id,db):
        """
        Retrieve an object from the database by its ID.

        Args:
            id (uuid.UUID): The ID of the object to retrieve.

        Returns:
            ObjTable: The retrieved object.

        Raises:
            HTTPException: If the object is marked as deleted or not found.
        """
        # result = db.query(ObjTable).filter(ObjTable.project_id == id, ObjTable.is_deleted==False).all()
        result = db.query(ObjTable).filter(ObjTable.object_id == id, ObjTable.is_deleted==False).first()
        print(result)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail="Record is deleted")
        


    @staticmethod    
    def get_system(system,current_user,db):
        """
        Retrieve all objects related to a specific system for the current user.

        Args:
            system (uuid.UUID): The system ID to filter objects by.
            current_user (dict): Dictionary containing current user details, including tenant ID.

        Returns:
            Optional[list]: A list of objects related to the specified system if found, else None.

        Raises:
            HTTPException: If the objects are marked as deleted or not found.
        """
        result = db.query(
            ObjTable.object_id,
            ObjTable.description,
            ObjTable.name,
            ObjTable.notes,
            ObjTable.criteria,
            ObjTable.records_count,
            ObjTable.migration_count,
            ObjTable.post_mig_strategy,
            User.username.label('username'),
            SystemTable.name.label('system_name'),
            ProjTable.name.label('project_name'),
            ObjTable.created_by,
            ObjTable.modified_by,
            ObjTable.created_date,
            ObjTable.modified_date
        ).join(SystemTable, SystemTable.id == ObjTable.system).join(User, ObjTable.owner == User.id).join(ProjTable, ObjTable.project == ProjTable.project_id).filter(ObjTable.system == system, ObjTable.is_deleted==False,ObjTable.tenant_key==current_user['tenant_id']).all()
        if result:
            return result
        else:
            # raise HTTPException(status_code=400, detail="Record is deleted")
            return None
        

    @staticmethod
    def get_project(project,current_user,db):
        """
        Retrieve all objects related to a specific project for the current user.

        Args:
            project (uuid.UUID): The project ID to filter objects by.
            current_user (dict): Dictionary containing current user details, including tenant ID.

        Returns:
            Optional[list]: A list of objects related to the specified project if found, else None.

        Raises:
            HTTPException: If the objects are marked as deleted or not found.
        """
        result = db.query(
            ObjTable.object_id,
            ObjTable.description,
            ObjTable.name,
            ObjTable.notes,
            ObjTable.criteria,
            ObjTable.records_count,
            ObjTable.migration_count,
            ObjTable.post_mig_strategy,
            ObjTable.field_count,
            User.username.label('username'),
            SystemTable.name.label('system_name'),
            ProjTable.project_name.label('project_name'),
            ObjTable.created_by,
            ObjTable.modified_by,
            ObjTable.created_date,
            ObjTable.modified_date
        ).join(SystemTable, SystemTable.id == ObjTable.system).join(User, ObjTable.owner == User.id).join(ProjTable, ObjTable.project == ProjTable.project_id).filter(ObjTable.project == project, ObjTable.is_deleted==False,ObjTable.tenant_key==current_user['tenant_id']).all()
        if result:
            return result
        else:
            # raise HTTPException(status_code=400, detail="Record is deleted")
            return None

    
    @staticmethod   
    def delete(id, check_obj,db):
        """
        Mark an object as deleted in the database by its ID.

        Args:
            id (uuid.UUID): The ID of the object to delete.
            check_obj (ObjTable): The object instance to mark as deleted.

        Returns:
            dict: A message indicating successful deletion.

        Raises:
            Exception: If an error occurs during the database operation.
        """
        try:
            check_obj.is_deleted = True
            db.commit()
            db.refresh(check_obj)
            return {"message":"Object With Given Id Deleted Successfully"}
        except Exception as e:
            db.rollback()
            raise e
        

    
    @staticmethod   
    def edit(check_obj, obj_data, current_user,db):
        """
        Edit an existing object in the database.

        Args:
            check_obj (ObjTable): The existing object to edit.
            obj_data (ObjectV2): The new data to update the object with.
            current_user (dict): Dictionary containing current user details.

        Returns:
            ObjTable: The updated object.

        Raises:
            HTTPException: If an error occurs during the database operation.
        """
        if obj_data.name:
            check_obj.name = obj_data.name
        if obj_data.system:
            check_obj.system = obj_data.system
        if obj_data.description:
            check_obj.description = obj_data.description
        if obj_data.notes:
            check_obj.notes = obj_data.notes
        if obj_data.criteria:
            check_obj.criteria = obj_data.criteria
        if obj_data.records_count:
            check_obj.records_count = obj_data.records_count
        if obj_data.migration_count:
            check_obj.migration_count = obj_data.migration_count
        if obj_data.post_mig_strategy:
            check_obj.post_mig_strategy = obj_data.post_mig_strategy
        check_obj.modified_by = current_user['user_id']
        db.commit()
        db.refresh(check_obj)
        return check_obj
    


    @staticmethod
    def get_all(current_user,db):
        """
        Retrieve all objects for the current user's tenant that are not marked as deleted.

        Args:
            current_user (dict): Dictionary containing current user details.

        Returns:
            List[ObjTable]: A list of all objects for the user's tenant that are not deleted.

        Raises:
            HTTPException: If an error occurs during the database operation.
        """
        return db.query(ObjTable).filter(ObjTable.tenant_key==current_user['tenant_id'],ObjTable.is_deleted==False).all()
    

    
    @staticmethod   
    def get_all_objects_for_system(system_id,db):
        """
        Retrieve all objects for a given system.

        Args:
            system_id (uuid.UUID): The ID of the system to retrieve objects for.

        Returns:
            List[ObjTable]: A list of all objects associated with the specified system.

        Raises:
            HTTPException: If an error occurs during the database operation.
        """
        try:
            return db.query(ObjTable).filter(ObjTable.system == system_id).all()
        except Exception as e:
            db.rollback()
            raise e