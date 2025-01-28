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

    __tablename__ = "role"  # Nom de la table en base de données

    id_role: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )  # Identifiant unique du rôle
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # Nom technique du rôle (ex: "admin", "user")
    label: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # Libellé affiché du rôle (ex: "Administrateur", "Utilisateur")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )  # Date de création du rôle
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )  # Date de dernière modification du rôle
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="role"
    )  # Relation avec les utilisateurs ayant ce rôle

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        back_populates="role",  # Relation avec les permissions associées au rôle
    )


class Permission(Base):
    """Modèle représentant une permission dans le système.

    Une permission définit une action possible sur une ressource pour un rôle donné.
    """

    __tablename__ = "permission"  # Nom de la table en base de données

    id_permission: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )  # Identifiant unique de la permission
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Type d'action (get, post, put, delete, etc.)
    resource: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Ressource concernée par la permission (ex: "users", "roles")

    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.id_role", ondelete="CASCADE"), nullable=False
    )  # Clé étrangère vers le rôle associé
    role: Mapped[Role] = relationship(
        "Role", back_populates="permissions"
    )  # Relation avec le rôle parent


class User(Base):
    """Modèle représentant un utilisateur dans le système.

    Un utilisateur est associé à un rôle qui définit ses permissions.
    """

    __tablename__ = "user"  # Nom de la table en base de données

    id_user: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )  # Identifiant unique de l'utilisateur
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,  # Email de l'utilisateur servant d'identifiant
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # Mot de passe hashé de l'utilisateur
    prenom: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Prénom de l'utilisateur
    nom: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Nom de famille de l'utilisateur
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # Indique si le compte est actif ou non
    service: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Service de rattachement de l'utilisateur
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )  # Date de création du compte
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )  # Date de dernière modification du compte

    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.id_role"), nullable=False
    )  # Clé étrangère vers le rôle de l'utilisateur
    role: Mapped["Role"] = relationship(
        "Role", back_populates="users"
    )  # Relation avec le rôle associé
