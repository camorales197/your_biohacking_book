import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up the graph (creates SQLite DB and compiles graph on first access)
    from graph.graph import get_graph
    get_graph()
    yield


app = FastAPI(
    title="Biohacking Book Generator API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow configured frontend origins
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "biohacking-book-generator"}
