#  ____             _
# |  _ \ ___  _   _| |_ ___ _ __ ___
# | |_) / _ \| | | | __/ _ \ '__/ __|
# |  _ < (_) | |_| | ||  __/ |  \__ \
# |_| \_\___/ \__,_|\__\___|_|  |___/
#

from fastapi import FastAPI

from .rt_common    import common_router
from .rt_predict   import predict_router
from .rt_resource  import resource_router
from .rt_self_heal import self_heal_router
from .rt_signature import signature_router
from .rt_speech    import speech_router


def register_routers(app: FastAPI) -> None:
    app.include_router(common_router     )
    app.include_router(predict_router    )
    app.include_router(resource_router   )
    app.include_router(self_heal_router  )
    app.include_router(signature_router  )
    app.include_router(speech_router     )


if __name__ == '__main__':
    pass
