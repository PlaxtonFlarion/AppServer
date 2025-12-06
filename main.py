#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#

from fastapi import FastAPI

from services.infrastructure.cache.upstash      import UpStash
from services.infrastructure.cloud.azure        import Azure
from services.infrastructure.llm.llm_groq       import LLMGroq
from services.infrastructure.storage.r2_storage import R2Storage
from services.infrastructure.vector.zilliz      import Zilliz

from utils       import toolset
from middlewares import register_middlewares
from routers     import register_routers


app: "FastAPI" = FastAPI(
    title="AppServerX",
    description="AppServerX Application Server",
    version="1.0.0"
)

toolset.init_logger()

app.state.cache    = UpStash()
app.state.azure    = Azure()
app.state.llm_groq = LLMGroq()
app.state.r2       = R2Storage()
app.state.store    = Zilliz()

app.state.r2.upload_openapi(app)

register_middlewares(app)
register_routers(app)


if __name__ == '__main__':
    # uvicorn main:app --host=0.0.0.0 --port=8000
    pass
