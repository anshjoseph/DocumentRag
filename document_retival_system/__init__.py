from document_retival_system.file_ingestion import JsonIngestion, URLIngestion
from document_retival_system.lancedb_control import LanceDBControl
from typing import List, Dict, Any


def init():
    return LanceDBControl()
# parsing method
def parse_json(path):
    """
    path : it has to be file path or FileIO
    """
    data = JsonIngestion().process(path)
    LanceDBControl().ingest_document(data)
    return data
def parse_pdf(path):
    """
    path : it has to be file path or FileIO
    """
    data = JsonIngestion().process(path)
    LanceDBControl().ingest_document(data)
    return data

def parse_url(path):
    """
    path : it has to be file path or FileIO
    """
    data = JsonIngestion().process(path)
    LanceDBControl().ingest_document(data)
    return data

def list_document()  -> List[Dict[str, Any]]:
    return LanceDBControl().list_documents()

def delete_document(doc_id:str) -> bool:
    return LanceDBControl().delete_document(doc_id)


def search(query:str, limit: int = 5) -> List[Dict[str, Any]]:
    return LanceDBControl().search_documents(query, limit)