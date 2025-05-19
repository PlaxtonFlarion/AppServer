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
        raise HTTPException(403, f"[!]通行证无效 -> {code}")

    # 查询最大激活次数
    if codes["activations"] >= codes["max_activations"]:
        raise HTTPException(403, f"[!]超过最大激活次数 ...")

    # 查询通行证是否吊销
    if codes["is_revoked"]:
        raise HTTPException(403, f"[!]通行证已被吊销，请重新申请 ...")

    # 若已有其他进程 pending 此通行证，拒绝
    if codes["pending"]:
        raise HTTPException(423, f"[!]授权正在处理，请稍后重试 ...")

    pre_castle, cur_castle, is_used = codes["castle"], req.castle, codes["is_used"]
    issued = datetime.now(timezone.utc).isoformat()

    try:
        sup.mark_code_pending()

        if is_used:
            pre_license_id, cur_license_id = codes["license_id"], req.license_id
            issued_at, license_id = codes["issued_at"], pre_license_id
            if cur_license_id == pre_license_id:
                sup.update_activation_status(**{"issued": issued})
            else:
                sup.update_activation_status(**{"issued": issued, "issued_at": issued})

        else:
            issued_at, license_id = issued, sup.generate_license_id(issued)
            sup.update_activation_status(
                **{"castle": cur_castle, "is_used": True,
                   "issued": issued, "issued_at": issued, "license_id": license_id}
            )

        license_data = signature.generate_license(
            code, cur_castle, codes["expire"], issued, issued_at, license_id, apps["private_key"]
        )

        sup.increment_activation_count(codes["activations"] + 1)

    except Exception as e:
        raise HTTPException(400, f"[!]授权失败，请稍后重试 -> {e}")
    else:
        return license_data
    finally:
        sup.wash_code_pending()


if __name__ == '__main__':
    pass