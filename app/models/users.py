from app.core.database import Base
from app.utils import extentions
from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship
from app.core.config import AccountStatuses, TokenStatuses, Roles


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=extentions.gen_uuid)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    address = Column(String, nullable=True)
    role = Column(String, server_default=Roles.USER.value)
    dob = Column(DateTime, nullable=True)
    create_at = Column(DateTime, server_default=func.now())
    update_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    status = Column(String, server_default=AccountStatuses.ACTIVE.value)
    refresh_tokens = relationship(
        "UserRefreshTokens", back_populates="user", cascade="all, delete"
    )


class UserRefreshTokens(Base):
    __tablename__ = "user_refresh_tokens"

    id = Column(String, primary_key=True, index=True, default=extentions.gen_uuid)
    user_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    refresh_token = Column(String, nullable=False, index=True)
    status = Column(String, server_default=TokenStatuses.ACTIVE.value)

    user = relationship("User", back_populates="refresh_tokens")
