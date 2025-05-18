#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#

from fastapi import FastAPI
from common import (
    utils, const
)

app = FastAPI()


@app.api_route("/", methods=["GET", "HEAD"])
async def index():
    return {"message": "License Server is live"}


@app.get("/status")
async def status():
    return {"ok": True}


@app.post(f"/sign/{const.APP_FX['app']}")
async def sign_fx(req: "utils.LicenseRequest"):
    return utils.handle_signature(req, const.APP_FX)


@app.post(f"/sign/{const.APP_MX['app']}")
async def sign_mx(req: "utils.LicenseRequest"):
    return utils.handle_signature(req, const.APP_MX)


if __name__ == '__main__':
    pass
