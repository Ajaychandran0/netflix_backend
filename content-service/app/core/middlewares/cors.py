from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def add_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust for prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Here you could add other middleware like logging, etc.
