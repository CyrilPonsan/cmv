from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
    Boolean,
    func,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..utils.database import Base


class Role(Base):
    __tablename__ = "role"

    id_role: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="role")

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", back_populates="role"
    )


class Permission(Base):
    __tablename__ = "permission"

    id_permission: Mapped[int] = mapped_column(primary_key=True, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)

    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.id_role", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[Role] = relationship("Role", back_populates="permissions")


class User(Base):
    __tablename__ = "user"

    id_user: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    prenom: Mapped[str] = mapped_column(String(50), nullable=False)
    nom: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    service: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id_role"), nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="users")
