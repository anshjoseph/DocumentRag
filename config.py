from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv(".env")


class Config(BaseModel):
    lancedb_path :str
    embed_model : str
    
    ai_endpoint : str
    ai_api : str
    ai_model : str

    server_host : str
    server_port : int

_config:Config = None

def get_config():
    global _config
    if _config == None:
        _config = Config(
            lancedb_path=os.environ["LANCE_DB"],
            embed_model=os.environ["EMBED_MODEL"],
            
            ai_endpoint=os.environ["AI_ENDPOINT"],
            ai_api=os.environ["AI_API"],
            ai_model=os.environ["AI_MODEL"],

            server_host=os.environ["SERVER_HOST"],
            server_port=os.environ["SERVER_PORT"]
        )
    return _config