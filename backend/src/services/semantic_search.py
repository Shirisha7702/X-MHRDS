import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import db

class CaseSearchEngine:
    """Lightweight text search engine using TF-IDF cosine similarity to match past resolutions."""
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.cases = db.get_all_cases()
        self.corpus = [case["post"] for case in self.cases]
        self.X_corpus = self.vectorizer.fit_transform(self.corpus)
        
    def find_similar_cases(self, query, top_k=2):
        """Finds the most semantically similar past cases matching the input query."""
        if not query.strip():
            return []
            
        X_query = self.vectorizer.transform([query])
        similarities = cosine_similarity(X_query, self.X_corpus).flatten()
        
        # Sort indices by similarity descending
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        matches = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.05: # Only return cases with some minimal match
                case_data = self.cases[idx].copy()
                case_data["similarity_score"] = score
                matches.append(case_data)
                
        return matches

if __name__ == "__main__":
    searcher = CaseSearchEngine()
    q = "feeling sad and alone, nobody cares about me"
    print(f"Query: {q}")
    results = searcher.find_similar_cases(q, top_k=2)
    for r in results:
        print(f"\nMatch ID: {r['id']} (Score: {r['similarity_score']:.4f})")
        print(f"Post: {r['post']}")
        print(f"Resolution: {r['resolution']}")
