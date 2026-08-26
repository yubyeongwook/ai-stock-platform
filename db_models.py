"""db_models.py — Company Core의 DB 스키마 (SQLAlchemy ORM).

`company_core.build_company_profile()`이 기대하는 clients/*.json 필드를 그대로
컬럼으로 옮긴 것뿐이다 — 새로운 데이터 모델을 발명하지 않고, 이미 검증된 스키마를
파일에서 DB로 옮기는 것.
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class Company(Base):
    __tablename__ = "companies"

    slug: Mapped[str] = mapped_column(String, primary_key=True)
    business_name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    homepage: Mapped[str | None] = mapped_column(String, nullable=True)
    business_description: Mapped[str | None] = mapped_column(String, nullable=True)
    flagship_product: Mapped[str | None] = mapped_column(String, nullable=True)
    price: Mapped[str | None] = mapped_column(String, nullable=True)
    hours: Mapped[str | None] = mapped_column(String, nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    keywords: Mapped[list] = mapped_column(JSON, default=list)
    existing_channels: Mapped[list] = mapped_column(JSON, default=list)
    ad_budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_target_phone: Mapped[str | None] = mapped_column(String, nullable=True)
    ga4_property_id: Mapped[str | None] = mapped_column(String, nullable=True)

    existing_customers_summary: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_stage: Mapped[str | None] = mapped_column(String, nullable=True)

    revenue: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_revenue: Mapped[float | None] = mapped_column(Float, nullable=True)
    funnel_rates: Mapped[dict] = mapped_column(JSON, default=dict)
    variable_cost_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    freedom_level: Mapped[int | None] = mapped_column(Integer, nullable=True)

    banned_terms: Mapped[list] = mapped_column(JSON, default=list)
    known_facts: Mapped[list] = mapped_column(JSON, default=list)
    public_references: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_client_dict(self) -> dict:
        """company_core.build_company_profile()이 기대하는 clients/*.json 형태로 변환."""

        return {
            "slug": self.slug,
            "business_name": self.business_name,
            "category": self.category,
            "location": self.location,
            "homepage": self.homepage,
            "business_description": self.business_description,
            "flagship_product": self.flagship_product,
            "price": self.price,
            "hours": self.hours,
            "employee_count": self.employee_count,
            "keywords": self.keywords or [],
            "existing_channels": self.existing_channels or [],
            "ad_budget": self.ad_budget,
            "review_target_phone": self.review_target_phone,
            "ga4_property_id": self.ga4_property_id,
            "existing_customers_summary": self.existing_customers_summary,
            "customer_stage": self.customer_stage,
            "revenue": self.revenue,
            "target_revenue": self.target_revenue,
            "funnel_rates": self.funnel_rates or {},
            "variable_cost_rate": self.variable_cost_rate,
            "freedom_level": self.freedom_level,
            "banned_terms": self.banned_terms or [],
            "known_facts": self.known_facts or [],
        }
