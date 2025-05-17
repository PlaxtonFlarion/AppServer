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


@app.post(f"/sign/{const.APP_FX}")
async def sign_fx(req: "utils.LicenseRequest"):
    key_code = const.APP_FX_DESC, const.FX_PRIVATE_KEY
    return utils.handle_signature(req, *key_code)


@app.post(f"/sign/{const.APP_MX}")
async def sign_mx(req: "utils.LicenseRequest"):
    key_code = const.APP_MX_DESC, const.MX_PRIVATE_KEY
    return utils.handle_signature(req, *key_code)


if __name__ == '__main__':
    pass
