#   _   _ _   _ _
#  | | | | |_(_) |___
#  | | | | __| | / __|
#  | |_| | |_| | \__ \
#   \___/ \__|_|_|___/
#

import typing
from pydantic import BaseModel
from fastapi import HTTPException
from datetime import (
    datetime, timezone
)
from common import (
    signature, supabase
)


class LicenseRequest(BaseModel):
    code: str
    castle: str
    license_id: typing.Optional[str] = None


def handle_signature(req: "LicenseRequest", apps: dict) -> dict:
    sup = supabase.Supabase(
        apps["app"], code := req.code, apps["table"]["license"]
    )

    # 查询所有通行证记录
    codes = sup.fetch_activation_code()
    if not codes:
        raise HTTPException(403, f"[!]通行证无效")

    # 查询最大激活次数
    if codes["activations"] >= codes["max_activations"]:
        raise HTTPException(403, f"[!]超过最大激活次数")

    # 查询通行证是否吊销
    if codes["is_revoked"]:
        raise HTTPException(403, f"[!]通行证已被吊销")

    # 若已有其他进程 pending 此通行证，拒绝
    if codes["pending"]:
        raise HTTPException(423, f"[!]授权正在处理中")

    pre_castle, cur_castle= codes["castle"], req.castle

    try:
        sup.mark_code_pending()  # pending 正在处理授权请求

        # 本次授权请求签发时间
        json = {
            "issued": (issued := datetime.now(timezone.utc).isoformat())
        }

        pre_license_id = codes["license_id"]

        # 用户重复激活，同设备联网检查通行证状态
        if codes["is_used"] and cur_castle == pre_castle and req.license_id == pre_license_id:
            issued_at, license_id = codes["issued_at"], pre_license_id
        else:
            issued_at, license_id = issued, sup.generate_license_id(issued)
            json.update({
                "castle": cur_castle, "is_used": True, "activations": codes["activations"] + 1
            })

        license_data = signature.generate_license(
            code, cur_castle, codes["expire"], issued, issued_at, license_id, apps["private_key"]
        )

        sup.update_activation_status(json | {"issued_at": issued_at, "license_id": license_id})

    except Exception as e:
        raise HTTPException(400, f"[!]授权失败，请稍后重试 -> {e}")

    else:
        return license_data

    finally:
        sup.wash_code_pending()  # 清除 pending 状态


if __name__ == '__main__':
    pass