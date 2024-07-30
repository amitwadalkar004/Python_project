from fastapi import APIRouter,HTTPException, Depends
from src.estimator_master.services.service import Estimator
from src.estimator_master.models.model import EstimatorModel
# from src.authentication.services.auth_services_v2 import get_current_user
from src.auth import get_current_user
from src.rbac.services.check_permission import check_permission
from src.db_session import get_db,SessionLocal
from sqlalchemy.orm import Session

# from logger_config import logging
service_obj=Estimator()
class EstimatorMaster:

    router=APIRouter()
    
    version="/v2"

    @router.post("/estimator")
    @check_permission("estimator_master.create")
    async def create_estimator(estimator: EstimatorModel,current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
        try:
            result=service_obj.create_estimator(estimator,current_user,db)
            return result  
        except Exception as e:
            # logging.error("Error Occurred: %s", e)
            raise HTTPException(status_code=500, detail=f"Error Occurred: {e}")

    @router.get("/estimator")
    @check_permission("estimator_master.read")
    async def read_estimators(current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
        try:
            result =service_obj.read_estimators(current_user,db)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Occurred: {e}")


    @router.put("/estimator")
    @check_permission("estimator_master.update")
    async def update_estimator(activity: str,estimator: EstimatorModel,current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
        try:
            result=await service_obj.update_estimator(activity,estimator,current_user,db)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Occurred: {e}")

    @router.delete("/estimator")
    @check_permission("estimator_master.delete")
    async def delete_estimator(activity: str,current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
        try:
            result= service_obj.delete_estimator(activity,db)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Occurred: {e}")

