from pydantic import BaseModel
from sqlalchemy import Column,Integer,String,Boolean,DateTime,text
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
import uuid
from src.db_session import Base
from datetime import datetime, timezone


# Base=declarative_base()
class EstimatorModel(BaseModel):
    id: uuid.UUID
    name:str
    activity:str
    phase:str
    dev_recc_effort:int
    range_min:int
    range_max:int
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    tenant_key: Optional[uuid.UUID] = None
    


class DataModel(Base):
    __tablename__= 'estimator_master_n'
    
    id = Column("id",UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    name=Column(String(20))
    activity=Column(String(20))
    tenant_key = Column(UUID(as_uuid=True))
    phase=Column(String(20))
    dev_recc_effort=Column(Integer)
    range_min=Column(Integer)
    range_max=Column(Integer)
    is_deleted=Column(Boolean,default=False)
    created_by = Column(String)
    modified_by = Column(String)
    created_date = Column(DateTime(timezone=True), server_default=text("(now() at time zone 'utc')"))
    modified_date = Column(DateTime(timezone=True), server_default=text("(now() at time zone 'utc')"), onupdate=lambda: datetime.now(timezone.utc))

    
# Base.metadata.create_all(bind=engine)
