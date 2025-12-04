#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#

from fastapi import FastAPI

from services    import redis_cache
from utils       import toolset
from middlewares import register_middlewares
from routers     import register_routers


app = FastAPI()
app.state.cache = redis_cache.RedisCache()

toolset.init_logger()

register_middlewares(app)
register_routers(app)


if __name__ == '__main__':
    # uvicorn main:app --host=0.0.0.0 --port=8000
    pass
