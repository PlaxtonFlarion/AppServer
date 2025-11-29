#  __  __ _     _     _ _
# |  \/  (_) __| | __| | | _____      ____ _ _ __ ___  ___
# | |\/| | |/ _` |/ _` | |/ _ \ \ /\ / / _` | '__/ _ \/ __|
# | |  | | | (_| | (_| | |  __/\ V  V / (_| | | |  __/\__ \
# |_|  |_|_|\__,_|\__,_|_|\___| \_/\_/ \__,_|_|  \___||___/
#

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth        import jwt_auth_middleware
from .exception   import exception_middleware
from .logging     import log_requests
from .performance import performance_middleware
from .trace       import trace_middleware


def register_middlewares(app: "FastAPI") -> None:
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )

    app.middleware("http")(jwt_auth_middleware     )
    app.middleware("http")(exception_middleware    )
    app.middleware("http")(log_requests            )
    app.middleware("http")(performance_middleware  )
    app.middleware("http")(trace_middleware        )


if __name__ == '__main__':
    pass
