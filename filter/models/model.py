from pydantic import BaseModel,Field, ValidationError
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey,Date
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date
from typing import Optional,List,Union
import uuid
from src.db_session import Base
from src.object.models.object import ObjTable

from typing import List


class FilterModel(BaseModel):
    order: int  # Sequential numbering
    type: str
    field: str
    object_id: uuid.UUID
    from_date: Union[Optional[date],Optional[str]] = None
    to_date: Union[Optional[date],Optional[str]] = datetime.now().date() 
    from_range: Optional[int] = None
    to_range: Optional[int] = None
    ref_obj_id: Optional[uuid.UUID] = None
    ref_field: Optional[str] = None
    ref_type: Optional[str] = None
    values: Optional[List[str]] = None

class DataModel(Base):
    __tablename__ = 'filter_records'

    filter_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order = Column(Integer)
    type = Column(String)
    field = Column(String)
    object_id = Column(UUID(as_uuid=True),ForeignKey(ObjTable.object_id))
    from_date = Column(Date)  # Changed to Date
    to_date = Column(Date, default=datetime.now().date())  # Changed to datetime.now().date()
    from_range = Column(Integer)
    to_range = Column(Integer)
    ref_obj_id = Column(UUID(as_uuid=True))
    ref_field = Column(String)
    ref_type = Column(String)
    values = Column(String) #comma separated values
    is_deleted = Column(Boolean,default=False)
    autofilter= Column(Boolean,default=False)
    created_by = Column(String)
    created_date = Column(Date, default=datetime.now().date())  # Changed to datetime.now().date()
    modified_by = Column(String)
    modified_date = Column(Date, default=datetime.now().date())  # Changed to datetime.now().date()

