#   ____                    _
#  / ___| _   _ _ __   __ _| |__   __ _ ___  ___
#  \___ \| | | | '_ \ / _` | '_ \ / _` / __|/ _ \
#   ___) | |_| | |_) | (_| | |_) | (_| \__ \  __/
#  |____/ \__,_| .__/ \__,_|_.__/ \__,_|___/\___|
#              |_|
#

import os
import httpx
import typing
import string
import hashlib
import secrets
from pathlib import Path
from dotenv import load_dotenv
from common import const

# 判断是否是本地开发环境（存在 .env 文件）
if (env_path := Path(__file__).resolve().parents[1] / ".env").exists():
    load_dotenv(env_path)
    supabase_url = os.getenv(const.SUPABASE_URL)
    supabase_key = os.getenv(const.SUPABASE_KEY)
else:
    # supabase_url = f"/etc/secrets/{const.SUPABASE_URL}".strip()
    # supabase_key = f"/etc/secrets/{const.SUPABASE_KEY}".strip()
    supabase_url = Path("/etc/secrets", const.SUPABASE_URL).read_text().strip()
    supabase_key = Path("/etc/secrets", const.SUPABASE_KEY).read_text().strip()

# 校验是否正确加载
if not supabase_url or not supabase_key:
    raise EnvironmentError("环境变量未正确加载，请检查 .env 或 Render 配置。")

HEADERS = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}


class Supabase(object):

    def __init__(self, app: str, code: str, table: str):
        self.app = app.capitalize()  # Notes: 首字母大写
        self.code = code
        self.table = table

        self.__url = f"{supabase_url}/rest/v1/{self.table}"
        self.__params = {
            "app": "eq." + self.app, "code": "eq." + self.code
        }

    def fetch_activation_code(self) -> dict | None:
        response = httpx.get(
            self.__url, headers=HEADERS, params=self.__params
        )
        return data[0] if (data := response.json()) else None

    def update_activation_status(self, json: dict, *_, **__) -> typing.Optional[bool]:
        try:
            response = httpx.patch(
                self.__url, headers=HEADERS, params=self.__params, json=json
            )
            return response.status_code == 204
        except Exception as e:
            return print(f"❌ 回写失败: {e}")

    def mark_code_pending(self) -> bool:
        json = {"pending": True}
        headers = HEADERS | {"Prefer": "return=minimal"}
        response = httpx.patch(
            self.__url, headers=headers, params=self.__params, json=json
        )
        return response.status_code == 204

    def wash_code_pending(self) -> None:
        json = {"pending": False}
        headers = HEADERS | {"Prefer": "return=minimal"}
        httpx.patch(
            self.__url, headers=headers, params=self.__params, json=json
        )

    def generate_license_id(self, issued_at: str) -> str:
        raw = f"{self.app}:{self.code}:{issued_at}".encode(const.CHARSET)
        return hashlib.sha256(raw).hexdigest()

    def upload_code(self, secure_code:str, expire: str) -> None:
        json = {
            "app": self.app,
            "code": secure_code,
            "expire": expire,
            "is_used": False
        }
        response = httpx.post(self.__url, headers=HEADERS, json=json)
        if response.status_code not in (200, 201):
            print(f"❌ 插入失败: {secure_code} -> {response.status_code}: {response.text}")
        else:
            print(f"✅ 成功插入: {secure_code}")

    def generate_and_upload(self, count: int, expire: str) -> None:

        def secure_code() -> str:
            chars = string.ascii_uppercase + string.digits
            core = ''.join(secrets.choice(chars) for _ in range(36))
            return f"{self.app}-Key-{core[:8]}-{core[8:16]}-{core[16:]}"

        for _ in range(count):
            self.upload_code(secure_code(), expire)


if __name__ == "__main__":
    pass