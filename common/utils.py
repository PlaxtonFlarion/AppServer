import typing
from pathlib import Path
from pydantic import BaseModel
from fastapi import HTTPException
from cryptography.hazmat.primitives import serialization
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


def handle_signature(req: "LicenseRequest", app: str, key_file: str) -> dict:
    # 查询所有通行证记录
    codes = supabase.fetch_activation_code(code := req.code, app)
    if not codes:
        raise HTTPException(403, f"[!]通行证无效 -> {code}")

    active_info, castle = codes[0], req.castle

    if active_info["is_used"] and active_info["castle"] != castle:
        raise HTTPException(403, f"[!]通行证已绑定其他设备 -> {castle}")

    # 若已有其他进程 pending 此激活码，拒绝
    if active_info.get("pending", False):
        raise HTTPException(423, f"[!]授权正在处理，请稍后重试 ...")

    # 先设置 pending = True，防止并发使用
    if not supabase.mark_code_pending(code, app):
        raise HTTPException(500, f"[!]授权标记失败，请稍后重试 ...")

    try:
        # 使用私钥签发 LIC 文件内容
        license_data = signature.generate_license(
            code, castle, active_info["expire"], key_file
        )
    except Exception as e:
        supabase.clear_code_pending(code, app)
        raise HTTPException(400, f"[!]授权失败，请稍后重试 -> {e}")

    supabase.update_activation_status(code, app, castle)
    supabase.clear_code_pending(code, app)

    return license_data


if __name__ == '__main__':
    pass