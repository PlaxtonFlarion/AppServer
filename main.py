#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#

import warnings
warnings.filterwarnings(
    action="ignore",
    message="pkg_resources is deprecated"
)

from fastapi import FastAPI

from services.infrastructure.cache.upstash      import UpStash
from services.infrastructure.cloud.azure        import Azure
from services.infrastructure.db.supabase        import Supabase
from services.infrastructure.llm.llm_groq       import LLMGroq
from services.infrastructure.storage.r2_storage import R2Storage
from services.infrastructure.vector.zilliz      import Zilliz

from middlewares import register_middlewares
from routers     import register_routers

from utils import (
    const, toolset
)


app = FastAPI(**const.SETTINGS)

toolset.init_logger()

app.state.cache    = UpStash()
app.state.azure    = Azure()
app.state.supabase = Supabase()
app.state.llm_groq = LLMGroq()
app.state.r2       = R2Storage()
app.state.store    = Zilliz()

register_middlewares(app)
register_routers(app)

toolset.generate_openapi_json(app)


if __name__ == '__main__':
    # uvicorn main:app --host=0.0.0.0 --port=8000
    pass
