"""
Debug: inspect raw API response
"""
from src.universalis_client import UniversalisClient
import json

client = UniversalisClient(datacenter="Chaos")

# Get data for a few items
item_ids = [10756, 49251, 3203]  # Some items from our analysis
print(f"Fetching raw data for items: {item_ids}")
print("=" * 80)

response = client.get_aggregated_data(item_ids)

# Pretty print the first result
if 'results' in response and len(response['results']) > 0:
    first_result = response['results'][0]
    print(f"\nFirst result (Item {first_result['itemId']}):")
    print(json.dumps(first_result, indent=2))
