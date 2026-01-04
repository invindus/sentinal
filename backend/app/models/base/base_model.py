"""
Base model with common fields and functionality for all database models.
"""

from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
import uuid


class BaseModel:
    # Primary Key - UUID for all tables
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

