import configparser
import shutil
from pathlib import Path
from src.file.dao.file_dao import FileDAO
from src.file.models.model import FileModel
from src.uuid_check import UUID
from fastapi import HTTPException
import polars as pl
from fastapi.responses import FileResponse
from src.utils.logs import CustomLogger
from src.file.models.model import FileModel
import pandas as pd

logger_instance = CustomLogger(log_level='DEBUG', log_file_name='upload.log', log_path='logs')
logger = logger_instance.get_logger()
config = configparser.ConfigParser()
config.read("secure.ini")
base_url = config['GENERAL']['base_url']


class FileManagement:
        
    @staticmethod
    #def file_upload(file, current_user, system: str, object: str, project: str, environment: str, file_type: str, is_deleted: bool, db):
    def file_upload(file, current_user, system, object, project, environment, file_type, is_deleted: bool, db):

        try:
            if not file.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail="Only .csv files are allowed for upload.")

            upload_folder = Path("src/object/data")
            upload_folder.mkdir(parents=True, exist_ok=True)
            file_path = upload_folder / file.filename

            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            df = pd.read_csv(file_path)
            records_count = len(df)
            fields_count = len(df.columns)

            field_dict = {
                "size": file.size,
                "filename": file.filename,
                "system": system,
                "project": project,
                "environment": environment,
                "record_count": records_count,
                "fields_count": fields_count,
                "file_type": file_type,
                "tenant_key": current_user['tenant_id'],
                "is_deleted": is_deleted,
                "object": object
            }

            logger.info("Successfully uploaded file and file records created.")
            return FileDAO.file_upload(field_dict, current_user, db)

        except FileNotFoundError:
            error_msg = "File not found."
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

        except pd.errors.ParserError:
            error_msg = "Error parsing CSV file."
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

        except Exception as e:
            error_msg = str(e)
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        
        
    @staticmethod
    def upload_succ(file, current_user):
        upload_folder = Path("object")
        upload_folder.mkdir(parents=True, exist_ok=True)
        file_path = upload_folder / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return "Success"

    
        
    @staticmethod
    def get(id: str, current_user, db):
        try:
            check_uuid = UUID.is_valid_uuid(id)  # Validate UUID format
            if check_uuid==True:            
                #uuid_obj = UUID(id)  # Validate UUID format
                check_acc = FileDAO.check_file(id, current_user, db)
                if check_acc:
                    result = FileDAO.get(id, current_user, db)
                    logger.info(f"File found: {result}")
                    return result
                else:
                    logger.error(f"{id} Not Found")
                    raise HTTPException(status_code=400, detail="ID Not Found")
        except ValueError:
            logger.error("Please provide a valid UUID format")
            raise HTTPException(status_code=400, detail="Please provide a valid UUID format")
        except Exception as e:
            logger.error(str(e))
            raise HTTPException(status_code=400, detail=str(e))
    


    @staticmethod
    def edit(id, current_user, upload: FileModel, db):
        try:
            check_uuid = UUID.is_valid_uuid(id)  # Validate UUID format
            if check_uuid==True:
            #uuid_obj = UUID(id)  # Validate UUID format
                check_acc = FileDAO.check_file(id, current_user, db)
                if check_acc:
                    result = FileDAO.edit(
                        id,
                        current_user,
                        upload.system,
                        upload.object,  
                        upload.project,
                        upload.environment,
                        upload.is_deleted,
                        db
                    )
                    logger.info(f"File updated: {result}")
                    return result
            else:
                logger.error(f"{id} Not Found")
                raise HTTPException(status_code=400, detail="ID Not Found")
        except ValueError:
            logger.error("Please provide a valid UUID format")
            raise HTTPException(status_code=400, detail="Please provide a valid UUID format")
        except Exception as e:
            logger.error(str(e))
            raise HTTPException(status_code=400, detail=str(e))
        

        
    @staticmethod
    def delete(id: str, current_user: dict, db):
        try:
            check_uuid = UUID.is_valid_uuid(id)
            if check_uuid==True:
                #uuid_obj = UUID(id)  # Validate UUID format
                check_acc = FileDAO.check_file(id, current_user, db)
                if check_acc:
                    result = FileDAO.delete(check_acc, id, current_user, db)
                    logger.info(f"File deleted: {result}")
                    return result
                else:
                    logger.error(f"{id} Not Found")
                    raise HTTPException(status_code=400, detail="ID Not Found")
        except ValueError:
            logger.error("Please provide a valid UUID format")
            raise HTTPException(status_code=400, detail="Please provide a valid UUID format")
        except Exception as e:
            logger.error(str(e))
            raise HTTPException(status_code=400, detail=str(e))
        
        

    @staticmethod
    def download_file(file_id, current_user,db):
        try:

            get_filename_dic = FileDAO.get_file_name(file_id, current_user,db)
            file_name = get_filename_dic['filename']
            file_path = Path(f"src/object/data") / file_name
            if not file_path.is_file():
                logger.error(f"{file_id} not available")
                raise HTTPException(status_code=404, detail="File not found")
            # print(file_name['filename'][0])
            logger.info(f"Succesfully download file {file_id}")
            return FileResponse(file_path, media_type="application/octet-stream", headers={"Content-Disposition": f'attachment; filename="{file_name}"'})
        except Exception as e:
            logger.error(f"{str(e)}")
            raise HTTPException(status_code=400,detail=str(e))

        # return file_name

    # @staticmethod
    # def file_handle(file_dict):
    #     fileid = FileDAO.get_file_id(file_dict)
    #     main_table = csv.read_csv(f"src/object/data/{file_dict['filename']}")
    #     if file_dict['file_type']   == 'main':
    #         # main_table = csv.read_csv(f"src/object/data/{file_dict['filename']}")
    #         # print(main_table)
    #         has_dmtid_main = 'dmtid' in main_table.column_names
    #         has_dmt_status_main = 'dmt_status' in main_table.column_names
    #         if not has_dmtid_main:
    #             main_table = create_dmt_id(main_table,'dmtid',f"{fileid}-")
    #             print(main_table)
    #         with pa.ipc.new_file(f"src/object/data/{file_dict['filename']}.ipc.arrow", main_table.schema) as writer:
    #             writer.write_table(main_table)

            # if not has_dmt_status_main:
            #     main_table = create_dmt_status(main_table,'dmt_status','new')
            # csv.write_csv(main_table, f"src/object/data/{file_dict['filename']}")




        # filei = FileDAO.get_file_id(file_dict)
        # print(filei)

    def get_filtered_info(object_id,db):
        return FileDAO.get_filtered_info(object_id,db)
    
    def update_filtered_info(object_id,db):
        return FileDAO.update_filtered_info(object_id,db)