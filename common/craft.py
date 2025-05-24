#    ____            __ _
#   / ___|_ __ __ _ / _| |_
#  | |   | '__/ _` | |_| __|
#  | |___| | | (_| |  _| |_
#   \____|_|  \__,_|_|  \__|
#

import sys
from pathlib import Path
from loguru import logger
from common import const


def init_logger() -> None:
    (log_dir := Path("logs")).mkdir(parents=True, exist_ok=True)
    log_level = "INFO"

    logger.remove()

    logger.add(
        sys.stdout,
        level=log_level,
        format=const.PRINT_FORMAT
    )

    logger.add(
        log_dir / f"app_server.log",
        level=log_level,
        format=const.WRITE_FORMAT,
        rotation="1 MB",
        retention="7 days",
        compression="zip"
    )


if __name__ == '__main__':
    pass