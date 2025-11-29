#  __  __ _     _     _ _
# |  \/  (_) __| | __| | | _____      ____ _ _ __ ___  ___
# | |\/| | |/ _` |/ _` | |/ _ \ \ /\ / / _` | '__/ _ \/ __|
# | |  | | | (_| | (_| | |  __/\ V  V / (_| | | |  __/\__ \
# |_|  |_|_|\__,_|\__,_|_|\___| \_/\_/ \__,_|_|  \___||___/
#

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .trace       import trace_middleware
from .performance import performance_middleware
from .logging     import logging_middleware
from .auth        import jwt_auth_middleware
from .exception   import exception_middleware


def register_middlewares(app: "FastAPI") -> None:
    # inbound 1（最外层）
    app.middleware("http")(trace_middleware        )
    # inbound 2
    app.middleware("http")(performance_middleware  )
    # inbound 3
    app.middleware("http")(logging_middleware      )
    # inbound 4
    app.middleware("http")(jwt_auth_middleware     )
    # inbound 5（最内层）
    app.middleware("http")(exception_middleware    )

    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )


if __name__ == '__main__':
    pass
