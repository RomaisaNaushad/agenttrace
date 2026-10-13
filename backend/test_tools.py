from app.tools import list_companies, get_stock_prices, calculator, web_search

print("=== Test 1: list_companies ===")
print(list_companies.invoke({}))

print("\n=== TEST 2: MDB, 2026-09-24 to 2026-09-28====")
print(get_stock_prices.invoke({
    "ticker": "MDB",
    "start_date": "2026-09-24",
    "end_date": "2026-09-28"
}))

print("\n=== TEST 3: bad ticker (should fail politely, not crash) ===")
print(get_stock_prices.invoke({
    "ticker": "FAKE",
    "start_date": "2026-09-24",
    "end_date": "2026-09-28",
}))

print("\n=== TEST 4: percent change MDB 421.40 -> 334.68 ===")
print(calculator.invoke({"operation": "percent_change", "a": 421.40, "b": 334.68}))

print("\n=== TEST 5: divide by zero (should fail politely) ===")
print(calculator.invoke({"operation": "divide", "a": 10, "b": 0}))

print("\n=== TEST 6: unknown operation (should fail politely) ===")
print(calculator.invoke({"operation": "power", "a": 2, "b": 3}))

print("\n=== TEST 7: web search ===")
search = web_search.invoke({"query": "MongoDB stock drop September 2026 Meta CEO"})
for item in search["results"]:
    print(item["title"])
    print("  snippet length:", len(item["snippet"]))