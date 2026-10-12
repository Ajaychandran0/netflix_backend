from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.middlewares.execptions import validation_exception_handler

def add_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust for prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Here you could add other middleware like logging, etc.
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
