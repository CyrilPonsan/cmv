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
    """Modèle représentant un rôle utilisateur dans le système.

    Un rôle définit les permissions et accès d'un groupe d'utilisateurs.
    """

    __tablename__ = "role"

    id_role: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # Nom technique du rôle
    label: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # Libellé affiché du rôle
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="role"
    )  # Relation avec les utilisateurs

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        back_populates="role",  # Relation avec les permissions
    )


class Permission(Base):
    """Modèle représentant une permission dans le système.

    Une permission définit une action possible sur une ressource pour un rôle donné.
    """

    __tablename__ = "permission"

    id_permission: Mapped[int] = mapped_column(primary_key=True, index=True)
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Type d'action (get, post, etc.)
    resource: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Ressource concernée

    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.id_role", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[Role] = relationship(
        "Role", back_populates="permissions"
    )  # Relation avec le rôle


class User(Base):
    """Modèle représentant un utilisateur dans le système.

    Un utilisateur est associé à un rôle qui définit ses permissions.
    """

    __tablename__ = "user"

    id_user: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,  # Email de l'utilisateur
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # Mot de passe hashé
    prenom: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Prénom de l'utilisateur
    nom: Mapped[str] = mapped_column(String(50), nullable=False)  # Nom de l'utilisateur
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # Statut du compte
    service: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Service de rattachement
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
    role: Mapped["Role"] = relationship(
        "Role", back_populates="users"
    )  # Relation avec le rôle
