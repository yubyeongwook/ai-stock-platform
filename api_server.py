"""api_server.py — AI GROWTH OS Command Center용 API 스켈레톤 (로컬 전용).

`docs/ai-growth-os-architecture.md` Phase 1의 "API CORE" 최소 구현. 지금은:
- 회사(Company) 등록/조회/수정 — Company Core 데이터의 실제 소스가 파일(clients/*.json)에서
  DB로 이동한다
- `company_core.build_company_profile()`을 그대로 재사용해 6개 카테고리 프로필을 반환

아직 없는 것 (정직하게 밝힘): 인증, Agent Registry, Workflow Engine, Connector,
Redis/Queue, Vector DB, Postgres 배포 — 전부 이 스켈레톤 범위 밖이다. 배포도 안 한다.
`uvicorn api_server:app --reload`로 로컬에서만 띄워서 API 형태를 검증하는 용도.
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from company_core import build_company_profile, render_summary
from db import get_db, init_db
from db_models import Company


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Growth OS — Company Core API (local skeleton)", lifespan=_lifespan)


class CompanyIn(BaseModel):
    slug: str
    business_name: str
    category: str
    location: str | None = None
    homepage: str | None = None
    business_description: str | None = None
    flagship_product: str | None = None
    price: str | None = None
    hours: str | None = None
    employee_count: int | None = None
    keywords: list[str] = []
    existing_channels: list[str] = []
    ad_budget: float | None = None
    review_target_phone: str | None = None
    ga4_property_id: str | None = None
    existing_customers_summary: str | None = None
    customer_stage: str | None = None
    revenue: float | None = None
    target_revenue: float | None = None
    funnel_rates: dict[str, float] = {}
    variable_cost_rate: float | None = None
    freedom_level: int | None = None
    banned_terms: list[str] = []
    known_facts: list[str] = []


@app.post("/companies", status_code=201)
def create_company(payload: CompanyIn, db: Session = Depends(get_db)):
    if db.get(Company, payload.slug):
        raise HTTPException(status_code=409, detail=f"'{payload.slug}' 이미 등록된 회사입니다")

    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    try:
        return build_company_profile(company.to_client_dict())
    except ValueError as e:
        db.delete(company)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/companies")
def list_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).order_by(Company.business_name).all()
    return [
        {"company_id": c.slug, "business_name": c.business_name, "category": c.category, "location": c.location}
        for c in companies
    ]


@app.get("/companies/{slug}")
def get_company(slug: str, db: Session = Depends(get_db)):
    company = db.get(Company, slug)
    if not company:
        raise HTTPException(status_code=404, detail=f"'{slug}' 회사를 찾을 수 없습니다")
    return build_company_profile(company.to_client_dict())


@app.get("/companies/{slug}/summary")
def get_company_summary(slug: str, db: Session = Depends(get_db)):
    company = db.get(Company, slug)
    if not company:
        raise HTTPException(status_code=404, detail=f"'{slug}' 회사를 찾을 수 없습니다")
    profile = build_company_profile(company.to_client_dict())
    return {"summary": render_summary(profile)}


class CompanyPatch(BaseModel):
    revenue: float | None = None
    target_revenue: float | None = None
    review_target_phone: str | None = None
    ga4_property_id: str | None = None
    ad_budget: float | None = None
    funnel_rates: dict[str, float] | None = None
    variable_cost_rate: float | None = None
    freedom_level: int | None = None


@app.patch("/companies/{slug}")
def patch_company(slug: str, payload: CompanyPatch, db: Session = Depends(get_db)):
    company = db.get(Company, slug)
    if not company:
        raise HTTPException(status_code=404, detail=f"'{slug}' 회사를 찾을 수 없습니다")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    try:
        return build_company_profile(company.to_client_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
