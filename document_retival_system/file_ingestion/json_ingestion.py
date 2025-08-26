from document_retival_system.file_ingestion.base import BaseIngestion
import json

class JsonIngestion(BaseIngestion):
    def __init__(self):
        super().__init__()
    def _process(self, path):
        with open(path,'r') as file:
            data = json.load(file)
        summary = self.summarize(data['title'], data['content'])
        return data['title'], summary, data['content']