#   _   _ _   _ _
#  | | | | |_(_) |___
#  | | | | __| | / __|
#  | |_| | |_| | \__ \
#   \___/ \__|_|_|___/
#

import os
from faker import Faker
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import (
    PrivateKeyTypes, PublicKeyTypes
)
from common import const

fake = Faker()


def load_env_file(env_path: "Path") -> None:
    if env_path.exists():
        for line in env_path.read_text(encoding=const.CHARSET).splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip()


def current_env(*args, **__) -> dict[str, str]:
    if (env_path := Path(__file__).resolve().parents[1] / ".env").exists():
        load_env_file(env_path)
        return {
            arg: os.getenv(arg) for arg in args
        }

    return {
        arg: Path(f"/etc/secrets/{arg}").read_text().strip() for arg in args
    }


def resolve_key(key_file: str) -> "Path":
    return (__p__ if (
        __p__ := Path(f"/etc/secrets")
    ).exists() else Path(__file__).resolve().parents[1] / const.KEYS_DIR) / key_file


def resolve_template(directory: str, template_file: str) -> "Path":
    return Path(__file__).resolve().parents[1] / const.TEMPLATES/ directory / template_file


def load_private_key(key_file: str) -> "PrivateKeyTypes":
    path = resolve_key(key_file)
    with open(path, const.READ_KEY_MODE) as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key(key_file: str) -> "PublicKeyTypes":
    path = resolve_key(key_file)
    with open(path, const.READ_KEY_MODE) as f:
        return serialization.load_pem_public_key(f.read())


def hide_string(s: str, visible: int = 2, max_len: int = 10, mask: str = "*") -> str:
    if len(s) <= visible:
        return s

    remaining_len = max_len - visible - len("...")
    masked = mask * max(0, remaining_len)
    return s[:visible] + masked + "..."


if __name__ == '__main__':
    pass
