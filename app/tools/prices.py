# app/tools/prices.py
"""
Price lookup tool for the offline RAG agent.

- Retrieves prices for financial instruments from a stub JSON file (prices_stub/prices.json).
- Designed to be called from the agent when queries contain keywords like "price".
"""
import json
import os

PRICES_FILE = os.path.join(os.path.dirname(__file__), "../../prices_stub/prices.json")

def get_price(query):
    """
    Simple price lookup tool.
    Looks for keywords in the query and returns the price from prices.json
    """
    try:
        with open(PRICES_FILE, "r", encoding="utf-8") as f:
            prices_data = json.load(f)
    except FileNotFoundError:
        return "Prices file not found."
    except json.JSONDecodeError:
        return "Prices file is invalid."

    # Lowercase query for simple keyword matching
    query_lower = query.lower()

    # Iterate over all keys in prices.json and return first match
    for item_name, price in prices_data.items():
        if item_name.lower() in query_lower:
            return f"{item_name}: {price}"

    return "No matching price found for your query."
