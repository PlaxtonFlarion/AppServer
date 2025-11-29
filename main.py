#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#

from fastapi import FastAPI
from common import craft
from services.redis_cache import RedisCache
from middlewares import register_middlewares
from routers import register_routers

app = FastAPI()
app.state.cache = RedisCache()

craft.init_logger()

register_middlewares(app)
register_routers(app)


if __name__ == '__main__':
    pass
