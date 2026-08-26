import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api_server import app
from db import Base, get_db


@pytest.fixture()
def client():
    # 테스트마다 독립된 인메모리 SQLite — growth_os.db 파일을 건드리지 않는다.
    # StaticPool로 커넥션을 스레드 간 공유해야 FastAPI(다른 스레드에서 요청 처리)가
    # 같은 인메모리 DB를 본다 — 안 그러면 스레드마다 별도의 :memory: DB가 생긴다.
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_create_and_get_company(client):
    resp = client.post(
        "/companies",
        json={"slug": "test-restaurant", "business_name": "테스트식당", "category": "고깃집", "location": "강남"},
    )
    assert resp.status_code == 201
    profile = resp.json()
    assert profile["business_dna"]["vertical"] == "restaurant"
    assert profile["business_dna"]["vertical_active"] is True

    resp = client.get("/companies/test-restaurant")
    assert resp.status_code == 200
    assert resp.json()["business_profile"]["business_name"] == "테스트식당"


def test_duplicate_slug_rejected(client):
    payload = {"slug": "dup-co", "business_name": "업체", "category": "고깃집"}
    assert client.post("/companies", json=payload).status_code == 201
    assert client.post("/companies", json=payload).status_code == 409


def test_missing_company_returns_404(client):
    assert client.get("/companies/nope").status_code == 404
    assert client.get("/companies/nope/summary").status_code == 404
    assert client.patch("/companies/nope", json={"revenue": 1}).status_code == 404


def test_list_companies(client):
    client.post("/companies", json={"slug": "a", "business_name": "A", "category": "고깃집"})
    client.post("/companies", json={"slug": "b", "business_name": "B", "category": "치과"})
    resp = client.get("/companies")
    assert resp.status_code == 200
    slugs = {row["company_id"] for row in resp.json()}
    assert slugs == {"a", "b"}


def test_patch_updates_growth_profile(client):
    client.post("/companies", json={"slug": "growth-test", "business_name": "업체", "category": "고깃집"})
    resp = client.patch("/companies/growth-test", json={"revenue": 3000000, "target_revenue": 5000000})
    assert resp.status_code == 200
    gp = resp.json()["growth_profile"]
    assert gp["revenue"] == 3000000
    assert gp["revenue_gap"] == 2000000


def test_dental_vertical_blocked_via_api(client):
    resp = client.post("/companies", json={"slug": "dental-test", "business_name": "치과", "category": "치과"})
    assert resp.status_code == 201
    assert resp.json()["business_dna"]["vertical_active"] is False


def test_summary_endpoint_returns_readable_text(client):
    client.post("/companies", json={"slug": "summary-test", "business_name": "업체", "category": "고깃집", "location": "강동"})
    resp = client.get("/companies/summary-test/summary")
    assert resp.status_code == 200
    assert "업체" in resp.json()["summary"]


def test_freedom_level_and_profit_impact_flow_through_api(client):
    resp = client.post(
        "/companies",
        json={
            "slug": "x-demo",
            "business_name": "X데모식당",
            "category": "고깃집",
            "revenue": 10_000_000,
            "target_revenue": 20_000_000,
            "variable_cost_rate": 0.5,
            "freedom_level": 2,
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["business_dna"]["freedom_level"] == 2
    assert body["growth_profile"]["profit_impact"]["contribution_margin_gap"] == 5_000_000


def test_invalid_freedom_level_returns_400_not_500(client):
    resp = client.post(
        "/companies", json={"slug": "x-bad", "business_name": "배드", "category": "고깃집", "freedom_level": 9}
    )
    assert resp.status_code == 400
    # 실패한 생성 시도가 DB에 남아있으면 안 됨(재시도 시 슬러그 충돌)
    assert client.get("/companies/x-bad").status_code == 404
