#    ____            __ _
#   / ___|_ __ __ _ / _| |_
#  | |   | '__/ _` | |_| __|
#  | |___| | | (_| |  _| |_
#   \____|_|  \__,_|_|  \__|
#

import sys
from pathlib import Path
from loguru import logger


def init_logger(level: str = "INFO") -> None:
    (log_dir := Path("logs")).mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        level=level,
        format="<bold><level>{level}</level></bold>: <bold><cyan>{message}</cyan></bold>"
    )

    logger.add(
        log_dir / f"app_server.log",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="1 MB",
        retention="7 days",
        compression="zip"
    )


if __name__ == '__main__':
    pass