#  ____               _ _      _     ____             _
# |  _ \ _ __ ___  __| (_) ___| |_  |  _ \ ___  _   _| |_ ___ _ __
# | |_) | '__/ _ \/ _` | |/ __| __| | |_) / _ \| | | | __/ _ \ '__|
# |  __/| | |  __/ (_| | | (__| |_  |  _ < (_) | |_| | ||  __/ |
# |_|   |_|  \___|\__,_|_|\___|\__| |_| \_\___/ \__,_|\__\___|_|
#

from fastapi import (
    APIRouter, Request, Query
)
from schemas.cognitive import PredictResponse
from services.domain.standard.predict import resolve_proxy_predict

predict_router = APIRouter(tags=["Predict"])


@predict_router.get(
    path="/proxy-predict",
    response_model=PredictResponse,
    operation_id="api_proxy_predict"
)
async def api_proxy_predict(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    代理推理请求接口。

    将客户端请求转发至 Modal/GPU 模型服务，支持 Token 校验。
    """

    return await resolve_proxy_predict(request, a, t, n)


if __name__ == '__main__':
    pass
