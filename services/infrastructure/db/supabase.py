#   ____                    _
#  / ___| _   _ _ __   __ _| |__   __ _ ___  ___
#  \___ \| | | | '_ \ / _` | '_ \ / _` / __|/ _ \
#   ___) | |_| | |_) | (_| | |_) | (_| \__ \  __/
#  |____/ \__,_| .__/ \__,_|_.__/ \__,_|___/\___|
#              |_|
#

import httpx
import typing
import string
import hashlib
import secrets
from loguru import logger
from utils import (
    const, toolset
)

env = toolset.current_env(
    const.SUPABASE_URL, const.SUPABASE_KEY
)

supabase_url = env[const.SUPABASE_URL]
supabase_key = env[const.SUPABASE_KEY]


class Supabase(object):

    def __init__(self):
        self.url = f"{supabase_url}/rest/v1/{const.LICENSE_CODES}"
        self.headers = {
            "apikey"        : supabase_key,
            "Authorization" : f"Bearer {supabase_key}"
        }
        self.timeout = 10.0

    def fetch_activation_code(self, app: str, code: str) -> typing.Optional[dict]:
        params   = {"app": f"eq.{app}", "code": f"eq.{code}"}
        response = httpx.get(
            self.url, headers=self.headers, params=params, timeout=self.timeout
        )
        response.raise_for_status()
        return data[0] if (data := response.json()) else None

    def update_activation_status(self, app: str, code: str, json: dict, *_, **__) -> typing.Optional[bool]:
        params   = {"app": f"eq.{app}", "code": f"eq.{code}"}
        response = httpx.patch(
            self.url, headers=self.headers, params=params, json=json, timeout=self.timeout
        )
        response.raise_for_status()
        return response.status_code == 204

    def mark_code_pending(self, app: str, code: str) -> bool:
        json    = {"pending": True}
        params  = {"app": f"eq.{app}", "code": f"eq.{code}"}
        headers = self.headers.copy() | {"Prefer": "return=minimal"}

        response = httpx.patch(
            self.url, headers=headers, params=params, json=json, timeout=self.timeout
        )
        response.raise_for_status()
        return response.status_code == 204

    def wash_code_pending(self, app: str, code: str) -> bool:
        json    = {"pending": False}
        params  = {"app": f"eq.{app}", "code": f"eq.{code}"}
        headers = self.headers.copy() | {"Prefer": "return=minimal"}

        response = httpx.patch(
            self.url, headers=headers, params=params, json=json, timeout=self.timeout
        )
        response.raise_for_status()
        return response.status_code == 204

    @staticmethod
    def generate_license_id(app: str, code: str, issued_at: str) -> str:
        raw = f"{app}:{code}:{issued_at}".encode(const.CHARSET)
        return hashlib.sha256(raw).hexdigest()

    def generate_and_upload(self, app: str, count: int, expire: str) -> None:

        def secure_code() -> str:
            chars = string.ascii_uppercase + string.digits
            core  = "".join(secrets.choice(chars) for _ in range(36))
            return f"{app}-Key-{core[:8]}-{core[8:16]}-{core[16:]}"

        def upload_code(code: str) -> None:
            json = {
                "app": app, "code": code, "expire": expire, "is_used": False
            }
            try:
                response = httpx.post(self.url, headers=self.headers, json=json)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"❌ 插入失败: {code} -> {e.response.status_code}: {e.response.text}")
            else:
                logger.info(f"✅ 成功插入: {code}")

        for _ in range(count): upload_code(secure_code())


if __name__ == "__main__":
    pass
