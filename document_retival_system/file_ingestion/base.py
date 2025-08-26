from abc import ABC, abstractmethod
from openai import OpenAI
from config import get_config
from typing import Tuple
from document_retival_system.models.ingestion_content import IngestionContent
import json


class BaseIngestion(ABC):
    def __init__(self):
        super().__init__()
        self.client = OpenAI(
            api_key=get_config().ai_api,
            base_url=get_config().ai_endpoint
        )
    
    @abstractmethod
    def _process(self, path) -> Tuple[str, str, str]:
        "title, summary, content"
        pass
    
    def process(self, path) -> IngestionContent:
        title, summary, content = self._process(path)
        chunks = self.ingest(title, summary, content)
        return IngestionContent(title=title, summary=summary, content=chunks)

    def summarize(self, title: str, content: str) -> str:
        response = self.client.chat.completions.create(
            model=get_config().ai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a summarization assistant.\n\n"
                        "TASK:\n"
                        "- Read the provided text.\n"
                        "- Generate a clear, concise summary (3–5 sentences).\n"
                        "- Focus on the main ideas and important details.\n"
                        "- Do NOT include any markdown, bullet points, or JSON.\n"
                        "- Return only plain text."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"TITLE:\n{title}\n\n"
                        f"CONTENT:\n{content}\n\n"
                        "Please provide the summary:"
                    )
                }
            ]
        )

        summary = response.choices[0].message.content

        return summary

    def ingest(self, title: str, summary: str, content: str):
        response = self.client.chat.completions.create(
            model=get_config().ai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for preparing text for a Retrieval-Augmented Generation (RAG) system.\n\n"
                        "TASK:\n"
                        "- Split the provided content into semantically meaningful chunks.\n"
                        "- Each chunk should be concise (100–300 words max) but complete in thought.\n"
                        "- Ensure the output is valid JSON (list of strings).\n"
                        "- Do NOT include any markdown formatting, backticks, or extra commentary.\n\n"
                        f"TITLE:\n{title}\n\n"
                        f"SUMMARY:\n{summary}\n\n"
                        f"CONTENT:\n{content}\n\n"
                        "RULES:\n"
                        "1. Return ONLY valid JSON.\n"
                        "2. JSON must be a list of text chunks, e.g. [\"chunk1\", \"chunk2\", ...].\n"
                    )
                }
            ]
        )

        raw_text = response.choices[0].message.content

        # --- JSON Parsing with cleanup ---
        try:
            # Remove accidental ```json ... ``` wrappers if present
            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`").replace("json", "", 1).strip()

            chunks = json.loads(raw_text)
            if not isinstance(chunks, list):
                raise ValueError("Expected JSON list")
        except Exception as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nRaw output:\n{raw_text}")

        return chunks