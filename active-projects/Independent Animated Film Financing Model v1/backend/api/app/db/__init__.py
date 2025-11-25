"""
Database Package

Provides database models, session management, and repositories.
"""

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.session import (
    get_db,
    get_db_context,
    get_async_db,
    get_async_db_context,
    init_db,
    init_async_db,
    SessionLocal,
    sync_engine,
)
from app.db.models import (
    CapitalProgramModel,
    CapitalSourceModel,
    CapitalDeploymentModel,
    ProjectModel,
    DealBlockModel,
    ProgramTypeEnum,
    ProgramStatusEnum,
    AllocationStatusEnum,
    DealTypeEnum,
    DealStatusEnum,
)
from app.db.repositories import (
    BaseRepository,
    AsyncBaseRepository,
    ProjectRepository,
    CapitalProgramRepository,
    CapitalSourceRepository,
    CapitalDeploymentRepository,
    DealBlockRepository,
    get_project_repository,
    get_capital_program_repository,
    get_capital_source_repository,
    get_capital_deployment_repository,
    get_deal_block_repository,
)

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    # Session
    "get_db",
    "get_db_context",
    "get_async_db",
    "get_async_db_context",
    "init_db",
    "init_async_db",
    "SessionLocal",
    "sync_engine",
    # Models
    "CapitalProgramModel",
    "CapitalSourceModel",
    "CapitalDeploymentModel",
    "ProjectModel",
    "DealBlockModel",
    # Enums
    "ProgramTypeEnum",
    "ProgramStatusEnum",
    "AllocationStatusEnum",
    "DealTypeEnum",
    "DealStatusEnum",
    # Repositories
    "BaseRepository",
    "AsyncBaseRepository",
    "ProjectRepository",
    "CapitalProgramRepository",
    "CapitalSourceRepository",
    "CapitalDeploymentRepository",
    "DealBlockRepository",
    "get_project_repository",
    "get_capital_program_repository",
    "get_capital_source_repository",
    "get_capital_deployment_repository",
    "get_deal_block_repository",
]
