#   ____  _                   _
#  / ___|(_) __ _ _ __   __ _| |_ _   _ _ __ ___
#  \___ \| |/ _` | '_ \ / _` | __| | | | '__/ _ \
#   ___) | | (_| | | | | (_| | |_| |_| | | |  __/
#  |____/|_|\__, |_| |_|\__,_|\__|\__,_|_|  \___|
#           |___/
#

import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from common import utils


def generate_license(code: str, castle: str, expire: str, issued:str, key_file: str) -> dict:
    private_key = utils.load_private_key(key_file)

    license_info = {
        "code": code.strip(),
        "castle": castle,
        "expire": expire,
        "issued": issued,
    }
    message_bytes = json.dumps(license_info, separators=(",", ":")).encode()

    signature = private_key.sign(
        message_bytes, padding.PKCS1v15(), hashes.SHA256()
    )

    """
    授权包结构如下：
    {
        "data": "<base64编码后的授权明文>",
        "signature": "<base64编码后的签名>"
    }
    
    其中 data 解码后格式为：
    {
        "code": "激活码",
        "castle": "机器唯一标识码",
        "expire": "授权到期时间，如 2025-12-31",
        "issued": "授权签发时间，如 2025-05-18T03:45:00.123456+00:00"
    }
    """
    return {
        "data": base64.b64encode(message_bytes).decode(),
        "signature": base64.b64encode(signature).decode()
    }


if __name__ == '__main__':
    pass
