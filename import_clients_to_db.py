"""import_clients_to_db.py — 기존 clients/*.json을 로컬 DB(growth_os.db)로 옮긴다.

일회성 마이그레이션 스크립트. slug 기준 upsert라 여러 번 돌려도 안전하다.
`public_references` 같은 clients/*.json에만 있고 db_models.Company에 없는 필드는
그대로 JSON 컬럼에 보존한다 — 스켈레톤이라고 정보를 버리지 않는다.
"""

import json
from pathlib import Path

from db import SessionLocal, init_db
from db_models import Company


def import_all(clients_dir: str = "clients") -> list[str]:
    init_db()
    db = SessionLocal()
    imported = []
    try:
        for path in sorted(Path(clients_dir).glob("*.json")):
            with open(path, encoding="utf-8") as f:
                client = json.load(f)

            existing = db.get(Company, client["slug"])
            fields = {
                "business_name": client["business_name"],
                "category": client["category"],
                "location": client.get("location"),
                "homepage": client.get("homepage"),
                "business_description": client.get("business_description"),
                "flagship_product": client.get("flagship_product"),
                "price": client.get("price"),
                "hours": client.get("hours"),
                "employee_count": client.get("employee_count"),
                "keywords": client.get("keywords", []),
                "existing_channels": client.get("existing_channels", []),
                "ad_budget": client.get("ad_budget"),
                "review_target_phone": client.get("review_target_phone"),
                "ga4_property_id": client.get("ga4_property_id"),
                "existing_customers_summary": client.get("existing_customers_summary"),
                "customer_stage": client.get("customer_stage"),
                "revenue": client.get("revenue"),
                "target_revenue": client.get("target_revenue"),
                "banned_terms": client.get("banned_terms", []),
                "known_facts": client.get("known_facts", []),
                "public_references": client.get("public_references"),
            }

            if existing:
                for k, v in fields.items():
                    setattr(existing, k, v)
            else:
                db.add(Company(slug=client["slug"], **fields))
            imported.append(client["slug"])

        db.commit()
    finally:
        db.close()
    return imported


def main():
    imported = import_all()
    print(f"{len(imported)}개 회사 DB로 가져옴: {', '.join(imported)}")


if __name__ == "__main__":
    main()
