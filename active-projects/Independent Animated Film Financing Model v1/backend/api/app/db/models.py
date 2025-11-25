"""
SQLAlchemy Database Models

Database models for persisting film financing data.
Designed for PostgreSQL with SQLAlchemy 2.0 async patterns.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum as PyEnum
import uuid

from sqlalchemy import (
    String, Text, Numeric, Integer, Boolean, Date, DateTime,
    Enum, ForeignKey, JSON, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)
from sqlalchemy.dialects.postgresql import UUID


# === Base Classes ===

class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class UUIDMixin:
    """Mixin for UUID primary key"""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


class TimestampMixin:
    """Mixin for created/updated timestamps"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


# === Enums ===

class ProgramTypeEnum(str, PyEnum):
    INTERNAL_POOL = "internal_pool"
    EXTERNAL_FUND = "external_fund"
    PRIVATE_EQUITY = "private_equity"
    FAMILY_OFFICE = "family_office"
    OUTPUT_DEAL = "output_deal"
    FIRST_LOOK = "first_look"
    OVERHEAD_DEAL = "overhead_deal"
    SPV = "spv"
    TAX_CREDIT_FUND = "tax_credit_fund"
    INTERNATIONAL_COPRO = "international_copro"
    GOVERNMENT_FUND = "government_fund"


class ProgramStatusEnum(str, PyEnum):
    PROSPECTIVE = "prospective"
    IN_NEGOTIATION = "in_negotiation"
    ACTIVE = "active"
    FULLY_DEPLOYED = "fully_deployed"
    WINDING_DOWN = "winding_down"
    CLOSED = "closed"


class AllocationStatusEnum(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    COMMITTED = "committed"
    FUNDED = "funded"
    RECOUPED = "recouped"
    WRITTEN_OFF = "written_off"


class DealTypeEnum(str, PyEnum):
    EQUITY = "equity"
    PRESALE = "presale"
    THEATRICAL_DISTRIBUTION = "theatrical_distribution"
    STREAMER_LICENSE = "streamer_license"
    GAP_FINANCING = "gap_financing"
    CO_PRODUCTION = "co_production"
    TALENT = "talent"
    OTHER = "other"


class DealStatusEnum(str, PyEnum):
    DRAFT = "draft"
    NEGOTIATING = "negotiating"
    TERM_SHEET = "term_sheet"
    CLOSED = "closed"
    TERMINATED = "terminated"


class ProjectStatusEnum(str, PyEnum):
    DEVELOPMENT = "development"
    PRE_PRODUCTION = "pre_production"
    PRODUCTION = "production"
    POST_PRODUCTION = "post_production"
    COMPLETED = "completed"


# === Capital Program Models ===

class CapitalProgramModel(Base, UUIDMixin, TimestampMixin):
    """Capital program / fund entity"""
    __tablename__ = "capital_programs"

    program_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    program_name: Mapped[str] = mapped_column(String(200), nullable=False)
    program_type: Mapped[ProgramTypeEnum] = mapped_column(
        Enum(ProgramTypeEnum, name="program_type_enum"),
        nullable=False
    )
    status: Mapped[ProgramStatusEnum] = mapped_column(
        Enum(ProgramStatusEnum, name="program_status_enum"),
        default=ProgramStatusEnum.PROSPECTIVE,
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(Text)
    target_size: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)

    # Management terms
    manager_name: Mapped[Optional[str]] = mapped_column(String(200))
    management_fee_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    carry_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    hurdle_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))

    # Term structure
    vintage_year: Mapped[Optional[int]] = mapped_column(Integer)
    investment_period_years: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    fund_term_years: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    extension_years: Mapped[int] = mapped_column(Integer, default=2, nullable=False)

    # Dates
    formation_date: Mapped[Optional[date]] = mapped_column(Date)
    first_close_date: Mapped[Optional[date]] = mapped_column(Date)
    final_close_date: Mapped[Optional[date]] = mapped_column(Date)

    # Constraints stored as JSON
    constraints: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    sources: Mapped[List["CapitalSourceModel"]] = relationship(
        back_populates="program",
        cascade="all, delete-orphan"
    )
    deployments: Mapped[List["CapitalDeploymentModel"]] = relationship(
        back_populates="program",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("target_size > 0", name="positive_target_size"),
        CheckConstraint("investment_period_years >= 1", name="valid_investment_period"),
        CheckConstraint("fund_term_years >= investment_period_years", name="valid_fund_term"),
        Index("ix_capital_programs_type_status", "program_type", "status"),
    )


class CapitalSourceModel(Base, UUIDMixin, TimestampMixin):
    """Capital source within a program"""
    __tablename__ = "capital_sources"

    source_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("capital_programs.id", ondelete="CASCADE"),
        nullable=False
    )
    source_name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), default="general", nullable=False)

    committed_amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2), nullable=False)
    drawn_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        default=Decimal("0"),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)

    # Terms
    interest_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    management_fee_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    carry_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    hurdle_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))

    # Restrictions stored as JSON
    geographic_restrictions: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    genre_restrictions: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    budget_range_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=18, scale=2))
    budget_range_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=18, scale=2))

    # Dates
    commitment_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    program: Mapped["CapitalProgramModel"] = relationship(back_populates="sources")

    __table_args__ = (
        CheckConstraint("committed_amount > 0", name="positive_committed"),
        CheckConstraint("drawn_amount >= 0", name="non_negative_drawn"),
        CheckConstraint("drawn_amount <= committed_amount", name="drawn_le_committed"),
        Index("ix_capital_sources_program", "program_id"),
    )


class CapitalDeploymentModel(Base, UUIDMixin, TimestampMixin):
    """Deployment of capital to a project"""
    __tablename__ = "capital_deployments"

    deployment_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("capital_programs.id", ondelete="CASCADE"),
        nullable=False
    )
    source_id: Mapped[Optional[str]] = mapped_column(String(50))
    project_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Financial amounts
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2), nullable=False)
    funded_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        default=Decimal("0"),
        nullable=False
    )
    recouped_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        default=Decimal("0"),
        nullable=False
    )
    profit_distributed: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        default=Decimal("0"),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)

    status: Mapped[AllocationStatusEnum] = mapped_column(
        Enum(AllocationStatusEnum, name="allocation_status_enum"),
        default=AllocationStatusEnum.PENDING,
        nullable=False
    )

    # Terms
    equity_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    recoupment_priority: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    backend_participation_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))

    # Dates
    allocation_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    funding_date: Mapped[Optional[date]] = mapped_column(Date)
    expected_recoupment_date: Mapped[Optional[date]] = mapped_column(Date)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    program: Mapped["CapitalProgramModel"] = relationship(back_populates="deployments")

    __table_args__ = (
        CheckConstraint("allocated_amount > 0", name="positive_allocated"),
        CheckConstraint("funded_amount >= 0", name="non_negative_funded"),
        CheckConstraint("funded_amount <= allocated_amount", name="funded_le_allocated"),
        CheckConstraint("recouped_amount >= 0", name="non_negative_recouped"),
        CheckConstraint("profit_distributed >= 0", name="non_negative_profit"),
        CheckConstraint("recoupment_priority BETWEEN 1 AND 15", name="valid_priority"),
        Index("ix_capital_deployments_program_status", "program_id", "status"),
    )


# === Project Models ===

class ProjectModel(Base, UUIDMixin, TimestampMixin):
    """Film project entity"""
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    project_budget: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2), nullable=False)

    genre: Mapped[Optional[str]] = mapped_column(String(50))
    jurisdiction: Mapped[Optional[str]] = mapped_column(String(100))
    rating: Mapped[Optional[str]] = mapped_column(String(20))

    status: Mapped[ProjectStatusEnum] = mapped_column(
        Enum(ProjectStatusEnum, name="project_status_enum"),
        default=ProjectStatusEnum.DEVELOPMENT,
        nullable=False
    )
    is_development: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_first_time_director: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    expected_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=18, scale=2))
    production_start_date: Mapped[Optional[date]] = mapped_column(Date)
    expected_release_date: Mapped[Optional[date]] = mapped_column(Date)

    description: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    deals: Mapped[List["DealBlockModel"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("project_budget > 0", name="positive_project_budget"),
        Index("ix_projects_status", "status"),
        Index("ix_projects_jurisdiction", "jurisdiction"),
    )


# === Deal Block Models ===

class DealBlockModel(Base, UUIDMixin, TimestampMixin):
    """Deal block entity"""
    __tablename__ = "deal_blocks"

    deal_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True
    )
    deal_name: Mapped[str] = mapped_column(String(200), nullable=False)
    deal_type: Mapped[DealTypeEnum] = mapped_column(
        Enum(DealTypeEnum, name="deal_type_enum"),
        nullable=False
    )
    status: Mapped[DealStatusEnum] = mapped_column(
        Enum(DealStatusEnum, name="deal_status_enum"),
        default=DealStatusEnum.DRAFT,
        nullable=False
    )

    counterparty_name: Mapped[str] = mapped_column(String(200), nullable=False)
    counterparty_type: Mapped[str] = mapped_column(String(50), default="company", nullable=False)

    # Financial terms
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    recoupment_priority: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    is_recoupable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    interest_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    premium_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    backend_participation_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    origination_fee_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    distribution_fee_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    sales_commission_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))

    # Rights and territory
    territories: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    is_worldwide: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rights_windows: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    term_years: Mapped[Optional[int]] = mapped_column(Integer)
    exclusivity: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    holdback_days: Mapped[Optional[int]] = mapped_column(Integer)

    # Ownership and control
    ownership_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    approval_rights_granted: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    has_board_seat: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_veto_rights: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    veto_scope: Mapped[Optional[str]] = mapped_column(String(200))
    ip_ownership: Mapped[str] = mapped_column(String(50), default="producer_retained", nullable=False)
    mfn_clause: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfn_scope: Mapped[Optional[str]] = mapped_column(String(200))

    # Reversion and sequel rights
    reversion_trigger_years: Mapped[Optional[int]] = mapped_column(Integer)
    reversion_trigger_condition: Mapped[Optional[str]] = mapped_column(String(200))
    sequel_rights_holder: Mapped[str] = mapped_column(String(50), default="producer", nullable=False)
    sequel_participation_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))

    # Cross-collateralization
    cross_collateralized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cross_collateral_scope: Mapped[Optional[str]] = mapped_column(String(200))

    # Risk metrics
    probability_of_closing: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2),
        default=Decimal("75"),
        nullable=False
    )
    complexity_score: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    project: Mapped[Optional["ProjectModel"]] = relationship(back_populates="deals")

    __table_args__ = (
        CheckConstraint("amount > 0", name="positive_deal_amount"),
        CheckConstraint("recoupment_priority BETWEEN 1 AND 15", name="valid_deal_priority"),
        CheckConstraint("probability_of_closing BETWEEN 0 AND 100", name="valid_probability"),
        CheckConstraint("complexity_score BETWEEN 1 AND 10", name="valid_complexity"),
        Index("ix_deal_blocks_project", "project_id"),
        Index("ix_deal_blocks_type_status", "deal_type", "status"),
    )


# === Repository Base ===

class BaseRepository:
    """
    Base repository with common CRUD operations.

    Usage:
        class CapitalProgramRepository(BaseRepository[CapitalProgramModel]):
            model = CapitalProgramModel
    """

    def __init__(self, session):
        self.session = session

    async def create(self, **kwargs):
        """Create a new entity"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, entity_id: uuid.UUID):
        """Get entity by UUID"""
        return await self.session.get(self.model, entity_id)

    async def get_by_unique_id(self, id_field: str, id_value: str):
        """Get entity by unique string ID field"""
        from sqlalchemy import select
        stmt = select(self.model).where(
            getattr(self.model, id_field) == id_value
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, **filters):
        """List all entities with optional filters"""
        from sqlalchemy import select
        stmt = select(self.model)
        for key, value in filters.items():
            if value is not None:
                stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, entity_id: uuid.UUID, **kwargs):
        """Update entity by ID"""
        instance = await self.get_by_id(entity_id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.session.commit()
            await self.session.refresh(instance)
        return instance

    async def delete(self, entity_id: uuid.UUID):
        """Delete entity by ID"""
        instance = await self.get_by_id(entity_id)
        if instance:
            await self.session.delete(instance)
            await self.session.commit()
            return True
        return False
