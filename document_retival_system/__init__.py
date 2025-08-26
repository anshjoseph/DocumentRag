from document_retival_system.file_ingestion import JsonIngestion, URLIngestion
from document_retival_system.lancedb_control import LanceDBControl


def parse_json(path):
    data = JsonIngestion().process(path)
    LanceDBControl().ingest_document(data)
    return data


def search(query, limit):
    return LanceDBControl().search_documents(query, limit)