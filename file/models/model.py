from pydantic import BaseModel, Field
from fastapi import UploadFile, File
from typing import Optional
from datetime import datetime, timezone
import uuid
from sqlalchemy import  Column, Integer, String, Boolean, MetaData, DateTime, text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from src.db_session import engine
from sqlalchemy.dialects.postgresql import UUID
from src.system.models.model import SystemTable
from src.object.models.object import ObjTable
from src.project.models.project import ProjTable
from src.environment.models.model import EnvTable
from src.db_session import Base

# Base = declarative_base()

# Define the users model using SQLAlchemy ORM

class FileTable(Base):
    __tablename__ = "file"

    id = Column("id",UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    system = Column(UUID(as_uuid=True), ForeignKey(SystemTable.id))
    object = Column(UUID(as_uuid=True), ForeignKey(ObjTable.object_id))
    project = Column(UUID(as_uuid=True), ForeignKey(ProjTable.project_id))
    environment = Column(UUID(as_uuid=True), ForeignKey(EnvTable.id))
    filename = Column(String)
    size = Column(String)
    current = Column(Boolean, default=False)
    is_filtered = Column(Boolean, default=False)
    record_count = Column(String)
    fields_count = Column(String)
    file_type = Column(String)
    tenant_key = Column(String)
    created_by = Column(String)
    modified_by = Column(String)
    created_date = Column(DateTime(timezone=True), server_default=text("(now() at time zone 'utc')"))
    modified_date = Column(DateTime(timezone=True), server_default=text("(now() at time zone 'utc')"), onupdate=lambda: datetime.now(timezone.utc))
    is_deleted = Column(Boolean, default=False)

# Create the table
# Base.metadata.create_all(bind=engine)


class FileModel(BaseModel):
    system: Optional[uuid.UUID]
    object: Optional[uuid.UUID]
    project: Optional[uuid.UUID]
    environment: Optional[uuid.UUID]
    filename: Optional[str]
    size: Optional[str]
    file_type: Optional[str]
    tenant_key: Optional[str]
    created_date: Optional[datetime]
    modified_date: Optional[datetime]
    created_by: Optional[str]
    modified_by: Optional[str]
    is_deleted: Optional[bool] = False
