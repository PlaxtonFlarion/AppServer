#  ____             _
# |  _ \ ___  _   _| |_ ___ _ __ ___
# | |_) / _ \| | | | __/ _ \ '__/ __|
# |  _ < (_) | |_| | ||  __/ |  \__ \
# |_| \_\___/ \__,_|\__\___|_|  |___/
#

from fastapi import FastAPI

from .alive      import alive_router
from .cargo      import cargo_router
from .permission import permission_router
from .speech     import speech_router


def register_routers(app: "FastAPI") -> None:
    app.include_router(alive_router       )
    app.include_router(cargo_router       )
    app.include_router(permission_router  )
    app.include_router(speech_router      )


if __name__ == '__main__':
    pass
