from pydantic import BaseModel
from typing import List

class IngestionContent(BaseModel):
    title : str
    summary : str
    content : List[str]