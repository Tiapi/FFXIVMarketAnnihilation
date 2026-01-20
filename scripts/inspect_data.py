"""
Deep inspection of API data structure and metrics
"""
from src.universalis_client import UniversalisClient
import json

client = UniversalisClient(datacenter="Chaos")

# Get detailed data for some items - both aggregated and history
item_ids = [49211, 41767, 10756]  # Mix of items with different activity levels

print("=" * 100)
print("1. INSPECTING AGGREGATED DATA (what we currently use)")
print("=" * 100)

agg_response = client.get_aggregated_data(item_ids)
if 'results' in agg_response and len(agg_response['results']) > 0:
    for result in agg_response['results'][:2]:
        print(f"\n\nItem {result['itemId']}:")
        print(json.dumps(result, indent=2, default=str))

print("\n\n" + "=" * 100)
print("2. INSPECTING HISTORY DATA (what we should analyze)")
print("=" * 100)

history_response = client.get_history(item_ids[:1], entries_to_return=50)
print(json.dumps(history_response, indent=2, default=str))

print("\n\n" + "=" * 100)
print("3. ANALYZING THE DIFFERENCE")
print("=" * 100)
print("""
AGGREGATED DATA (/api/v2/aggregated/):
- averageSalePrice: Average price of recent SALES (last 4 days)
- dailySaleVelocity: AVERAGE SALES PER DAY (calculated over last 4 days)
- minListing: LOWEST CURRENT LISTING PRICE (only 1 item usually)
- recentPurchase: Last sale price and timestamp

Issues:
1. Min listing = 1 item (not sustainable volume)
2. Average sale price can be skewed by outliers
3. Daily velocity may not reflect current market (4-day average)
4. Doesn't show actual stack sizes or quantity available

HISTORY DATA (/api/v2/history/):
- entries: Actual individual sales with:
  - pricePerUnit: Exact price paid
  - quantity: Number of items sold
  - timestamp: When it was sold
  - hq: Whether it was high quality
  - buyerName: Who bought it
  - onMannequin: Sold from mannequin?

Benefits:
1. See REAL sales volume with exact quantities
2. Can calculate MEDIAN price (not affected by outliers)
3. Can filter by time period
4. Can track price trends
5. Can see actual availability

Better approach would be:
- Use MEDIAN price from history (50th percentile = not affected by outliers)
- Calculate REALISTIC volume from actual sales transactions
- Consider time decay (recent sales > old sales)
- Analyze price distribution instead of just average
""")
