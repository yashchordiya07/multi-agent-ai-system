"""
FastAPI entry point.
Provides /api/query, /health, /api/memory, /api/cache/stats.
"""

import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas.models    import QueryRequest, FinalResponse, ErrorResponse
from agents.orchestrator import Orchestrator
from utils.logger      import setup_logger, get_logger
from utils import cache as Cache
from utils import memory as Memory

# Boot logger (creates logs/ dir)
setup_logger("agent_system")
logger = get_logger("main")

os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Multi-Agent AI System (Ollama) — starting up")
    yield
    logger.info("🛑 Multi-Agent AI System — shutting down")


app = FastAPI(
    title="Multi-Agent AI System (Ollama)",
    description="Autonomous Decision Engine powered by llama3:8b via Ollama",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / latency middleware ───────────────────────────────────────────

@app.middleware("http")
async def _trace(request: Request, call_next):
    rid   = uuid.uuid4().hex[:8]
    start = time.time()
    request.state.rid = rid
    logger.info("[%s] ▶ %s %s", rid, request.method, request.url.path)
    response = await call_next(request)
    ms = round((time.time() - start) * 1000, 1)
    logger.info("[%s] ◀ %d — %.0fms", rid, response.status_code, ms)
    response.headers["X-Request-ID"] = rid
    response.headers["X-Latency-Ms"] = str(ms)
    return response


# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health", tags=["ops"])
async def health():
    return {
        "status":  "ok",
        "service": "Multi-Agent AI System",
        "model":   "llama3:8b",
        "version": "1.0.0",
    }


@app.post(
    "/api/query",
    tags=["pipeline"],
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def run_query(request: Request, body: QueryRequest):
    rid = getattr(request.state, "rid", uuid.uuid4().hex[:8])
    logger.info("[%s] Query received: '%s'", rid, body.query[:80])

    # Cache check
    cached = Cache.get(body.query)
    if cached:
        logger.info("[%s] Cache HIT — returning stored result", rid)
        cached["_meta"]["cached"] = True
        return JSONResponse(content=cached)

    try:
        orch   = Orchestrator(request_id=rid)
        result = await orch.run(query=body.query, context=body.context)
        Cache.set(body.query, result)
        return JSONResponse(content=result)

    except ValueError as exc:
        logger.warning("[%s] Validation error: %s", rid, exc)
        raise HTTPException(status_code=400, detail=str(exc))

    except RuntimeError as exc:
        logger.error("[%s] Runtime error: %s", rid, exc)
        raise HTTPException(status_code=503, detail=str(exc))

    except Exception as exc:
        logger.error("[%s] Unexpected error: %s", rid, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")


@app.get("/api/memory", tags=["ops"])
async def get_memory():
    return {"entries": Memory.get_all(), "count": Memory.count()}


@app.delete("/api/memory", tags=["ops"])
async def clear_memory():
    Memory.clear_all()
    return {"message": "Memory cleared"}


@app.get("/api/cache/stats", tags=["ops"])
async def cache_stats():
    return Cache.stats()
