from app.core.database import Base
from app.utils import extentions
from sqlalchemy import Column, String, Integer


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=extentions.gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Integer, default=0)
    refresh_token = Column(String, nullable=True)
