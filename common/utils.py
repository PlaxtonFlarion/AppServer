#   _   _ _   _ _
#  | | | | |_(_) |___
#  | | | | __| | / __|
#  | |_| | |_| | \__ \
#   \___/ \__|_|_|___/
#

import os
from faker import Faker
from pathlib import Path
from dotenv import load_dotenv

fake = Faker()


def current_env(url_name: str, key_name: str) -> tuple[str, str]:
    if (env_path := Path(__file__).resolve().parents[1] / ".env").exists():
        load_dotenv(env_path)
        service_url = os.getenv(url_name)
        service_key = os.getenv(key_name)
    else:
        service_url = Path("/etc/secrets", key_name).read_text().strip()
        service_key = Path("/etc/secrets", url_name).read_text().strip()

    if not service_url or not service_key:
        raise EnvironmentError("环境变量未正确加载，请检查 .env 或 Render 配置。")

    return service_url, service_key


if __name__ == '__main__':
    pass