"""Rate limiting simples (janela deslizante, em memória, por IP).

Nota: em memória = por processo. Se o serviço rodar com múltiplas réplicas,
migre para um contador compartilhado (ex.: Redis) antes de escalar horizontalmente.
"""

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

EXEMPT_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.limit = requests_per_minute
        self.window_seconds = 60
        self.hits: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        client_id = request.client.host if request.client else "unknown"
        now = time.monotonic()
        bucket = self.hits[client_id]

        while bucket and now - bucket[0] > self.window_seconds:
            bucket.popleft()

        if len(bucket) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        f"Limite de {self.limit} requisições/minuto excedido. "
                        "Aguarde um pouco e tente novamente."
                    )
                },
            )

        bucket.append(now)
        return await call_next(request)
