from fastapi import FastAPI

from .auth        import jwt_auth_middleware
from .exception   import exception_middleware
from .performance import performance_middleware
from .trace       import trace_middleware


def register_middlewares(app: "FastAPI") -> None:
    app.middleware("http")(jwt_auth_middleware)
    app.middleware("http")(exception_middleware)
    app.middleware("http")(performance_middleware)
    app.middleware("http")(trace_middleware)


if __name__ == '__main__':
    pass
