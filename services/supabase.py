#   ____                    _
#  / ___| _   _ _ __   __ _| |__   __ _ ___  ___
#  \___ \| | | | '_ \ / _` | '_ \ / _` / __|/ _ \
#   ___) | |_| | |_) | (_| | |_) | (_| \__ \  __/
#  |____/ \__,_| .__/ \__,_|_.__/ \__,_|___/\___|
#              |_|
#

import time
import httpx
import typing
import string
import hashlib
import secrets
from loguru import logger
from common import (
    utils, const
)

env = utils.current_env(
    const.SUPABASE_URL, const.SUPABASE_KEY
)

supabase_url = env[const.SUPABASE_URL]
supabase_key = env[const.SUPABASE_KEY]

HEADERS = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}


class Supabase(object):

    def __init__(self, app: str, code: str, table: str):
        self.app = app
        self.code = code
        self.table = table
        self.timeout = 10.0

        self.params = {
            "app": f"eq.{self.app}", "code": f"eq.{self.code}"
        }

    def fetch_activation_code(self) -> dict | None:
        url = f"{supabase_url}/rest/v1/{self.table}"
        response = httpx.get(
            url, headers=HEADERS, params=self.params, timeout=self.timeout
        )
        try:
            return data[0] if (data := response.json()) else None
        except Exception as e:
            return logger.error(f"❌ 查询失败: {e}")

    def update_activation_status(self, json: dict, *_, **__) -> typing.Optional[bool]:
        url = f"{supabase_url}/rest/v1/{self.table}"
        try:
            response = httpx.patch(
                url, headers=HEADERS, params=self.params, json=json, timeout=self.timeout
            )
            return response.status_code == 204
        except Exception as e:
            return logger.info(f"❌ 回写失败: {e}")

    def mark_code_pending(self) -> bool:
        url = f"{supabase_url}/rest/v1/{self.table}"
        json = {"pending": True}
        headers = HEADERS | {"Prefer": "return=minimal"}
        response = httpx.patch(
            url, headers=headers, params=self.params, json=json, timeout=self.timeout
        )
        return response.status_code == 204

    def wash_code_pending(self) -> bool:
        url = f"{supabase_url}/rest/v1/{self.table}"
        json = {"pending": False}
        headers = HEADERS | {"Prefer": "return=minimal"}
        response = httpx.patch(
            url, headers=headers, params=self.params, json=json, timeout=self.timeout
        )
        return response.status_code == 204

    def generate_license_id(self, issued_at: str) -> str:
        raw = f"{self.app}:{self.code}:{issued_at}".encode(const.CHARSET)
        return hashlib.sha256(raw).hexdigest()

    def generate_and_upload(self, count: int, expire: str) -> None:

        def secure_code() -> str:
            chars = string.ascii_uppercase + string.digits
            core = "".join(secrets.choice(chars) for _ in range(36))
            return f"{self.app}-Key-{core[:8]}-{core[8:16]}-{core[16:]}"

        def upload_code(code: str) -> None:
            url = f"{supabase_url}/rest/v1/{self.table}"
            json = {
                "app": self.app, "code": code, "expire": expire, "is_used": False
            }
            try:
                response = httpx.post(url, headers=HEADERS, json=json)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"❌ 插入失败: {code} -> {e.response.status_code}: {e.response.text}")
            else:
                logger.info(f"✅ 成功插入: {code}")

        for _ in range(count):
            upload_code(secure_code())

    def keep_alive(self) -> dict:
        url = f"{supabase_url}/rest/v1/{self.table}"
        params = {"select": "id", "limit": 1}
        try:
            resp = httpx.get(
                url, headers=HEADERS, params=params, timeout=self.timeout
            )
            resp.raise_for_status()
            logger.info("🟢 Supabase online")
            return {
                "status": "OK",
                "message": "Supabase online",
                "timestamp": int(time.time()),
                "http_status": resp.status_code
            }

        except httpx.HTTPStatusError as e:
            logger.warning(f"🟡 Supabase offline: {e.response.status_code}")
            return {
                "status": "ERROR",
                "message": f"Supabase offline: {e.response.text}",
                "timestamp": int(time.time()),
                "http_status": e.response.status_code
            }

        except Exception as e:
            logger.error(f"🔴 Supabase connection error: {e}")
            return {
                "status": "ERROR",
                "message": f"Supabase connection error: {str(e)}",
                "timestamp": int(time.time())
            }


if __name__ == "__main__":
    pass
