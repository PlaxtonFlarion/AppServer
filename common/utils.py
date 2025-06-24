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
    """
    加载指定 .env 文件中的环境变量到系统环境中。

    逐行读取键值对并写入 `os.environ`，忽略注释与空行。

    Parameters
    ----------
    env_path : Path
        .env 文件路径
    """
    if env_path.exists():
        for line in env_path.read_text(encoding=const.CHARSET).splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip()


def current_env(*args, **__) -> dict[str, str]:
    """
    获取当前环境变量字典。

    优先读取项目根目录 `.env` 文件；若不存在，则从 `/etc/secrets` 读取密钥文件。

    Parameters
    ----------
    *args : str
        需要获取的环境变量名

    Returns
    -------
    dict[str, str]
        键为变量名，值为环境值
    """
    if (env_path := Path(__file__).resolve().parents[1] / ".env").exists():
        load_env_file(env_path)
        return {
            arg: os.getenv(arg) for arg in args
        }

    return {
        arg: Path(f"/etc/secrets/{arg}").read_text().strip() for arg in args
    }


def resolve_key(key_file: str) -> "Path":
    """
    获取密钥文件的绝对路径。

    优先使用 `/etc/secrets` 中的密钥路径；否则使用本地 `KEYS_DIR` 中的密钥。

    Parameters
    ----------
    key_file : str
        密钥文件名

    Returns
    -------
    Path
        密钥文件路径
    """
    return (__p__ if (
        __p__ := Path(f"/etc/secrets")
    ).exists() else Path(__file__).resolve().parents[1] / const.KEYS_DIR) / key_file


def resolve_template(directory: str, template_file: str) -> "Path":
    """
    获取模板文件的绝对路径。

    Parameters
    ----------
    directory : str
        模板所属子目录名

    template_file : str
        模板文件名

    Returns
    -------
    Path
        模板文件完整路径
    """
    return Path(__file__).resolve().parents[1] / const.TEMPLATES/ directory / template_file


def load_private_key(key_file: str) -> "PrivateKeyTypes":
    """
    加载 PEM 格式私钥。

    Parameters
    ----------
    key_file : str
        私钥文件名

    Returns
    -------
    PrivateKeyTypes
        加载后的私钥对象
    """
    path = resolve_key(key_file)
    with open(path, const.READ_KEY_MODE) as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key(key_file: str) -> "PublicKeyTypes":
    """
    加载 PEM 格式公钥。

    Parameters
    ----------
    key_file : str
        公钥文件名

    Returns
    -------
    PublicKeyTypes
        加载后的公钥对象
    """
    path = resolve_key(key_file)
    with open(path, const.READ_KEY_MODE) as f:
        return serialization.load_pem_public_key(f.read())


def hide_string(s: str, visible: int = 2, max_len: int = 21, mask: str = "*") -> str:
    """
    对字符串进行脱敏处理，仅显示前几个字符，其他使用掩码遮盖。

    Parameters
    ----------
    s : str
        原始字符串

    visible : int
        显示的起始字符数量，默认 2

    max_len : int
        最长返回长度（含省略号），默认 21

    mask : str
        掩码字符，默认 "*"

    Returns
    -------
    str
        脱敏后的字符串（带掩码和 " ..." 后缀）
    """
    if len(s) <= visible:
        return s

    remaining_len = max_len - visible - len(padding := " ...")
    masked = mask * max(0, remaining_len)
    return s[:visible] + masked + padding


if __name__ == '__main__':
    pass
