import os
import pickle
import numpy as np
import requests
import faiss

class PersistentFaissStore:
    def __init__(self):
        # 1. Paths for permanent hard drive storage
        self.index_file = os.path.join(os.getcwd(), "memory", "faiss_index.bin")
        self.docs_file = os.path.join(os.getcwd(), "memory", "faiss_docs.pkl")
        
        # 2. Ollama configuration
        self.ollama_url = "http://localhost:11434/api/embeddings"
        self.embed_model = "nomic-embed-text"
        self.dimension = 768 # The exact math dimension size of nomic-embed-text
        
        self.documents = []
        self._load_memory()

    def _load_memory(self):
        """Loads the FAISS index and text metadata from disk."""
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        
        # Load the text documents metadata
        if os.path.exists(self.docs_file):
            with open(self.docs_file, 'rb') as f:
                self.documents = pickle.load(f)
        
        # Load the high-speed FAISS math index
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
        else:
            # If no memory exists, initialize a blank L2 distance FAISS index
            self.index = faiss.IndexFlatL2(self.dimension)

    def _save_memory(self):
        """Saves both the text and the FAISS tree to the hard drive."""
        with open(self.docs_file, 'wb') as f:
            pickle.dump(self.documents, f)
            
        faiss.write_index(self.index, self.index_file)

    def _get_embedding(self, text):
        """Asks Ollama to convert text into a semantic math vector."""
        payload = {"model": self.embed_model, "prompt": text}
        try:
            response = requests.post(self.ollama_url, json=payload).json()
            return response.get("embedding", [])
        except Exception as e:
            print(f"[!] Ollama Embedding Error: {e}")
            return []

    def store_memory(self, text):
        print(f"[*] FAISS STORE: Saving permanent neural memory -> {text[:50]}...")
        embedding = self._get_embedding(text)
        
        if embedding:
            # FAISS requires strictly typed float32 numpy arrays for max speed
            vector = np.array([embedding], dtype=np.float32)
            
            self.index.add(vector)          # Add to FAISS math tree
            self.documents.append(text)     # Add text to list
            self._save_memory()             # Save immediately to disk

    def search_memory(self, query, k=2):
        print(f"[*] FAISS STORE: Executing high-speed neural match -> {query}")
        
        if self.index.ntotal == 0:
            return {"documents": [["No past event memories found. Starting fresh."]]}
            
        query_vec = self._get_embedding(query)
        if not query_vec:
            return {"documents": [[self.documents[-1]]]}
            
        vector = np.array([query_vec], dtype=np.float32)
        
        # FAISS returns distances and the exact indices of the matches
        distances, indices = self.index.search(vector, min(k, self.index.ntotal))
        
        # Map the math indices back to human-readable text documents
        results = [self.documents[i] for i in indices[0] if i != -1]
        
        if not results:
             return {"documents": [["No highly relevant past events found."]]}
        return {"documents": [results]}

# Export singleton instance functions (Keeps the orchestrator logic intact!)
_store = PersistentFaissStore()
store_memory = _store.store_memory
search_memory = _store.search_memory