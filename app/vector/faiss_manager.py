from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np


class FaissManager:
    def __init__(
        self,
        dimension: int = 1024,
        index_path: str = "storage/quotes.index",
        ids_path: str = "storage/quotes_ids.json",
    ):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.ids_path = Path(ids_path)

        self.index = faiss.IndexFlatIP(dimension)
        self.ids: list[str] = []

        self.load()

    def load(self):
        if self.index_path.exists() and self.index_path.stat().st_size > 0:
            try:
                loaded = faiss.read_index(str(self.index_path))

                if loaded.d != self.dimension:
                    self.index = faiss.IndexFlatIP(self.dimension)
                else:
                    self.index = loaded
            except Exception:
                self.index = faiss.IndexFlatIP(self.dimension)

        if self.ids_path.exists():
            try:
                loaded_ids = json.loads(
                    self.ids_path.read_text(encoding="utf-8")
                )

                if isinstance(loaded_ids, list):
                    self.ids = [str(item) for item in loaded_ids]
                else:
                    self.ids = []
            except Exception:
                self.ids = []

        if self.index.ntotal != len(self.ids):
            self.index = faiss.IndexFlatIP(self.dimension)
            self.ids = []
            self.save()

    def save(self):
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.ids_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(
            self.index,
            str(self.index_path),
        )

        self.ids_path.write_text(
            json.dumps(self.ids, ensure_ascii=False),
            encoding="utf-8",
        )

    def add(
        self,
        quote_id: str,
        embedding: np.ndarray,
    ):
        vector = np.asarray(
            embedding,
            dtype=np.float32,
        ).reshape(-1)

        if vector.shape[0] != self.dimension:
            raise ValueError(
                f"Embedding dimension {vector.shape[0]} "
                f"does not match FAISS dimension {self.dimension}."
            )

        if quote_id in self.ids:
            self.remove(quote_id)

        self.index.add(
            vector.reshape(1, -1)
        )

        self.ids.append(quote_id)

        self.save()

    def remove(
        self,
        quote_id: str,
    ) -> bool:
        if quote_id not in self.ids:
            return False

        remove_index = self.ids.index(quote_id)

        if self.index.ntotal <= 1:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.ids = []
            self.save()
            return True

        vectors = self.index.reconstruct_n(
            0,
            self.index.ntotal,
        )

        keep_indices = [
            i
            for i in range(len(self.ids))
            if i != remove_index
        ]

        remaining_vectors = vectors[keep_indices]

        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(
            np.asarray(
                remaining_vectors,
                dtype=np.float32,
            )
        )

        self.ids = [
            self.ids[i]
            for i in keep_indices
        ]

        self.save()

        return True

    def search(
        self,
        embedding: np.ndarray,
        k: int = 5,
    ):
        if self.index.ntotal == 0:
            return []

        vector = np.asarray(
            embedding,
            dtype=np.float32,
        ).reshape(-1)

        if vector.shape[0] != self.dimension:
            raise ValueError(
                f"Embedding dimension {vector.shape[0]} "
                f"does not match FAISS dimension {self.dimension}."
            )

        k = min(k, self.index.ntotal)

        scores, indices = self.index.search(
            vector.reshape(1, -1),
            k,
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            if idx >= len(self.ids):
                continue

            results.append(
                (
                    self.ids[idx],
                    float(score),
                )
            )

        return results
