# To launch: uvicorn api.main:app --reload
# To see Swagger: http://localhost:8000/docs

from fastapi import FastAPI
from contextlib import asynccontextmanager

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.config import EMBEDDING_MODEL_NAME
from infrastructure.load_db import DatabaseManager
from infrastructure.sqlite_embedding_repository import SqliteEmbeddingRepository
from api.routers import movies, rating, member
from api.error_handlers import register_error_handlers

#region Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Set up the embedding index when the app starts, to avoid calling a whole table every time."""
    
    conn = DatabaseManager().load_db()
    try:
        repo = SqliteEmbeddingRepository(conn)
        app.state.embedding_index = repo.load_index(EMBEDDING_MODEL_NAME)
    finally:
        conn.close()
    yield

app = FastAPI(
    title='Cinedata Project: Movie Info',
    description='APIs of simple movie details such as genres, cast and ratings.',
    version='1.0.0',
    lifespan=lifespan
)

# Add a general error handling
register_error_handlers(app)


#region Main
@app.get("/", tags=['General'])
def welcome():
    return {
        "message": "Welcome!"
    }

app.include_router(movies.router)
app.include_router(member.router)
app.include_router(rating.router)