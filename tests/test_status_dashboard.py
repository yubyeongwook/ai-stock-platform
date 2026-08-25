import json

from status_dashboard import build_status_rows, render_html


def _write_client(path, **overrides):
    client = {
        "slug": "test-biz",
        "business_name": "테스트업체",
        "category": "고깃집",
        "location": "강남",
        "keywords": ["키워드"],
        "review_target_phone": None,
        "ga4_property_id": None,
    }
    client.update(overrides)
    path.write_text(json.dumps(client, ensure_ascii=False), encoding="utf-8")
    return client


def test_build_status_rows_reads_client_and_marks_inactive_vertical(tmp_path):
    clients_dir = tmp_path / "clients"
    clients_dir.mkdir()
    _write_client(clients_dir / "test-biz.json", category="치과")

    rows = build_status_rows(clients_dir=str(clients_dir), out_dir=str(tmp_path / "outbox"))
    assert len(rows) == 1
    assert rows[0]["vertical"] == "dental"
    assert rows[0]["vertical_active"] is False
    assert rows[0]["latest_content_date"] is None


def test_build_status_rows_picks_latest_outbox_date(tmp_path):
    clients_dir = tmp_path / "clients"
    clients_dir.mkdir()
    _write_client(clients_dir / "test-biz.json")

    out_dir = tmp_path / "outbox"
    (out_dir / "test-biz" / "2026-08-20").mkdir(parents=True)
    (out_dir / "test-biz" / "2026-08-25").mkdir(parents=True)

    rows = build_status_rows(clients_dir=str(clients_dir), out_dir=str(out_dir))
    assert rows[0]["latest_content_date"] == "2026-08-25"


def test_render_html_contains_business_name():
    rows = [
        {
            "slug": "x",
            "business_name": "예시업체",
            "vertical": "restaurant",
            "vertical_active": True,
            "has_phone": True,
            "latest_content_date": "2026-08-25",
        }
    ]
    html = render_html(rows)
    assert "예시업체" in html
    assert "활성" in html
