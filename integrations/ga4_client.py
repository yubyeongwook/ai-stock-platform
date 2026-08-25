"""Google Analytics 4 데이터 조회 클라이언트 — 성과 분석 에이전트의 웹 전환 데이터 소스.

사전 준비물: GA4 속성(고객 웹사이트에 연결), 서비스 계정 생성 후
GA4 속성에 "뷰어" 권한으로 추가, 서비스 계정 키 JSON 파일.

의존성: pip install google-analytics-data (requirements.txt에 포함)
"""

import os


class GA4ConfigError(RuntimeError):
    pass


def _load_client():
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
    except ImportError as e:
        raise GA4ConfigError(
            "google-analytics-data 패키지가 설치되어 있지 않습니다. `pip install google-analytics-data`"
        ) from e

    credentials_path = os.environ.get("GA4_SERVICE_ACCOUNT_JSON")
    if not credentials_path:
        raise GA4ConfigError("GA4_SERVICE_ACCOUNT_JSON 환경변수(서비스 계정 키 파일 경로)가 설정되지 않았습니다.")

    return BetaAnalyticsDataClient.from_service_account_file(credentials_path)


def get_weekly_summary(property_id: str | None = None) -> dict:
    """최근 7일 세션·전환 이벤트 요약 — 성과 분석 에이전트가 매주 호출하는 함수."""

    property_id = property_id or os.environ.get("GA4_PROPERTY_ID")
    if not property_id:
        raise GA4ConfigError("GA4_PROPERTY_ID가 설정되지 않았습니다.")

    client = _load_client()  # 패키지 미설치·크리덴셜 미설정을 여기서 먼저 GA4ConfigError로 잡는다

    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="sessions"), Metric(name="conversions"), Metric(name="engagementRate")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
    )
    response = client.run_report(request)

    rows = [
        {
            "date": row.dimension_values[0].value,
            "sessions": row.metric_values[0].value,
            "conversions": row.metric_values[1].value,
            "engagement_rate": row.metric_values[2].value,
        }
        for row in response.rows
    ]
    return {"property_id": property_id, "rows": rows}
