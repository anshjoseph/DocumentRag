from lancedb.embeddings import get_registry
import lancedb
from config import get_config
from sentence_transformers import SentenceTransformer
from document_retival_system.models.ingestion_content import IngestionContent
import uuid
from typing import List, Dict, Any
import pandas as pd
import pyarrow as pa
import numpy as np

class LanceDBControl:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LanceDBControl, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.db = lancedb.connect(get_config().lancedb_path)
            self.model = get_registry().get("sentence-transformers").create(name="all-MiniLM-L6-v2")
            self._initialize_tables()
            LanceDBControl._initialized = True
    
    def _initialize_tables(self):
        try:
            self.documents_table = self.db.open_table("Documents")
        except:
            # FIX: Use fixed size list for better performance
            vector_dim = 384  # all-MiniLM-L6-v2 produces 384-dimensional vectors
            documents_schema = pa.schema([
                pa.field("doc_id", pa.string()),
                pa.field("title", pa.string()),
                pa.field("summary", pa.string()),
                pa.field("combined_text", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), vector_dim))  # Fixed size list
            ])
            self.documents_table = self.db.create_table("Documents", schema=documents_schema)
        
        try:
            self.chunks_table = self.db.open_table("Chunks")
        except:
            # FIX: Use fixed size list for better performance
            vector_dim = 384  # all-MiniLM-L6-v2 produces 384-dimensional vectors
            chunks_schema = pa.schema([
                pa.field("chunk_id", pa.string()),
                pa.field("doc_id", pa.string()),
                pa.field("content", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), vector_dim))  # Fixed size list
            ])
            self.chunks_table = self.db.create_table("Chunks", schema=chunks_schema)
    
    def _ensure_vector_format(self, embedding):
        """Ensure embedding is in the correct format for LanceDB"""
        if isinstance(embedding, np.ndarray):
            return embedding.tolist()
        elif isinstance(embedding, list):
            return embedding
        else:
            # Handle other types (e.g., torch tensors)
            try:
                return embedding.cpu().numpy().tolist() if hasattr(embedding, 'cpu') else list(embedding)
            except:
                return list(embedding)
    
    def ingest_document(self, content: IngestionContent) -> str:
        doc_id = str(uuid.uuid4())
        combined_text = f"{content.title} {content.summary}"
        
        # FIX: Ensure proper vector formatting
        document_embedding = self.model.compute_source_embeddings([combined_text])[0]
        document_embedding = self._ensure_vector_format(document_embedding)
        
        document_data = {
            "doc_id": doc_id,
            "title": content.title,
            "summary": content.summary,
            "combined_text": combined_text,
            "vector": document_embedding
        }
        
        self.documents_table.add([document_data])
        
        chunk_data = []
        for chunk_content in content.content:
            chunk_id = str(uuid.uuid4())
            # FIX: Ensure proper vector formatting
            chunk_embedding = self.model.compute_source_embeddings([chunk_content])[0]
            chunk_embedding = self._ensure_vector_format(chunk_embedding)
            
            chunk_data.append({
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "content": chunk_content,
                "vector": chunk_embedding
            })
        
        if chunk_data:
            self.chunks_table.add(chunk_data)
        
        return doc_id
    
    def list_documents(self) -> List[Dict[str, Any]]:
        documents = self.documents_table.to_pandas()[["doc_id", "title", "summary"]].to_dict("records")
        return documents
    
    def delete_document(self, doc_id: str) -> bool:
        try:
            self.documents_table.delete(f"doc_id = '{doc_id}'")
            self.chunks_table.delete(f"doc_id = '{doc_id}'")
            return True
        except Exception:
            return False
    
    def debug_database(self):
        """Debug method to check database contents"""
        print("=== DATABASE DEBUG INFO ===")
        
        # Check documents
        try:
            docs_df = self.documents_table.to_pandas()
            print(f"Documents table: {len(docs_df)} rows")
            if not docs_df.empty:
                print("Document titles:")
                for title in docs_df["title"].head():
                    print(f"  - {title}")
        except Exception as e:
            print(f"Error reading documents: {e}")
        
        # Check chunks
        try:
            chunks_df = self.chunks_table.to_pandas()
            print(f"Chunks table: {len(chunks_df)} rows")
            if not chunks_df.empty:
                print("Sample chunk content:")
                for content in chunks_df["content"].head(3):
                    print(f"  - {content[:100]}...")
        except Exception as e:
            print(f"Error reading chunks: {e}")
    
    def test_search_simple(self, query: str):
        """Simple search test without vector similarity"""
        print(f"=== TESTING SIMPLE SEARCH: '{query}' ===")
        
        # Simple text search in documents
        try:
            docs_df = self.documents_table.to_pandas()
            matching_docs = docs_df[
                docs_df["title"].str.contains(query, case=False, na=False) |
                docs_df["summary"].str.contains(query, case=False, na=False) |
                docs_df["combined_text"].str.contains(query, case=False, na=False)
            ]
            print(f"Text-based matches in documents: {len(matching_docs)}")
            
            if not matching_docs.empty:
                for _, row in matching_docs.head().iterrows():
                    print(f"  - {row['title']}: {row['summary'][:100]}...")
        except Exception as e:
            print(f"Error in simple search: {e}")

    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # FIX: Ensure proper vector formatting for query
        query_embedding = self.model.compute_source_embeddings([query])[0]
        query_embedding = self._ensure_vector_format(query_embedding)
        
        # Debug: Check if we have any documents
        try:
            total_docs = len(self.documents_table.to_pandas())
            print(f"Total documents in database: {total_docs}")
            if total_docs == 0:
                print("No documents found in database")
                return []
        except Exception as e:
            print(f"Error checking document count: {e}")
            return []
        
        # Search documents
        try:
            document_results = (self.documents_table
                               .search(query_embedding, vector_column_name="vector")
                               .limit(limit)
                               .to_pandas())
            
            print(f"Document search returned {len(document_results)} results")
            if not document_results.empty:
                print(f"Top result distance: {document_results.iloc[0].get('_distance', 'N/A')}")
        except Exception as e:
            print(f"Error in document search: {e}")
            return []
        
        if document_results.empty:
            return []
        
        # Get chunks from ALL matching documents, not just the top one
        results = []
        for _, doc_row in document_results.iterrows():
            doc_id = doc_row["doc_id"]
            
            # Search chunks within this specific document
            try:
                chunk_results = (self.chunks_table
                                .search(query_embedding, vector_column_name="vector")
                                .where(f"doc_id = '{doc_id}'")
                                .limit(limit)
                                .to_pandas())
                
                doc_chunks = chunk_results["content"].tolist() if not chunk_results.empty else []
                
            except Exception as e:
                print(f"Error searching chunks for doc {doc_id}: {e}")
                # Fallback: get all chunks for this document without vector search
                try:
                    all_chunks = self.chunks_table.to_pandas()
                    doc_chunks = all_chunks[all_chunks["doc_id"] == doc_id]["content"].tolist()
                except Exception as e2:
                    print(f"Error getting chunks fallback: {e2}")
                    doc_chunks = []
            
            results.append({
                "doc_id": doc_row["doc_id"],
                "title": doc_row["title"],
                "summary": doc_row["summary"],
                "chunks": doc_chunks,
                "score": doc_row.get("_distance", 0.0)
            })
        
        print(f"Returning {len(results)} results")
        # print(f"result: {results}")
        return results