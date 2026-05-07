"""
Pydantic models compartidos entre módulos y verticales.
"""
from __future__ import annotations
from datetime import date, datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field


# ─── Organizations ────────────────────────────────────────────────────────────

OrgSlug = Literal["sicoops", "pauops", "trujillosales"]


# ─── M1 LeadFinder ───────────────────────────────────────────────────────────

class TenderScore(BaseModel):
    score: int = Field(ge=0, le=100)
    go: bool
    reason_go: str | None = None
    reason_no: str | None = None
    estimated_prep_hours: float
    risk_flag: str | None = None
    key_requirement_gap: str | None = None


class TenderRecord(BaseModel):
    id: UUID | None = None
    org_slug: OrgSlug
    source: str
    external_id: str
    title: str
    budget_min: float | None = None
    budget_max: float | None = None
    deadline: date | None = None
    cpv_codes: list[str] = Field(default_factory=list)
    score: float | None = None
    status: Literal[
        "detected", "analyzing", "drafting", "submitted", "won", "lost"
    ] = "detected"
    full_text: str = ""
    created_at: datetime | None = None


# ─── PauOps ──────────────────────────────────────────────────────────────────

class OrderRecord(BaseModel):
    id: UUID | None = None
    org_slug: OrgSlug = "pauops"
    raw_message: str
    origin: str | None = None
    destination: str | None = None
    cargo_type: str | None = None
    weight_kg: float | None = None
    pickup_date: date | None = None
    client_name: str | None = None
    client_phone: str | None = None
    status: Literal[
        "received", "assigned", "in_transit", "delivered", "billed"
    ] = "received"
    driver_id: UUID | None = None


# ─── TrujilloSales ───────────────────────────────────────────────────────────

class BiogasLead(BaseModel):
    id: UUID | None = None
    org_slug: OrgSlug = "trujillosales"
    company: str
    country: str
    plant_capacity_nm3h: float | None = None
    contact_name: str | None = None
    contact_linkedin: str | None = None
    contact_email: str | None = None
    score: float | None = None
    status: Literal[
        "identified", "contacted", "replied", "meeting", "proposal", "closed"
    ] = "identified"
    notes: str = ""
