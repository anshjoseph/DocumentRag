from fastapi import FastAPI
import uvicorn
from config import get_config
from contextlib import asynccontextmanager
from document_retival_system import LanceDBControl



@asynccontextmanager
async def lifespan(app):
    LanceDBControl()
    yield

app = FastAPI(lifespan=lifespan)



if __name__ == "__main__":
    uvicorn.run(
        app,
        host=get_config().server_host,
        port=get_config().server_port
    )
