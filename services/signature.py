#   ____  _                   _
#  / ___|(_) __ _ _ __   __ _| |_ _   _ _ __ ___
#  \___ \| |/ _` | '_ \ / _` | __| | | | '__/ _ \
#   ___) | | (_| | | | | (_| | |_| |_| | | |  __/
#  |____/|_|\__, |_| |_|\__,_|\__|\__,_|_|  \___|
#           |___/
#

import uuid
import time
import json
import base64
import typing
import hashlib
from pathlib import Path
from loguru import logger
from datetime import (
    datetime, timezone
)
from cryptography.hazmat.primitives import (
    hashes, serialization
)
from cryptography.hazmat.primitives.asymmetric import (
    padding, rsa
)
from pydantic import BaseModel
from fastapi import HTTPException
from services import supabase
from common import (
    const, utils
)


class LicenseRequest(BaseModel):
    code: str
    castle: str
    a: str
    t: int
    n: str
    license_id: typing.Optional[str] = None


def generate_keys() -> None:
    (key_folder := Path(__file__).resolve().parents[1] / const.KEYS_DIR).mkdir(exist_ok=True)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    (key_folder / const.APP_PRIVATE_KEY).write_bytes(private_pem)

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    (key_folder / const.APP_PUBLIC_KEY).write_bytes(public_pem)

    return print(f"✓ 密钥已生成 -> {key_folder}")


def generate_x_app_token(app: str) -> dict:
    return {
        "a": (a := app),
        "t": (t := hashlib.sha1(str(time.monotonic_ns()).encode()).hexdigest()[:12].upper()),
        "n": (n := uuid.uuid4().hex.upper()[:12]),
        "license_id": hashlib.sha256((a + t + n).encode()).hexdigest()[:16].upper()
    }


def decrypt_data(data: str, private_key_file: str) -> str:
    private_key = utils.load_private_key(private_key_file)

    decrypted = private_key.decrypt(
        base64.b64decode(data), padding.PKCS1v15()
    )
    return json.loads(decrypted)


def signature_license(license_info: dict, private_key_file: str, compress: bool = False) -> str | dict:
    message_bytes = json.dumps(license_info, separators=(",", ":")).encode(const.CHARSET)

    private_key = utils.load_private_key(private_key_file)

    signature = private_key.sign(
        message_bytes, padding.PKCS1v15(), hashes.SHA256()
    )

    token = {
        "data": base64.b64encode(message_bytes).decode(),
        "signature": base64.b64encode(signature).decode()
    }

    logger.info(f"下发签名: {license_info}")

    if compress:
        return base64.b64encode(json.dumps(token).encode()).decode()
    return token


def verify_signature(x_app_id: str, x_app_token: str, public_key_file: str) -> dict:
    if not x_app_id or not x_app_token:
        raise HTTPException(403, f"[!] 签名无效")

    logger.info(x_app_id)
    logger.info(x_app_token)
    
    try:
        app_token = json.loads(
            base64.b64decode(x_app_token).decode(const.CHARSET)
        )
        data = base64.b64decode(app_token["data"])
        signature = base64.b64decode(app_token["signature"])

        public_key = utils.load_public_key(public_key_file)

        public_key.verify(
            signature, data, padding.PKCS1v15(), hashes.SHA256()
        )

    except Exception as e:
        logger.error(e)
        raise HTTPException(403, f"[!] 签名无效")

    logger.info(f"验证签名: {(auth_info := json.loads(data))}")
    return auth_info


def handle_signature(
        req: "LicenseRequest",
        x_app_id: str,
        x_app_token: str
) -> dict:

    app_name = req.a.lower().strip()

    verify_signature(x_app_id, x_app_token, public_key_file=f"{app_name}_{const.BASE_PUBLIC_KEY}")

    sup = supabase.Supabase(
        req.a, code := req.code, table=f"{app_name}_{const.LICENSE_CODES}"
    )

    # 查询所有通行证记录
    if not (codes := sup.fetch_activation_code()):
        raise HTTPException(403, f"[!] 通行证无效")

    # 查询通行证是否吊销
    if codes["is_revoked"]:
        raise HTTPException(403, f"[!] 通行证已被吊销")

    # 查询最大激活次数
    if codes["activations"] >= codes["max_activations"]:
        raise HTTPException(403, f"[!] 超过最大激活次数")

    # 若已有其他进程 pending 此通行证，拒绝
    if codes["pending"]:
        raise HTTPException(423, f"[!] 授权正在处理中")

    # 防重放：如果 nonce 相同则拒绝
    if req.n == codes["last_nonce"]:
        raise HTTPException(409, "[!] 重放请求被拒绝")

    pre_castle, cur_castle= codes["castle"], req.castle

    try:
        sup.mark_code_pending()  # pending 正在处理授权请求

        # 本次授权请求签发时间
        payload = {
            "issued": (issued := datetime.now(timezone.utc).isoformat())
        }

        pre_license_id = codes["license_id"]

        logger.info(f"pre_castle {pre_castle}")
        logger.info(f"cur_castle {cur_castle}")
        logger.info(f"pre_license_id {pre_license_id}")
        logger.info(f"cur_license_id {req.license_id}")

        # 用户重复激活，同设备联网检查通行证状态
        if codes["is_used"] and cur_castle == pre_castle and req.license_id == pre_license_id:
            issued_at, license_id = codes["issued_at"], pre_license_id
        else:
            issued_at, license_id = issued, sup.generate_license_id(issued)
            payload.update({
                "castle": cur_castle, "is_used": True, "activations": codes["activations"] + 1
            })

        license_info = {
            "app": req.a,
            "code": code,
            "castle": cur_castle,
            "expire": codes["expire"],
            "issued": issued,
            "issued_at": issued_at,
            "license_id": license_id
        }
        license_data = signature_license(
            license_info, private_key_file=f"{req.a}_{const.BASE_PRIVATE_KEY}"
        )

        sup.update_activation_status(
            payload | {"issued_at": issued_at, "last_nonce": req.n, "license_id": license_id}
        )

    except Exception as e:
        logger.error(e)
        raise HTTPException(400, f"[!] 授权失败，请稍后重试")

    else:
        return license_data

    finally:
        sup.wash_code_pending()  # 清除 pending 状态


if __name__ == '__main__':
    pass
