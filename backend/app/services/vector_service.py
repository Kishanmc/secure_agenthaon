import os
import math
import numpy as np
from typing import List, Dict, Any, Tuple
from app.config import settings

class VectorService:
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.use_fallback = True
        
        # Simple fallback memory DB: list of tuples (id, text, metadata, vector)
        self.fallback_db: List[Dict[str, Any]] = []
        
        # Initialize chroma if possible
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_DIR,
                settings=ChromaSettings(allow_reset=True)
            )
            self.collection = self.chroma_client.get_or_create_collection("security_kb")
            self.use_fallback = False
            print("ChromaDB initialized successfully.")
        except Exception as e:
            print(f"ChromaDB not available: {e}. Falling back to internal simple vector DB.")
            
        # Seed some default security knowledge base documents
        self.seed_knowledge_base()

    def _get_dummy_embedding(self, text: str) -> List[float]:
        """
        Creates a mock tf-idf/hash based embedding vector (size 128)
        so we can perform cosine similarity matching locally without a remote LLM API.
        """
        vector = np.zeros(128)
        text = text.lower()
        words = text.split()
        
        # Populate values based on hashes of characters/words
        for i, word in enumerate(words):
            char_sum = sum(ord(c) for c in word)
            idx = char_sum % 128
            vector[idx] += 1.0 + (i * 0.1)
            
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector.tolist()

    def seed_knowledge_base(self):
        kb_docs = [
            {
                "id": "kb_sqli",
                "text": "SQL Injection vulnerability occurs when untrusted input is concatenated directly into SQL strings without parametrization. Prevention involves using prepared statements, parameterized queries, or using object relational mapping tools (ORMs) like SQLAlchemy.",
                "metadata": {"cwe": "CWE-89", "category": "Injection"}
            },
            {
                "id": "kb_xss",
                "text": "Cross-Site Scripting (XSS) happens when an application includes untrusted data in a web page without proper validation or escaping. Prevent by escaping HTML, inputs, and attributes, sanitizing client side rendering templates, and using a Content Security Policy (CSP).",
                "metadata": {"cwe": "CWE-79", "category": "Injection"}
            },
            {
                "id": "kb_ssrf",
                "text": "Server-Side Request Forgery (SSRF) allows an attacker to abuse functionality on the server to make requests to internal or external resources. Prevent by implementing strict destination whitelists, validating URL formats, and restricting socket creation to localhost or private IPs.",
                "metadata": {"cwe": "CWE-918", "category": "Broken Access Control"}
            },
            {
                "id": "kb_secrets",
                "text": "Leaking secrets involves storing sensitive values like API tokens, database connection strings, passwords, or private SSH keys directly in source code. Remediation requires revoking the leaked token immediately, auditing logs, and loading values from server environment variables or vault secret managers.",
                "metadata": {"cwe": "CWE-798", "category": "Cryptographic Failures"}
            },
            {
                "id": "kb_command_injection",
                "text": "Command Injection happens when an application executes arbitrary shell commands based on user input. To fix, avoid shell=True, use list-based subprocess arrays, sanitize argument parameters, or use programming language API libraries instead of operating system shell commands.",
                "metadata": {"cwe": "CWE-78", "category": "Injection"}
            }
        ]
        
        for doc in kb_docs:
            self.add_document(doc["id"], doc["text"], doc["metadata"])

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        if not self.use_fallback and self.collection:
            try:
                # Add using chroma
                self.collection.upsert(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[metadata],
                    embeddings=[self._get_dummy_embedding(text)]
                )
                return
            except Exception as e:
                print(f"Chroma add_document failed: {e}. Switching to fallback.")
                self.use_fallback = True
                
        # Fallback in-memory add
        # Check if already exists, update it
        for idx, item in enumerate(self.fallback_db):
            if item["id"] == doc_id:
                self.fallback_db[idx] = {
                    "id": doc_id,
                    "text": text,
                    "metadata": metadata,
                    "vector": self._get_dummy_embedding(text)
                }
                return
                
        self.fallback_db.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata,
            "vector": self._get_dummy_embedding(text)
        })

    def query_similarity(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Performs Cosine Similarity search over cached security database docs.
        """
        query_vector = self._get_dummy_embedding(query_text)
        
        if not self.use_fallback and self.collection:
            try:
                res = self.collection.query(
                    query_embeddings=[query_vector],
                    n_results=n_results
                )
                
                hits = []
                ids = res.get("ids", [[]])[0]
                docs = res.get("documents", [[]])[0]
                metadatas = res.get("metadatas", [[]])[0]
                distances = res.get("distances", [[]])[0]
                
                for i in range(len(ids)):
                    hits.append({
                        "id": ids[i],
                        "text": docs[i],
                        "metadata": metadatas[i] if metadatas else {},
                        "score": 1.0 - (distances[i] if i < len(distances) else 0.5) # distance is usually cosine distance
                    })
                return hits
            except Exception as e:
                print(f"Chroma query failed: {e}. Using fallback DB.")
                
        # Fallback Vector DB Search (Cosine Similarity)
        hits = []
        q_vec = np.array(query_vector)
        
        for item in self.fallback_db:
            db_vec = np.array(item["vector"])
            # Calculate cosine similarity
            dot_product = np.dot(q_vec, db_vec)
            norm_q = np.linalg.norm(q_vec)
            norm_db = np.linalg.norm(db_vec)
            
            similarity = 0.0
            if norm_q > 0 and norm_db > 0:
                similarity = dot_product / (norm_q * norm_db)
                
            hits.append({
                "id": item["id"],
                "text": item["text"],
                "metadata": item["metadata"],
                "score": float(similarity)
            })
            
        # Sort by score descending
        hits.sort(key=lambda x: x["score"], reverse=True)
        return hits[:n_results]
