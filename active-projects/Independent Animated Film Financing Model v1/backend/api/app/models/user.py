"""
User Database Model

Represents users of the Film Financing Navigator platform.
"""

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model for authentication and profile management.

    Attributes:
        id: UUID primary key
        email: Unique email address
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        organization: Company/studio name
        role: User role (user, admin)
        is_active: Account active status
        is_verified: Email verification status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        projects: Relationship to user's projects
    """

    __tablename__ = "users"

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Profile
    full_name: Mapped[str | None] = mapped_column(String(255))

    organization: Mapped[str | None] = mapped_column(String(255))

    # Permissions
    role: Mapped[str] = mapped_column(
        String(50),
        default="user",
        nullable=False
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Relationships
    # projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    # custom_policies = relationship("CustomPolicy", back_populates="user", cascade="all, delete-orphan")
    # jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(email='{self.email}', role='{self.role}')>"
