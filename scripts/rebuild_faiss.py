from __future__ import annotations

import json

from app.ai.embedding_service import EmbeddingService
from app.core.config import Settings
from app.database.base import create_engine_from_settings
from app.database.session import build_session_factory
from app.repositories.quote_repository import QuoteRepository
from app.vector.faiss_manager import FaissManager


def main():
    settings = Settings()

    engine = create_engine_from_settings(settings)
    session_factory = build_session_factory(engine)

    repository = QuoteRepository(
        session_factory=session_factory
    )

    quotes = repository.list_all(
        limit=100000,
        offset=0,
    )

    print(f"Quotes found: {len(quotes)}")

    embedding_service = EmbeddingService()

    faiss_manager = FaissManager()

    faiss_manager.index = __import__("faiss").IndexFlatIP(
        faiss_manager.dimension
    )
    faiss_manager.ids = []

    indexed = 0
    failed = 0

    for quote in quotes:
        try:
            vector = embedding_service.encode_one(
                quote.text
            )

            quote.embedding = json.dumps(
                vector.tolist()
            )

            faiss_manager.add(
                quote.id,
                vector,
            )

            indexed += 1

            print(
                f"[OK] {indexed}: {quote.id}"
            )

        except Exception as exc:
            failed += 1

            print(
                f"[FAILED] {quote.id}: {exc}"
            )

    print()
    print("================================")
    print("FAISS REBUILD COMPLETE")
    print("================================")
    print(f"Quotes found : {len(quotes)}")
    print(f"Indexed      : {indexed}")
    print(f"Failed       : {failed}")
    print(f"FAISS vectors: {faiss_manager.index.ntotal}")
    print(f"FAISS ids    : {len(faiss_manager.ids)}")


if __name__ == "__main__":
    main()
