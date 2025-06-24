#    ____            __ _
#   / ___|_ __ __ _ / _| |_
#  | |   | '__/ _` | |_| __|
#  | |___| | | (_| |  _| |_
#   \____|_|  \__,_|_|  \__|
#

import sys
from loguru import logger
from common import const


def init_logger() -> None:
    """
    初始化日志系统。

    清除 Loguru 默认日志输出，添加新的终端输出配置，使用项目约定的日志级别与格式。
    依赖于 common.const 中定义的 SHOW_LEVEL 和 PRINT_FORMAT。
    """
    logger.remove()
    logger.add(sys.stdout, level=const.SHOW_LEVEL, format=const.PRINT_FORMAT)


if __name__ == '__main__':
    pass
