from sqlalchemy.orm import Session
from src.file.models.model import FileTable
from sqlalchemy import update
from src.utils.logs import CustomLogger

logger_instance = CustomLogger(log_level='DEBUG', log_file_name='filedao.log', log_path='logs')
logger = logger_instance.get_logger()
class FileDAO:
    
    @staticmethod
    def check_file(id, current_user,db):
        return db.query(FileTable).filter(FileTable.id == id, FileTable.tenant_key==current_user['tenant_id']).first()

    @staticmethod
    def file_upload(field_dict, current_user,db):
        if field_dict['file_type'] == 'main' or field_dict['file_type'] == 'part' or field_dict['file_type'] == 'correction':
            if field_dict['file_type'] == 'main':
                db.query(FileTable).filter(FileTable.current == True, FileTable.tenant_key==current_user['tenant_id'], FileTable.environment == field_dict['environment']).update({FileTable.current: False})
            field_dict['current'] = True
            logger.info(field_dict)
            create_file_record = FileTable(**field_dict)
            logger.info(create_file_record)

            db.add(create_file_record)
            db.commit()
            db.refresh(create_file_record)
            return create_file_record
    
    
       
    @staticmethod
    def get(id: str, current_user: str, db):
        result = db.query(FileTable).filter(FileTable.id == id, FileTable.tenant_key == current_user['tenant_id'], FileTable.is_deleted == False).first()
        if result:
            return result
        else:
            return {"message": "File Record Deleted"}
    
   
    
    @staticmethod
    def edit(id, current_user, system, object, project, environment, is_deleted,db):
        update_values = {}
        if system is not None:
            update_values['system'] = system
        if object is not None:
            update_values['object'] = object
        if project is not None:
            update_values['project'] = project
        if environment is not None:
            update_values['environment'] = environment
        
                                        
        update_query = (
            update(FileTable)
            .where(FileTable.id == id, FileTable.tenant_key == current_user['tenant_id'])
            .values(update_values)
        )
        db.execute(update_query)
        db.commit()
        
        # Fetch the updated file data after the update operation
        updated_file = db.query(FileTable).filter(FileTable.id == id).first() 
        logger.info(updated_file)       
        return updated_file  
    

    @staticmethod
    def delete(check_acc: FileTable, id: str, current_user: str, db):
        check_acc.is_deleted = True
        check_acc.modified_by = current_user['user_id']
        db.commit()
        db.refresh(check_acc)
        return {"message": "File Record With Given Id Deleted Successfully"}
    
    
    @staticmethod
    def get_file_name(file_id: str, current_user: str, db):
        return db.query(FileTable.filename).filter(FileTable.id == file_id, FileTable.tenant_key == current_user['tenant_id']).first()
    
    @staticmethod
    def get_filtered_info(object_id,db):
        try:
            object_id = str(object_id)
            is_filtered = db.query(FileTable.is_filtered).filter(FileTable.object == object_id, FileTable.is_filtered == True, FileTable.file_type == "main", FileTable.current == True).first()
            return is_filtered.is_filtered if is_filtered else False
        except Exception as e:
            db.rollback()
            raise e
        
    @staticmethod
    def update_filtered_info(object_id,db):
        try:
            object_id = str(object_id)
            update = db.query(FileTable).filter(FileTable.object == object_id, FileTable.file_type == "main", FileTable.current == True).update({FileTable.is_filtered: True})
            db.commit()
            return update
        except Exception as e:
            db.rollback()
            raise e
