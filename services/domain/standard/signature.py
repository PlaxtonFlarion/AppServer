#   ____  _                   _
#  / ___|(_) __ _ _ __   __ _| |_ _   _ _ __ ___
#  \___ \| |/ _` | '_ \ / _` | __| | | | '__/ _ \
#   ___) | | (_| | | | | (_| | |_| |_| | | |  __/
#  |____/|_|\__, |_| |_|\__,_|\__|\__,_|_|  \___|
#           |___/
#

import uuid
import time
import hmac
import json
import base64
import secrets
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
from fastapi import (
    Request, HTTPException
)
from schemas.cognitive import LicenseRequest
from services.infrastructure.db.supabase import Supabase
from utils import (
    const, toolset
)

env = toolset.current_env(
    const.SHARED_SECRET
)

shared_secret = env[const.SHARED_SECRET]


def generate_keys() -> None:
    (key_folder := Path(__file__).resolve().parents[1] / const.KEYS_DIR).mkdir(exist_ok=True)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key  = private_key.public_key()

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

    return logger.success(f"✓ 密钥已生成 -> {key_folder}")


def generate_x_app_token(app_name: str, app_desc: str) -> str:
    x_app_token = signature_license(
        license_info={
            "app"        : (a := app_desc.strip()),
            "time"       : (t := hashlib.sha1(str(time.monotonic_ns()).encode()).hexdigest()[:12].upper()),
            "nonce"      : (n := uuid.uuid4().hex.upper()[:12]),
            "license_id" : hashlib.sha256((a + t + n).encode()).hexdigest()[:16].upper()
        },
        private_key=f"{app_name.lower().strip()}_{const.BASE_PRIVATE_KEY}"
    )

    x_app_token_str = base64.b64encode(json.dumps(x_app_token).encode()).decode()
    logger.info(x_app_token_str)

    return x_app_token_str


def generate_shared_secret(length: int = 32) -> str:
    secret_bytes = secrets.token_bytes(length)

    return base64.b64encode(secret_bytes).decode()


def decrypt_data(data: str, private_key: str) -> str:
    private_key = toolset.load_private_key(private_key)
    decrypted   = private_key.decrypt(
        base64.b64decode(data), padding.PKCS1v15()
    )

    return json.loads(decrypted)


def sign_token(app_id: str, expire_at: int) -> str:
    payload = f"{app_id}:{expire_at}"
    sig     = hmac.new(shared_secret.encode(), payload.encode(), hashlib.sha256).digest()
    token   = f"{payload}.{base64.b64encode(sig).decode()}"

    return token


def signature_license(license_info: dict, private_key: str) -> dict:
    message_bytes = json.dumps(license_info, separators=(",", ":")).encode(const.CHARSET)
    private_key   = toolset.load_private_key(private_key)
    signature     = private_key.sign(
        message_bytes, padding.PKCS1v15(), hashes.SHA256()
    )

    logger.info(f"签名: {license_info}")

    return {
        "data"      : base64.b64encode(message_bytes).decode(),
        "signature" : base64.b64encode(signature).decode()
    }


def verify_jwt(x_app_id: str, x_app_token: str) -> dict:
    logger.info(f"X-App-ID: {x_app_id}")
    logger.info(f"X-App-Token: {toolset.hide_string(x_app_token)}")

    b64_dec = lambda s: base64.b64decode(s + "=" * (-len(s) % 4), validate=True)

    try:
        head_b64, payload_b64, sig_b64 = x_app_token.split(".")
    except Exception:
        raise ValueError("invalid token format")

    try:
        header  = json.loads(b64_dec(head_b64))
        payload = json.loads(b64_dec(payload_b64))
    except Exception:
        raise ValueError("invalid token encoding")

    if header.get("alg") != "HS256":
        raise ValueError("unsupported alg")

    # 重算签名
    signing_input = f"{head_b64}.{payload_b64}".encode()
    expect_sig    = hmac.new(shared_secret.encode(), signing_input, hashlib.sha256).digest()
    got_sig       = b64_dec(sig_b64)

    if not hmac.compare_digest(expect_sig, got_sig):
        raise ValueError("invalid signature")

    # 时效校验
    now = int(time.time())
    exp = int(payload.get("exp", 0))
    iat = int(payload.get("iat", 0))

    leeway = 30

    if now > exp + leeway:
        raise ValueError("token expired")
    if iat - now > leeway:
        raise ValueError("iat in the future")

    logger.info(f"验证通过: {payload}")

    return payload


def manage_signature(req: LicenseRequest, request: Request) -> dict:
    app_name        = req.a.lower().strip()
    app_desc        = req.a
    activation_code = req.code.strip()

    supabase: Supabase = request.app.state.supabase

    # Notes: ==== 1) 通行证预检 ====
    if not (codes := supabase.fetch_activation_code(app_name, activation_code)):
        raise HTTPException(status_code=403, detail=f"[!] 通行证无效")

    if codes["is_revoked"]:
        raise HTTPException(status_code=403, detail=f"[!] 通行证已吊销")

    if datetime.now(timezone.utc).date() > datetime.fromisoformat(codes["expire"]).date():
        raise HTTPException(status_code=403, detail=f"[!] 通行证已过期")

    if codes["pending"]:
        raise HTTPException(status_code=423, detail=f"[!] 授权正在处理中")

    if req.n == codes["last_nonce"]:
        raise HTTPException(status_code=409, detail=f"[!] 重放请求被拒绝")

    # Notes: ==== 2) 业务逻辑层 ====
    pre_castle     = codes["castle"]
    cur_castle     = req.castle
    pre_license_id = codes["license_id"]

    # pending 正在处理授权请求
    supabase.mark_code_pending(app_name, activation_code)

    try:
        issued  = datetime.now(timezone.utc).isoformat()
        payload = {"issued": issued}

        logger.info(f"pre_castle: {pre_castle}")
        logger.info(f"cur_castle: {cur_castle}")
        logger.info(f"pre_license_id: {pre_license_id}")
        logger.info(f"cur_license_id: {req.license_id}")

        # 同设备重复激活
        if codes["is_used"] and cur_castle == pre_castle and req.license_id == pre_license_id:
            issued_at, license_id = codes["issued_at"], pre_license_id
        else:
            # 达到最大激活次数
            if codes["activations"] >= codes["max_activations"]:
                raise HTTPException(status_code=403, detail=f"[!] 超过最大激活次数")

            issued_at  = issued
            license_id = supabase.generate_license_id(app_name, activation_code, issued)

            payload.update({
                "castle": cur_castle, "is_used": True, "activations": codes["activations"] + 1
            })

        # 生成 License File
        license_info = {
            "app"        : app_desc,
            "code"       : activation_code,
            "castle"     : cur_castle,
            "expire"     : codes["expire"],
            "issued"     : issued,
            "issued_at"  : issued_at,
            "license_id" : license_id,
            "interval"   : codes["interval"]
        }
        license_data = signature_license(
            license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
        )

        # 更新状态
        supabase.update_activation_status(
            app_name, activation_code, payload | {
                "issued_at": issued_at, "last_nonce": req.n, "license_id": license_id
            }
        )

        logger.success(f"下发 License file {license_info}")
        return license_data

    finally:
        # 不管成功失败都要清除 pending 状态
        supabase.wash_code_pending(app_name, activation_code)


if __name__ == '__main__':
    pass
