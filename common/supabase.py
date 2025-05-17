import os
import httpx
import typing
import string
import secrets
from pathlib import Path
from dotenv import load_dotenv
from common import const

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
supabase_url = os.getenv(const.SUPABASE_URL)
supabase_key = os.getenv(const.SUPABASE_KEY)

HEADERS = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}


def generate_secure_code(app: str) -> str:
    chars = string.ascii_uppercase + string.digits
    core = ''.join(secrets.choice(chars) for _ in range(24))
    return f"{app}-{core[:8]}-{core[8:16]}-{core[16:]}"


def generate_and_upload(count: int, app: str, expire: str) -> None:
    for _ in range(count):
        code = generate_secure_code(app)
        upload_code_to_supabase(code, app, expire)


def upload_code_to_supabase(code: str, app: str, expire: str) -> None:
    url = f"{supabase_url}/rest/v1/license_codes"
    json = {
        "code": code,
        "app": app,
        "expire": expire,
        "is_used": False
    }
    response = httpx.post(url, headers=HEADERS, json=json)
    if response.status_code not in (200, 201):
        print(f"❌ 插入失败: {code} -> {response.status_code}: {response.text}")
    else:
        print(f"✅ 成功插入: {code}")


def fetch_activation_code(code: str, app: str) -> dict | None:
    url = f"{supabase_url}/rest/v1/license_codes"
    params = {
        "code": "eq." + code, "app": "eq." + app
    }
    response = httpx.get(url, headers=HEADERS, params=params)
    return data[0] if (data := response.json()) else None


def update_activation_status(code: str, app: str, castle: str) -> typing.Optional[bool]:
    url = f"{supabase_url}/rest/v1/{const.SUPABASE_TABLE}"
    params = {
        "code": "eq." + code, "app": "eq." + app
    }
    json = {
        "is_used": True, "castle": castle
    }
    try:
        response = httpx.patch(url, headers=HEADERS, params=params, json=json)
        return response.status_code == 204  # 204 表示成功但无返回体
    except Exception as e:
        return print(f"❌ 回写失败: {e}")


def mark_code_pending(code: str, app: str) -> bool:
    url = f"{supabase_url}/rest/v1/license_codes"
    data = {"pending": True}
    params = {"code": f"eq.{code}", "app": f"eq.{app}"}
    headers = HEADERS | {"Prefer": "return=minimal"}
    r = httpx.patch(url, headers=headers, params=params, json=data)
    return r.status_code == 204


def clear_code_pending(code: str, app: str) -> None:
    url = f"{supabase_url}/rest/v1/license_codes"
    data = {"pending": False}
    params = {"code": f"eq.{code}", "app": f"eq.{app}"}
    headers = HEADERS | {"Prefer": "return=minimal"}
    httpx.patch(url, headers=headers, params=params, json=data)


if __name__ == "__main__":
    pass