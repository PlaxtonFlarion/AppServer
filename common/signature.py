import json
import base64
from datetime import (
    datetime, timezone
)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from common import utils


def generate_license(code: str, castle: str, expire: str, key_file: str) -> dict:
    private_key = utils.load_private_key(key_file)

    license_info = {
        "code": code.strip(),
        "castle": castle,
        "expire": expire,
        "issued": datetime.now(timezone.utc).isoformat()
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
