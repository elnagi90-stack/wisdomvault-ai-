from app.services.web_search.service import WebSearchService

service = WebSearchService()

results = service.search(
    "Dale Carnegie quotes happiness success",
    limit=5,
)

print()
print("RESULTS:", len(results))
print("=" * 70)

for index, result in enumerate(results, start=1):
    print(f"\n[{index}]")
    print("TEXT   :", result.text)
    print("SOURCE :", result.source)
    print("URL    :", result.url)
