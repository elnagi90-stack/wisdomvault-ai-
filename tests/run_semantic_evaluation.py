from app.ai.semantic_search_service import SemanticSearchService
from app.core.config import Settings
from app.database.base import create_engine_from_settings
from app.database.session import build_session_factory
from app.repositories.quote_repository import QuoteRepository


CASES = [
    (
        "success and achieving goals",
        "870e6f59-02fb-44be-aaf3-b4b9fd2ac751",
    ),
    (
        "happiness and contentment",
        "3467b25a-e86d-477b-9c90-d9b26b242d9f",
    ),
    (
        "money and wealth",
        "f371622d-39ea-480a-a663-1fe47ba712a1",
    ),
    (
        "what makes a successful life",
        "f371622d-39ea-480a-a663-1fe47ba712a1",
    ),
    (
        "getting what you want",
        "870e6f59-02fb-44be-aaf3-b4b9fd2ac751",
    ),
    (
        "being satisfied with what you have",
        "3467b25a-e86d-477b-9c90-d9b26b242d9f",
    ),
    (
        "true meaning of success",
        "f371622d-39ea-480a-a663-1fe47ba712a1",
    ),
    (
        "wealth is not the most important thing in life",
        "f371622d-39ea-480a-a663-1fe47ba712a1",
    ),
    (
        "happiness comes from contentment",
        "3467b25a-e86d-477b-9c90-d9b26b242d9f",
    ),
    (
        "success is more than money",
        "f371622d-39ea-480a-a663-1fe47ba712a1",
    ),
    (
        "wealth and financial success",
        "f371622d-39ea-480a-a663-1fe47ba712a1",
    ),
    (
        "having money does not define a good life",
        "f371622d-39ea-480a-a663-1fe47ba712a1",
    ),
    (
        "material possessions versus happiness",
        "3467b25a-e86d-477b-9c90-d9b26b242d9f",
    ),
    (
        "desiring things versus being content",
        "3467b25a-e86d-477b-9c90-d9b26b242d9f",
    ),
    (
        "achieving your desires",
        "870e6f59-02fb-44be-aaf3-b4b9fd2ac751",
    ),
    (
        "getting the things you desire",
        "870e6f59-02fb-44be-aaf3-b4b9fd2ac751",
    ),
]


def build_service():
    settings = Settings()
    engine = create_engine_from_settings(settings)
    session_factory = build_session_factory(engine)
    repository = QuoteRepository(session_factory=session_factory)
    return SemanticSearchService(repository=repository)


def main():
    service = build_service()

    total = len(CASES)
    top1 = 0
    top3 = 0
    reciprocal_rank_sum = 0.0
    score_gaps = []

    print("=== SEMANTIC SEARCH EVALUATION ===")
    print(f"CASES: {total}")

    for number, (query, expected_id) in enumerate(CASES, 1):
        results = service.search(query, k=3)
        ids = [item["quote"].id for item in results]

        expected_rank = None

        for rank, item in enumerate(results, 1):
            if item["quote"].id == expected_id:
                expected_rank = rank
                break

        top1_hit = bool(ids) and ids[0] == expected_id
        top3_hit = expected_id in ids

        if top1_hit:
            top1 += 1

        if top3_hit:
            top3 += 1

        if expected_rank is not None:
            reciprocal_rank_sum += 1.0 / expected_rank

        top1_score = results[0]["score"] if results else None
        expected_score = None

        for item in results:
            if item["quote"].id == expected_id:
                expected_score = item["score"]
                break

        score_gap = None

        if top1_score is not None and expected_score is not None:
            score_gap = top1_score - expected_score

        if score_gap is not None:
            score_gaps.append(score_gap)

        print()
        print(f"{number}. QUERY: {query}")
        print(f"   EXPECTED: {expected_id}")

        for rank, item in enumerate(results, 1):
            print(
                f"   {rank}. "
                f"SCORE={item['score']:.4f} | "
                f"ID={item['quote'].id} | "
                f"TEXT={item['quote'].text}"
            )

        print(
            f"   EXPECTED_RANK="
            f"{expected_rank if expected_rank is not None else 'MISS'} | "
            f"TOP1={'PASS' if top1_hit else 'FAIL'} | "
            f"TOP3={'PASS' if top3_hit else 'FAIL'}"
        )

        if score_gap is not None:
            print(f"   SCORE_GAP={score_gap:.4f}")

    mrr = reciprocal_rank_sum / total
    avg_score_gap = (
        sum(score_gaps) / len(score_gaps)
        if score_gaps
        else 0.0
    )

    print()
    print("=== SUMMARY ===")
    print(f"TOP1: {top1}/{total} = {top1 / total:.2%}")
    print(f"TOP3: {top3}/{total} = {top3 / total:.2%}")
    print(f"MRR:  {mrr:.4f}")
    print(f"AVG_SCORE_GAP: {avg_score_gap:.4f}")

    print()
    print("=== HARD CASES ===")

    for query, expected_id in CASES:
        results = service.search(query, k=3)
        ids = [item["quote"].id for item in results]

        expected_rank = None

        for rank, item in enumerate(results, 1):
            if item["quote"].id == expected_id:
                expected_rank = rank
                break

        if expected_rank != 1:
            top1_id = results[0]["quote"].id if results else None
            top1_score = results[0]["score"] if results else None

            expected_score = None

            for item in results:
                if item["quote"].id == expected_id:
                    expected_score = item["score"]
                    break

            score_gap = None

            if top1_score is not None and expected_score is not None:
                score_gap = top1_score - expected_score

            print()
            print(f"QUERY: {query}")
            print(f"EXPECTED: {expected_id}")
            print(f"EXPECTED_RANK: {expected_rank}")
            print(f"TOP1_ID: {top1_id}")
            print(
                f"TOP1_SCORE: "
                f"{top1_score if top1_score is not None else 'None'}"
            )
            print(
                f"EXPECTED_SCORE: "
                f"{expected_score if expected_score is not None else 'None'}"
            )
            print(
                f"SCORE_GAP: "
                f"{score_gap if score_gap is not None else 'None'}"
            )


if __name__ == "__main__":
    main()
