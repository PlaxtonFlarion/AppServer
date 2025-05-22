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


def current_env(*args, **__) -> dict[str, str]:
    if (env_path := Path(__file__).resolve().parents[1] / ".env").exists():
        load_dotenv(env_path)
        return {
            arg: os.getenv(arg) for arg in args
        }
    
    return {
        arg: Path(f"/etc/secrets/{arg}").read_text().strip() for arg in args
    }


if __name__ == '__main__':
    pass
