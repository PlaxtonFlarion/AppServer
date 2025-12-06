#  ____
# |  _ \  ___   ___ ___
# | | | |/ _ \ / __/ __|
# | |_| | (_) | (__\__ \
# |____/ \___/ \___|___/
#

from fastapi import APIRouter
from fastapi.responses import (
    FileResponse, HTMLResponse
)
from utils import (
    const, toolset
)

docs_router = APIRouter(tags=["Docs"])


@docs_router.get(path="/openapi.json", include_in_schema=False)
async def openapi_file() -> FileResponse:
    return FileResponse(path="openapi.json", media_type="application/json")


@docs_router.get(path="/docs", include_in_schema=False)
async def docs() -> HTMLResponse:
    html = toolset.resolve_template("static", "api_docs.html")
    with open(html, "r", encoding=const.CHARSET) as f:
        html = f.read()

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
