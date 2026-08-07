from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:
    _model = None

    @classmethod
    def model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer(
                "BAAI/bge-m3"
            )
        return cls._model

    def encode_one(
        self,
        text: str,
    ) -> np.ndarray:
        return self.model().encode(
            text,
            normalize_embeddings=True,
        )

    def encode_many(
        self,
        texts: list[str],
    ) -> np.ndarray:
        return self.model().encode(
            texts,
            normalize_embeddings=True,
        )
