from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey,Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date
from typing import Optional
import uuid
from src.db_session import engine
from src.object.models.object import ObjTable
from typing import List
Base = declarative_base()

class FilterapplyModel(BaseModel):
    order: int  # Sequential numbering
    type: str
    field: str
    object_id: uuid.UUID
    from_date: Optional[date]
    to_date: Optional[date] = datetime.now().date()  # Changed to datetime.now().date()
    from_range: Optional[int]
    to_range: Optional[int]
    ref_obj_id: Optional[uuid.UUID]
    ref_field: Optional[str]
    ref_type: Optional[str]
    values: Optional[List[str]]

class DataModel(Base):
    __tablename__ = 'filter_new'

    filter_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order = Column(Integer)
    type = Column(String)
    field = Column(String)
    object_id = Column(UUID(as_uuid=True),ForeignKey(ObjTable.object_id))
    from_date = Column(Date)  # Changed to Date
    to_date = Column(Date, default=datetime.now().date())  # Changed to datetime.now().date()
    from_range = Column(Integer)
    to_range = Column(Integer)
    ref_obj_id = Column(UUID(as_uuid=True),ForeignKey(ObjTable.object_id))
    ref_field = Column(String)
    ref_type = Column(String)
    values = Column(String) #comma separated values
    is_deleted = Column(Boolean,default=False)
    autofilter= Column(Boolean,default=False)
    created_by = Column(String)
    created_date = Column(Date, default=datetime.now().date())  # Changed to datetime.now().date()
    modified_by = Column(String)
    modified_date = Column(Date, default=datetime.now().date())  # Changed to datetime.now().date()

Base.metadata.create_all(bind=engine)
