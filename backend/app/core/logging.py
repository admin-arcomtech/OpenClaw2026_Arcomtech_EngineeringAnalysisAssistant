import logging
import uuid
from contextvars import ContextVar
from fastapi import Request

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
user_id_var: ContextVar[str] = ContextVar("user_id", default="-")


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.request_id = request_id_var.get("-")
        record.user_id = user_id_var.get("-")
        return super().format(record)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        StructuredFormatter(
            fmt="%(asctime)s [%(levelname)s] req=%(request_id)s user=%(user_id)s | %(name)s: %(message)s"
        )
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(getattr(logging, level.upper(), logging.INFO))


async def request_id_middleware(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    token = request_id_var.set(rid)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    request_id_var.reset(token)
    return response
