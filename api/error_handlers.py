from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.movie_service import NotFoundError

async def not_found_handler(request: Request, error: NotFoundError):
    return JSONResponse(status_code=404, content={ "detail": str(error) })

def register_error_handlers(app: FastAPI):
    app.add_exception_handler(NotFoundError, not_found_handler)