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
            self.index = faiss.read_index(str(self.index_path))

        if self.ids_path.exists():
            try:
                self.ids = json.loads(
                    self.ids_path.read_text(encoding="utf-8")
                )
            except Exception:
                self.ids = []

    def save(self):
        faiss.write_index(
            self.index,
            str(self.index_path),
        )

        self.ids_path.write_text(
            json.dumps(self.ids),
            encoding="utf-8",
        )

    def add(
        self,
        quote_id: str,
        embedding: np.ndarray,
    ):
        self.index.add(
            np.asarray(
                [embedding],
                dtype=np.float32,
            )
        )

        self.ids.append(quote_id)

        self.save()

    def search(
        self,
        embedding: np.ndarray,
        k: int = 5,
    ):
        if self.index.ntotal == 0:
            return []

        scores, indices = self.index.search(
            np.asarray(
                [embedding],
                dtype=np.float32,
            ),
            k,
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            results.append(
                (
                    self.ids[idx],
                    float(score),
                )
            )

        return results
