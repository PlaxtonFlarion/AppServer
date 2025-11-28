#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#

from fastapi import FastAPI
from common import craft
from routers import (
    health, loader, predict, signature, source, speech
)
from services.redis_cache import RedisCache
from middlewares import register_middlewares

app = FastAPI()
app.state.cache = RedisCache()

register_middlewares(app)

craft.init_logger()

app.include_router(health.router     )
app.include_router(loader.router     )
app.include_router(predict.router    )
app.include_router(signature.router  )
app.include_router(source.router     )
app.include_router(speech.router     )


if __name__ == '__main__':
    pass
