#   _   _ _   _ _
#  | | | | |_(_) |___
#  | | | | __| | / __|
#  | |_| | |_| | \__ \
#   \___/ \__|_|_|___/
#

import typing
from pathlib import Path
from pydantic import BaseModel
from fastapi import HTTPException
from cryptography.hazmat.primitives import serialization
from datetime import (
    datetime, timezone
)
from common import (
    const, signature, supabase
)

JOB_DIR: "Path" = Path(__file__).resolve().parents[1]


class LicenseRequest(BaseModel):
    code: str
    castle: str


def load_private_key(key_file: str) -> typing.Any:
    private_key_path = JOB_DIR / const.KEYS_DIR / key_file
    with open(private_key_path, const.READ_KEY_MODE) as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def handle_signature(req: "LicenseRequest", apps: dict) -> dict:
    sup = supabase.Supabase(
        apps["app"], code := req.code, apps["table"]["license"]
    )

    # 查询所有通行证记录
    codes = sup.fetch_activation_code()
    if not codes:
        raise HTTPException(403, f"[!]通行证无效 -> {code}")

    # 查询通行证是否吊销
    if codes["is_revoked"]:
        raise HTTPException(403, f"[!]通行证已被吊销，请重新申请 ...")

    pre_castle, cur_castle, is_used = codes["castle"], req.castle, codes["is_used"]

    # 查询通行证使用和绑定情况
    if is_used and pre_castle != cur_castle:
        raise HTTPException(403, f"[!]通行证已绑定其他设备 -> {pre_castle}")

    # 若已有其他进程 pending 此通行证，拒绝
    if codes["pending"]:
        raise HTTPException(423, f"[!]授权正在处理，请稍后重试 ...")

    try:
        sup.mark_code_pending()

        issued = datetime.now(timezone.utc).isoformat()

        # Notes: 使用私钥签发 LIC 文件内容
        license_data = signature.generate_license(
            code, cur_castle, codes["expire"], issued, apps["private_key"]
        )

    except Exception as e:
        sup.wash_code_pending()
        raise HTTPException(400, f"[!]授权失败，请稍后重试 -> {e}")

    if is_used:
        sup.update_activation_status(**{"issued": issued})
    else:
        issued_at = issued
        sup.update_first_status(cur_castle, issued, issued_at)

    sup.wash_code_pending()

    return license_data


if __name__ == '__main__':
    print(datetime.now(timezone.utc))
    pass