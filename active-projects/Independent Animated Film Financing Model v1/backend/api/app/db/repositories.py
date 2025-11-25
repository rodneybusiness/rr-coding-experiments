"""
Database Repositories

Repository pattern implementation for database operations.
Provides clean abstraction over SQLAlchemy operations.
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from datetime import datetime
import uuid

from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.db.models import (
    CapitalProgramModel,
    CapitalSourceModel,
    CapitalDeploymentModel,
    ProjectModel,
    DealBlockModel,
    ProgramStatusEnum,
    AllocationStatusEnum,
)


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Base repository with common CRUD operations.

    Usage:
        class ProjectRepository(BaseRepository[ProjectModel]):
            pass

        repo = ProjectRepository(ProjectModel, db_session)
        project = repo.get_by_id(project_id)
    """

    def __init__(self, model: Type[ModelT], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, entity_id: uuid.UUID) -> Optional[ModelT]:
        """Get entity by UUID primary key."""
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelT]:
        """Get all entities with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> ModelT:
        """Create a new entity."""
        entity = self.model(**kwargs)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity_id: uuid.UUID, **kwargs) -> Optional[ModelT]:
        """Update an entity by ID."""
        entity = self.get_by_id(entity_id)
        if entity:
            for key, value in kwargs.items():
                if hasattr(entity, key) and value is not None:
                    setattr(entity, key, value)
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(entity)
        return entity

    def delete(self, entity_id: uuid.UUID) -> bool:
        """Delete an entity by ID."""
        entity = self.get_by_id(entity_id)
        if entity:
            self.db.delete(entity)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        """Count all entities."""
        return self.db.query(func.count(self.model.id)).scalar()

    def exists(self, entity_id: uuid.UUID) -> bool:
        """Check if entity exists."""
        return self.db.query(
            self.db.query(self.model).filter(self.model.id == entity_id).exists()
        ).scalar()


class AsyncBaseRepository(Generic[ModelT]):
    """
    Async base repository with common CRUD operations.
    """

    def __init__(self, model: Type[ModelT], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, entity_id: uuid.UUID) -> Optional[ModelT]:
        """Get entity by UUID primary key."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelT]:
        """Get all entities with pagination."""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelT:
        """Create a new entity."""
        entity = self.model(**kwargs)
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity_id: uuid.UUID, **kwargs) -> Optional[ModelT]:
        """Update an entity by ID."""
        entity = await self.get_by_id(entity_id)
        if entity:
            for key, value in kwargs.items():
                if hasattr(entity, key) and value is not None:
                    setattr(entity, key, value)
            entity.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(entity)
        return entity

    async def delete(self, entity_id: uuid.UUID) -> bool:
        """Delete an entity by ID."""
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.db.delete(entity)
            await self.db.commit()
            return True
        return False

    async def count(self) -> int:
        """Count all entities."""
        result = await self.db.execute(select(func.count(self.model.id)))
        return result.scalar()


# === Specialized Repositories ===

class ProjectRepository(BaseRepository[ProjectModel]):
    """Repository for Project operations."""

    def get_by_project_id(self, project_id: str) -> Optional[ProjectModel]:
        """Get project by business ID (not UUID)."""
        return self.db.query(self.model).filter(
            self.model.project_id == project_id
        ).first()

    def get_by_genre(self, genre: str) -> List[ProjectModel]:
        """Get all projects by genre."""
        return self.db.query(self.model).filter(
            self.model.genre == genre
        ).all()

    def get_by_jurisdiction(self, jurisdiction: str) -> List[ProjectModel]:
        """Get all projects by jurisdiction."""
        return self.db.query(self.model).filter(
            self.model.jurisdiction == jurisdiction
        ).all()

    def get_in_development(self) -> List[ProjectModel]:
        """Get all projects in development."""
        return self.db.query(self.model).filter(
            self.model.is_development == True
        ).all()

    def get_with_funding_gap(self) -> List[ProjectModel]:
        """Get all projects with funding gap."""
        return self.db.query(self.model).filter(
            self.model.funding_gap > 0
        ).all()

    def get_total_budget(self) -> float:
        """Get total budget across all projects."""
        result = self.db.query(func.sum(self.model.project_budget)).scalar()
        return float(result) if result else 0.0


class CapitalProgramRepository(BaseRepository[CapitalProgramModel]):
    """Repository for Capital Program operations."""

    def get_by_program_id(self, program_id: str) -> Optional[CapitalProgramModel]:
        """Get program by business ID."""
        return self.db.query(self.model).filter(
            self.model.program_id == program_id
        ).first()

    def get_by_status(self, status: ProgramStatusEnum) -> List[CapitalProgramModel]:
        """Get programs by status."""
        return self.db.query(self.model).filter(
            self.model.status == status
        ).all()

    def get_active_programs(self) -> List[CapitalProgramModel]:
        """Get all active programs."""
        return self.get_by_status(ProgramStatusEnum.ACTIVE)

    def get_by_program_type(self, program_type: str) -> List[CapitalProgramModel]:
        """Get programs by type."""
        return self.db.query(self.model).filter(
            self.model.program_type == program_type
        ).all()

    def get_total_committed(self) -> float:
        """Get total committed capital across all programs."""
        result = self.db.query(func.sum(self.model.total_committed)).scalar()
        return float(result) if result else 0.0


class CapitalSourceRepository(BaseRepository[CapitalSourceModel]):
    """Repository for Capital Source operations."""

    def get_by_source_id(self, source_id: str) -> Optional[CapitalSourceModel]:
        """Get source by business ID."""
        return self.db.query(self.model).filter(
            self.model.source_id == source_id
        ).first()

    def get_by_program(self, program_id: uuid.UUID) -> List[CapitalSourceModel]:
        """Get all sources for a program."""
        return self.db.query(self.model).filter(
            self.model.program_id == program_id
        ).all()

    def get_available_sources(self, min_amount: float = 0) -> List[CapitalSourceModel]:
        """Get sources with available capital above threshold."""
        return self.db.query(self.model).filter(
            (self.model.committed_amount - self.model.drawn_amount) > min_amount
        ).all()


class CapitalDeploymentRepository(BaseRepository[CapitalDeploymentModel]):
    """Repository for Capital Deployment operations."""

    def get_by_deployment_id(self, deployment_id: str) -> Optional[CapitalDeploymentModel]:
        """Get deployment by business ID."""
        return self.db.query(self.model).filter(
            self.model.deployment_id == deployment_id
        ).first()

    def get_by_project(self, project_id: str) -> List[CapitalDeploymentModel]:
        """Get all deployments for a project."""
        return self.db.query(self.model).filter(
            self.model.project_id == project_id
        ).all()

    def get_by_program(self, program_id: uuid.UUID) -> List[CapitalDeploymentModel]:
        """Get all deployments for a program."""
        return self.db.query(self.model).filter(
            self.model.program_id == program_id
        ).all()

    def get_by_status(self, status: AllocationStatusEnum) -> List[CapitalDeploymentModel]:
        """Get deployments by status."""
        return self.db.query(self.model).filter(
            self.model.status == status
        ).all()

    def get_active_deployments(self) -> List[CapitalDeploymentModel]:
        """Get all active (funded, not recouped) deployments."""
        return self.db.query(self.model).filter(
            self.model.status.in_([
                AllocationStatusEnum.COMMITTED,
                AllocationStatusEnum.FUNDED
            ])
        ).all()


class DealBlockRepository(BaseRepository[DealBlockModel]):
    """Repository for Deal Block operations."""

    def get_by_deal_id(self, deal_id: str) -> Optional[DealBlockModel]:
        """Get deal by business ID."""
        return self.db.query(self.model).filter(
            self.model.deal_id == deal_id
        ).first()

    def get_by_project(self, project_id: str) -> List[DealBlockModel]:
        """Get all deals for a project."""
        return self.db.query(self.model).filter(
            self.model.project_id == project_id
        ).all()

    def get_by_counterparty(self, counterparty: str) -> List[DealBlockModel]:
        """Get all deals with a counterparty."""
        return self.db.query(self.model).filter(
            self.model.counterparty_name == counterparty
        ).all()


# === Repository Factory ===

def get_project_repository(db: Session) -> ProjectRepository:
    """Factory function for Project repository."""
    return ProjectRepository(ProjectModel, db)


def get_capital_program_repository(db: Session) -> CapitalProgramRepository:
    """Factory function for Capital Program repository."""
    return CapitalProgramRepository(CapitalProgramModel, db)


def get_capital_source_repository(db: Session) -> CapitalSourceRepository:
    """Factory function for Capital Source repository."""
    return CapitalSourceRepository(CapitalSourceModel, db)


def get_capital_deployment_repository(db: Session) -> CapitalDeploymentRepository:
    """Factory function for Capital Deployment repository."""
    return CapitalDeploymentRepository(CapitalDeploymentModel, db)


def get_deal_block_repository(db: Session) -> DealBlockRepository:
    """Factory function for Deal Block repository."""
    return DealBlockRepository(DealBlockModel, db)
