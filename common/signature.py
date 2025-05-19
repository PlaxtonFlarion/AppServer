#   ____  _                   _
#  / ___|(_) __ _ _ __   __ _| |_ _   _ _ __ ___
#  \___ \| |/ _` | '_ \ / _` | __| | | | '__/ _ \
#   ___) | | (_| | | | | (_| | |_| |_| | | |  __/
#  |____/|_|\__, |_| |_|\__,_|\__|\__,_|_|  \___|
#           |___/
#

import json
import base64
import typing
from pathlib import Path
from cryptography.hazmat.primitives import (
    hashes, serialization
)
from cryptography.hazmat.primitives.asymmetric import padding
from common import const

JOB_DIR: "Path" = Path(__file__).resolve().parents[1]


def load_private_key(key_file: str) -> typing.Any:
    private_key_path = JOB_DIR / const.KEYS_DIR / key_file
    with open(private_key_path, const.READ_KEY_MODE) as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def generate_license(
        code: str,
        castle: str,
        expire: str,
        issued:str,
        issued_at:str,
        license_id: str,
        key_file: str
) -> dict:

    private_key = load_private_key(key_file)

    license_info = {
        "code": code.strip(),
        "castle": castle,
        "expire": expire,
        "issued": issued,
        "issued_at": issued_at,
        "license_id": license_id
    }
    message_bytes = json.dumps(license_info, separators=(",", ":")).encode()

    signature = private_key.sign(
        message_bytes, padding.PKCS1v15(), hashes.SHA256()
    )

    return {
        "data": base64.b64encode(message_bytes).decode(),
        "signature": base64.b64encode(signature).decode()
    }


if __name__ == '__main__':
    pass
