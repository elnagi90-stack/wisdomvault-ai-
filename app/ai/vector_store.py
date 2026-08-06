import faiss
import numpy as np


class VectorStore:
    def __init__(self, dimension: int = 384):
        self.index = faiss.IndexFlatIP(dimension)
        self.ids = []

    def add(self, vector, item_id):
        vector = np.array([vector]).astype("float32")
        self.index.add(vector)
        self.ids.append(item_id)

    def search(self, vector, k=5):
        vector = np.array([vector]).astype("float32")

        scores, indexes = self.index.search(vector, k)

        results = []

        for score, idx in zip(scores[0], indexes[0], strict=False):
            if idx == -1:
                continue

            results.append(
                {
                    "id": self.ids[idx],
                    "score": float(score),
                }
            )

        return results
