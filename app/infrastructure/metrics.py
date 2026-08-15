from prometheus_client import Counter

transactions_created_total = Counter(
    "pocketledger_transactions_created_total", "Total transactions created"
)
summaries_requested_total = Counter(
    "pocketledger_summaries_requested_total",
    "Total financial summaries requested",
)
