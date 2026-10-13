# To launch: uvicorn api.main:app --reload
# To see Swagger: http://localhost:8000/docs

from fastapi import FastAPI
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from routers.movies import router as movie_router
from api.error_handlers import register_error_handlers

app = FastAPI(
    title='Cinedata Project: Movie Info',
    description='APIs of simple movie details such as genres, cast and ratings.',
    version='1.0.0'
)

# Add a general error handling
register_error_handlers(app)

@app.get("/", tags=['General'])
def welcome():
    return {
        "message": "Welcome!"
    }

app.include_router(movie_router)