"""메타(페이스북·인스타그램) 마케팅 API 클라이언트 — 리타겟팅 캠페인용 최소 래퍼.

공식 Graph API를 requests로 직접 호출한다(무거운 공식 SDK 없이).
사전 준비물: 메타 비즈니스 관리자 계정, 광고 계정 ID, 액세스 토큰(장기 토큰 권장),
웹/랜딩페이지에 설치된 메타 픽셀(리타겟팅 오디언스의 시드가 됨).

캠페인 생성 계열 함수는 실제 광고비가 집행되므로 기본값을 dry_run=True로 두었다.
실제로 집행할 때만 명시적으로 dry_run=False를 넘긴다.
"""

import os

import requests

GRAPH_API_VERSION_DEFAULT = "v21.0"  # 메타는 버전을 주기적으로 올린다 — 실행 전 최신 버전 확인 권장


class MetaAdsConfigError(RuntimeError):
    pass


class MetaAdsClient:
    def __init__(
        self,
        access_token: str | None = None,
        ad_account_id: str | None = None,
        api_version: str | None = None,
    ):
        self.access_token = access_token or os.environ.get("META_ACCESS_TOKEN")
        self.ad_account_id = ad_account_id or os.environ.get("META_AD_ACCOUNT_ID")
        self.api_version = api_version or os.environ.get("META_API_VERSION", GRAPH_API_VERSION_DEFAULT)

        if not self.access_token or not self.ad_account_id:
            raise MetaAdsConfigError(
                "META_ACCESS_TOKEN / META_AD_ACCOUNT_ID가 설정되지 않았습니다. "
                "메타 비즈니스 관리자에서 발급받은 값을 .env에 채워 넣으세요."
            )

        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def _post(self, path: str, payload: dict) -> dict:
        response = requests.post(f"{self.base_url}/{path}", data={**payload, "access_token": self.access_token}, timeout=15)
        response.raise_for_status()
        return response.json()

    def _get(self, path: str, params: dict) -> dict:
        response = requests.get(f"{self.base_url}/{path}", params={**params, "access_token": self.access_token}, timeout=15)
        response.raise_for_status()
        return response.json()

    def create_website_custom_audience(self, name: str, retention_days: int = 30, dry_run: bool = True) -> dict:
        """메타 픽셀 방문자 기반 리타겟팅 오디언스 생성 (전체 방문자 세그먼트)."""

        payload = {
            "name": name,
            "subtype": "WEBSITE",
            "retention_days": retention_days,
            "rule": '{"inclusions":{"operator":"or","rules":[{"event_sources":[{"type":"pixel"}],"retention_seconds":%d,"filter":{"operator":"and","filters":[{"field":"event","operator":"=","value":"PageView"}]}}]}}'
            % (retention_days * 86400),
        }

        if dry_run:
            return {"dry_run": True, "endpoint": f"act_{self.ad_account_id}/customaudiences", "payload": payload}

        return self._post(f"act_{self.ad_account_id}/customaudiences", payload)

    def get_account_insights(self, date_preset: str = "last_7d") -> dict:
        """광고 계정 성과 조회(집행 없음, 실제 API 호출) — 성과 분석 에이전트의 인풋 소스."""

        return self._get(f"act_{self.ad_account_id}/insights", {"date_preset": date_preset, "fields": "spend,cpc,ctr,actions"})
