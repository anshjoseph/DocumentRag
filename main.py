import tempfile
import os
import json
from fastapi import FastAPI, Request, Form
import uvicorn
from config import get_config
from contextlib import asynccontextmanager
from document_retival_system import (
    init,
    delete_document,
    search,
    parse_json,
    list_document,
    parse_url,
)
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any


@asynccontextmanager
async def lifespan(app):
    init()
    yield


app = FastAPI(lifespan=lifespan)

# Jinja templates for frontend
templates = Jinja2Templates(directory="./doc_rag_ui/dist")

# ======================
#   Static Files
# ======================
app.mount(
    "/assets",
    StaticFiles(directory="./doc_rag_ui/dist/assets"),
    name="assets",
)

# ======================
#   Frontend Routes
# ======================

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    response = templates.TemplateResponse("index.html", {"request": request})
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/vite.svg")
async def vite_svg():
    return FileResponse("./dist/vite.svg")


# ======================
#   Document API Routes
# ======================

@app.post("/documents/ingest/json")
async def ingest_json_document(
    title: str = Form(..., description="Title of the document"),
    content: str = Form(..., description="Content of the document"),
):
    """
    Ingest a JSON document into LanceDB.
    - Takes title + content
    - Creates a temp JSON file
    - Passes it to parse_json
    """
    doc = {"title": title, "content": content}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as tmp:
        json.dump(doc, tmp, ensure_ascii=False, indent=2)
        tmp_path = tmp.name

    try:
        data = parse_json(tmp_path)
    finally:
        os.remove(tmp_path)

    return {"status": "success", "type": "json", "data": data}


@app.post("/documents/ingest/aep-url")
async def ingest_url_document(
    url: str = Form(..., description="URL of the document"),
):
    """
    Ingest a document from a URL into LanceDB.
    """
    data = parse_url(url)
    return {"status": "success", "type": "url", "data": data}


@app.get("/documents", response_model=List[Dict[str, Any]])
async def get_documents():
    return list_document()


@app.delete("/documents/{doc_id}")
async def remove_document(doc_id: str):
    success = delete_document(doc_id)
    return {"status": "success" if success else "failed", "doc_id": doc_id}


@app.get("/documents/search", response_model=List[Dict[str, Any]])
async def search_documents(query: str, limit: int = 1):
    return search(query, limit)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=get_config().server_host,
        port=get_config().server_port,
    )
