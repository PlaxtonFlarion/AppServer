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

        self.__params = {
            "app": "eq." + self.app, "code": "eq." + self.code
        }

    def fetch_activation_code(self) -> dict | None:
        url = f"{supabase_url}/rest/v1/{self.table}"
        response = httpx.get(
            url, headers=HEADERS, params=self.__params
        )
        return data[0] if (data := response.json()) else None

    def update_activation_status(self, json: dict, *_, **__) -> typing.Optional[bool]:
        url = f"{supabase_url}/rest/v1/{self.table}"
        try:
            response = httpx.patch(
                url, headers=HEADERS, params=self.__params, json=json
            )
            return response.status_code == 204
        except Exception as e:
            return logger.info(f"❌ 回写失败: {e}")

    def mark_code_pending(self) -> bool:
        url = f"{supabase_url}/rest/v1/{self.table}"
        json = {"pending": True}
        headers = HEADERS | {"Prefer": "return=minimal"}
        response = httpx.patch(
            url, headers=headers, params=self.__params, json=json
        )
        return response.status_code == 204

    def wash_code_pending(self) -> None:
        url = f"{supabase_url}/rest/v1/{self.table}"
        json = {"pending": False}
        headers = HEADERS | {"Prefer": "return=minimal"}
        httpx.patch(
            url, headers=headers, params=self.__params, json=json
        )

    def generate_license_id(self, issued_at: str) -> str:
        raw = f"{self.app}:{self.code}:{issued_at}".encode(const.CHARSET)
        return hashlib.sha256(raw).hexdigest()

    def upload_code(self, secure_code:str, expire: str) -> None:
        url = f"{supabase_url}/rest/v1/{self.table}"
        json = {
            "app": self.app.capitalize(),
            "code": secure_code,
            "expire": expire,
            "is_used": False
        }
        response = httpx.post(url, headers=HEADERS, json=json)
        if response.status_code not in (200, 201):
            logger.error(f"❌ 插入失败: {secure_code} -> {response.status_code}: {response.text}")
        else:
            logger.info(f"✅ 成功插入: {secure_code}")

    def generate_and_upload(self, count: int, expire: str) -> None:

        def secure_code() -> str:
            chars = string.ascii_uppercase + string.digits
            core = ''.join(secrets.choice(chars) for _ in range(36))
            return f"{self.app.capitalize()}-Key-{core[:8]}-{core[8:16]}-{core[16:]}"

        for _ in range(count):
            self.upload_code(secure_code(), expire)


if __name__ == "__main__":
    pass
