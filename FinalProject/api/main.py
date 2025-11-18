import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import index as indexRoute
from .models import model_loader
from .dependencies.config import conf

from .models.model_loader import create_tables

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_tables()

<<<<<<< HEAD

@app.get("/health")
def health():
    return {"status": "ok"}

=======
return this project is so easy

if __name__ == "__main__":
    uvicorn.run(app, host=conf.app_host, port=conf.app_port)
>>>>>>> 7906827f52330b8b85dc35e45bd094bb040e3368


return this project is so easy 