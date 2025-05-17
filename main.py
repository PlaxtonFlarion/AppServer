from fastapi import FastAPI
from common import (
    utils, const
)

app = FastAPI()


@app.post(f"/sign/{const.APP_FX}")
async def sign_fx(req: "utils.LicenseRequest"):
    key_code = const.FX_CODES, const.FX_PRIVATE_KEY
    return utils.handle_signature(req, *key_code)


@app.post(f"/sign/{const.APP_MX}")
async def sign_mx(req: "utils.LicenseRequest"):
    key_code = const.MX_CODES, const.MX_PRIVATE_KEY
    return utils.handle_signature(req, *key_code)


if __name__ == '__main__':
    pass
