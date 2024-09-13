from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Integer,
    DateTime,
    Boolean,
    func,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..settings.database import Base


class Role(Base):
    __tablename__ = "role"

    id_role: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    label: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="role")

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", back_populates="role"
    )


class Permission(Base):
    __tablename__ = "permission"

    id_permission: Mapped[int] = mapped_column(primary_key=True, index=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    resource: Mapped[str] = mapped_column(String, nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id_role", ondelete="CASCADE"))
    role: Mapped[Role] = relationship("Role", back_populates="permissions")


class User(Base):
    __tablename__ = "user"

    id_user: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    service: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    role: Mapped["Role"] = relationship("Role", back_populates="users")
