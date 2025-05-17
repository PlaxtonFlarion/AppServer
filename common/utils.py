import json
import uuid
import typing
from pathlib import Path
from pydantic import BaseModel
from fastapi import HTTPException
from cryptography.hazmat.primitives import serialization
from common import (
    const, signature
)

DISKS: "Path" = Path("mnt", "data")


class LicenseRequest(BaseModel):
    code: str
    castle: str


def load_codes(code_file: str) -> typing.Any:
    codes = json.load(open(
        DISKS / const.BOOKS_DIR / code_file, encoding=const.CHARSET
    ))
    return codes


def save_codes(dst: typing.Any, code_file: str) -> None:
    code_store = DISKS / const.BOOKS_DIR / code_file
    json.dump(dst, open(code_store, "w", encoding=const.CHARSET), indent=2)


def load_private_key(key_file: str) -> typing.Any:
    private_key_path = DISKS / const.KEYS_DIR / key_file
    with open(private_key_path, const.READ_KEY_MODE) as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def generate_activation_codes(count: int, expire: str, code_file: str) -> None:
    active_codes = {}
    for _ in range(count):
        code = str(uuid.uuid4()).upper()[:8] + "-" + str(uuid.uuid4()).upper()[:8]
        active_codes[code] = {
            "used": False, "castle": None, "expire": expire
        }
    save_codes(active_codes, code_file)


def handle_signature(req: "LicenseRequest", code_file: str, key_file: str) -> dict:
    if req.code not in (codes := load_codes(code_file)):
        raise HTTPException(status_code=403, detail="激活码无效")

    active_info, castle = codes[code := req.code], req.castle

    if active_info["used"] and active_info["castle"] != castle:
        raise HTTPException(status_code=403, detail="激活码已绑定其他设备")
    active_info.update({"used": True, "castle": castle})

    save_codes(codes, code_file)

    try:
        return signature.generate_license(
            code, castle, active_info["expire"], key_file
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == '__main__':
    # generate_activation_codes(30, "2025-12-31", const.FX_CODES)
    # generate_activation_codes(30, "2025-12-31", const.MX_CODES)
    pass