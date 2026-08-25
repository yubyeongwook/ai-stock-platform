"""카카오 알림톡 발송 클라이언트.

카카오는 알림톡 API를 직접 제공하지 않는다 — 카카오 공식 파트너사(대행사, 예: 알리고·비즈고·NHN Toast 등)와
계약해야 API 키가 나온다. 이 모듈은 대행사가 어디든 재사용 가능하도록
인증·설정 뼈대만 잡아두고, 실제 요청 파라미터(`_build_payload`)는
계약한 대행사의 공식 API 문서를 보고 반드시 맞춰 넣어야 한다.
(연동 전 필요 절차: 카카오 비즈니스 채널 개설·인증 → 알림톡 템플릿 등록·심사 → 대행사 계약)
"""

import os

import requests


class AlimtalkConfigError(RuntimeError):
    pass


class KakaoAlimtalkClient:
    def __init__(
        self,
        api_base_url: str | None = None,
        api_key: str | None = None,
        user_id: str | None = None,
        sender_key: str | None = None,
    ):
        self.api_base_url = api_base_url or os.environ.get("ALIMTALK_API_BASE_URL")
        self.api_key = api_key or os.environ.get("ALIMTALK_API_KEY")
        self.user_id = user_id or os.environ.get("ALIMTALK_USER_ID")
        self.sender_key = sender_key or os.environ.get("ALIMTALK_SENDER_KEY")

        if not self.api_base_url or not self.api_key:
            raise AlimtalkConfigError(
                "ALIMTALK_API_BASE_URL / ALIMTALK_API_KEY가 설정되지 않았습니다. "
                "대행사 계약 후 발급받은 값을 .env에 채워 넣으세요."
            )

    def _build_payload(self, phone: str, template_code: str, variables: dict, fallback_sms: str | None) -> dict:
        # TODO: 계약한 대행사(알리고/비즈고/NHN Toast 등)의 공식 API 문서 기준으로
        # 파라미터명을 맞춰야 한다. 아래는 대행사들이 공통적으로 요구하는 필드를
        # 참고해 잡아둔 초안이며, 실제 발송 전 대행사 문서와 반드시 대조할 것.
        return {
            "apikey": self.api_key,
            "userid": self.user_id,
            "senderkey": self.sender_key,
            "tpl_code": template_code,
            "receiver": phone,
            "variables": variables,
            "fallback_sms": fallback_sms,
        }

    def send(
        self,
        phone: str,
        template_code: str,
        variables: dict,
        fallback_sms: str | None = None,
        dry_run: bool = True,
    ) -> dict:
        """알림톡 1건 발송. dry_run=True(기본값)면 실제 전송 없이 payload만 반환한다."""

        payload = self._build_payload(phone, template_code, variables, fallback_sms)

        if dry_run:
            return {"dry_run": True, "payload": payload}

        response = requests.post(self.api_base_url, data=payload, timeout=10)
        response.raise_for_status()
        return response.json()
