from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class LocalVectorStore:
    def __init__(self):
        self.documents = []
        self.vectorizer = TfidfVectorizer()
        self.vectors = None

    def store_memory(self, text):
        print(f"[*] TF-IDF VECTOR STORE: Saving memory -> {text[:50]}...")
        self.documents.append(text)
        self.vectors = self.vectorizer.fit_transform(self.documents)

    def search_memory(self, query, k=2):
        print(f"[*] TF-IDF VECTOR STORE: Searching for -> {query}")
        if not self.documents:
            return {"documents": [["No past event memories found. Starting fresh."]]}
        
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.vectors).flatten()
        
        # Get top k indices mathematically
        top_indices = np.argsort(similarities)[::-1][:k]
        results = [self.documents[i] for i in top_indices if similarities[i] > 0]
        
        if not results:
             return {"documents": [[self.documents[-1]]]}
        return {"documents": [results]}

# Export singleton instance functions
_store = LocalVectorStore()
store_memory = _store.store_memory
search_memory = _store.search_memory