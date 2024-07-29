from fastapi import File, UploadFile, HTTPException,APIRouter,Depends, Form
# from src.authentication.services.auth_services_v2 import get_current_user
from src.auth import get_current_user
from src.rbac.services.check_permission import check_permission
from src.file.services.file_services import FileManagement
from fastapi.responses import JSONResponse, FileResponse
from src.file.models.model import FileModel
from src.utils.logs import CustomLogger
from sqlalchemy.orm import Session
from src.db_session import get_db
from pathlib import Path
import uuid


logger_instance = CustomLogger(log_level='DEBUG', log_file_name='upload.log', log_path='logs')
logger = logger_instance.get_logger()


class FileAPI:
    version = "/V2"
    router = APIRouter()
    
        
    @router.post("/file/upload")
    @check_permission("file.create")
    async def upload_file_api(file: UploadFile = File(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db),
                              system: str = Form(...), object: str = Form(...), project: str = Form(...),
                              environment: str = Form(...), file_type: str = Form(...),
                              is_deleted: bool = Form(False)):
        try:
            result = FileManagement.file_upload(file, current_user,system, object, project, environment, file_type, is_deleted,db)
            logger.info(f"File uploaded successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        


    @router.get("/view/file/{id}")
    @check_permission("file.read")
    async def get_file_id_api(id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
        try:
            file = FileManagement.get(id, current_user, db)
            logger.info(f"File retrieved: {file}")
            return file
        except Exception as e:
            logger.error(f"Error retrieving file: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        

    
    @router.put("/edit/file/{id}")
    @check_permission("file.update")
    async def edit_file_api(upload: FileModel, id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):

        try:
            updated_file = FileManagement.edit(id, current_user, upload, db)
            logger.info(f"File updated: {updated_file}")
            return updated_file
        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        

    
    @router.delete("/delete/file/{id}")
    @check_permission("file.delete")
    async def delete_file_api(id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
        try:
            deleted_file = FileManagement.delete(id, current_user, db)
            logger.info(f"File deleted: {deleted_file}")
            return deleted_file
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        


    @router.get("/list-files")
    @check_permission("file.read")
    async def list_files(current_user: str = Depends(get_current_user)):
        try:
            files = [file.name for file in Path("src/object/data").iterdir() if file.is_file()]
            download_links = [
                {"file_name": file_name, "download_link": f"/download-file?file_name={file_name}"}
                for file_name in files
            ]
            logger.info("Files listed successfully")
            return JSONResponse(content={"files": download_links})
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        

    
    @router.get("/download-file")
    @check_permission("file.read")
    async def download_file(file_name: str, current_user: str = Depends(get_current_user)):
        try:
            file_path = Path("src/object/data") / file_name
            if not file_path.is_file():
                raise HTTPException(status_code=404, detail="File not found")
            logger.info(f"File downloaded: {file_name}")
            return FileResponse(file_path)
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        

    
    @router.get("/download/{file_id}")
    @check_permission("file.read")
    async def download_file_by_id(file_id: uuid.UUID, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
        try:
            file = FileManagement.download_file(file_id, current_user, db)
            logger.info(f"File downloaded by id: {file_id}")
            return file
        except Exception as e:
            logger.error(f"Error downloading file by id: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @router.get("/filtered_info/")
    async def get_filtered_info(object_id: uuid.UUID,db:Session=Depends(get_db)) :
        return FileManagement.get_filtered_info(object_id,db)
    
    @router.put("/update/filtered_info/")
    def update_filtered_info(object_id: uuid.UUID,db : Session = Depends(get_db)) :
        return FileManagement.update_filtered_info(object_id,db)
