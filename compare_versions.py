"""
Comparison between v1 (aggregated data) and v2 (history-based) analysis
"""
import pandas as pd

print("\n" + "=" * 110)
print("COMPARISON: Analysis v1 (Aggregated) vs v2 (History-Based)")
print("=" * 110)

# Load both datasets
v1_df = pd.read_csv('data/market_analysis.csv')
v2_df = pd.read_csv('data/market_analysis_v2.csv')

print("\n\n1. DATA QUALITY & COVERAGE")
print("-" * 110)
print(f"v1 (Aggregated): {len(v1_df)} items analyzed")
print(f"v2 (History):    {len(v2_df)} items analyzed")
print(f"Overlap (items in both): {len(set(v1_df['item_id']).intersection(set(v2_df['item_id'])))} items")

print("\n\n2. METHODOLOGY DIFFERENCES")
print("-" * 110)
print("""
v1 (Aggregated API):
  - Uses averageSalePrice (can be skewed by outliers)
  - Uses minListing (only 1 item, not sustainable)
  - Uses dailySaleVelocity (4-day average, may not reflect current market)
  - Problem: Crescent Moon Nightgown shows 47M profitability (unrealistic)

v2 (Historical Data):
  - Uses MEDIAN price (resistant to outliers)
  - Uses percentile-based pricing (25th percentile for buying, 75th for selling)
  - Calculates realistic volume from actual transactions
  - Accounts for days spanned in history
  - Much more realistic and actionable
""")

print("\n3. KEY METRICS COMPARISON")
print("-" * 110)

# Get common items for comparison
common_items = set(v1_df['item_id']).intersection(set(v2_df['item_id']))
v1_common = v1_df[v1_df['item_id'].isin(common_items)].set_index('item_id')
v2_common = v2_df[v2_df['item_id'].isin(common_items)].set_index('item_id')

print(f"\nProfitability (first 10 common items):")
print("Item ID | Item Name | v1 Profitability | v2 Profitability | Difference")
print("-" * 110)

for item_id in list(common_items)[:10]:
    v1_prof = v1_common.loc[item_id, 'nq_profitability'] if 'nq_profitability' in v1_common.columns else 0
    v2_prof = v2_common.loc[item_id, 'profitability']
    v1_name = v1_common.loc[item_id, 'item_name']
    
    ratio = v2_prof / v1_prof if v1_prof != 0 else 0
    print(f"{item_id:7d} | {v1_name:30s} | {v1_prof:17,.0f} | {v2_prof:17,.0f} | {ratio:8.2%}")

print("\n\n4. VOLUME ANALYSIS")
print("-" * 110)
print(f"\nv1 Average daily sales across items: {v1_common['nq_daily_sales'].mean():.1f} units/day")
print(f"v2 Average daily volume across items: {v2_common['daily_volume'].mean():.1f} units/day")

print("\nv1 shows extremely high volume numbers (383,877 Ice Crystals/day reported)")
print("v2 shows more realistic numbers (84,492 Ice Crystals/day)")
print("\nReality check: Ice Crystals are gathered items, selling thousands per day is plausible")
print("but v1's dailySaleVelocity appears to be cumulative across entire datacenter,")
print("not per-world or realistic purchase volume")

print("\n\n5. PROFITABILITY DISTRIBUTION")
print("-" * 110)

v1_positive = (v1_df['nq_profitability'] > 0).sum()
v2_positive = (v2_df['profitability'] > 0).sum()

print(f"\nv1 Items with positive profitability: {v1_positive}/{len(v1_df)} ({100*v1_positive/len(v1_df):.1f}%)")
print(f"v2 Items with positive profitability: {v2_positive}/{len(v2_df)} ({100*v2_positive/len(v2_df):.1f}%)")

print(f"\nv1 Total daily profitability: {v1_df['nq_profitability'].sum():,.0f} gil")
print(f"v2 Total daily profitability: {v2_df['profitability'].sum():,.0f} gil")

print(f"\nv1 Average per item: {v1_df['nq_profitability'].mean():,.0f} gil")
print(f"v2 Average per item: {v2_df['profitability'].mean():,.0f} gil")

print("\n\n6. TOP 5 ITEMS COMPARISON")
print("-" * 110)
print("\nv1 Top 5 by Profitability:")
v1_top = v1_df.nlargest(5, 'nq_profitability')[['item_id', 'item_name', 'nq_profitability']]
for idx, row in v1_top.iterrows():
    print(f"  {row['item_id']:5d} - {row['item_name']:30s}: {row['nq_profitability']:15,.0f} gil")

print("\nv2 Top 5 by Profitability:")
v2_top = v2_df.nlargest(5, 'profitability')[['item_id', 'item_name', 'profitability']]
for idx, row in v2_top.iterrows():
    print(f"  {row['item_id']:5d} - {row['item_name']:30s}: {row['profitability']:15,.0f} gil")

print("\n\n7. VERDICT & RECOMMENDATIONS")
print("-" * 110)
print("""
✓ v2 (History-Based) is MORE RELIABLE because:
  1. Uses MEDIAN prices (not affected by one-time sales to collectors)
  2. Uses PERCENTILE-based margins (realistic buying/selling)
  3. Shows ACTUAL transaction data with quantities
  4. Accounts for price volatility and distribution
  5. Smaller but more realistic profitability numbers
  6. Better suited for actual trading decisions

✗ v1 (Aggregated) issues:
  1. Average price can be skewed by outliers
  2. Min listing is only 1 item (not sustainable)
  3. Daily velocity appears to be datacenter-wide cumulative
  4. Doesn't show price distribution
  5. Overstates profitability significantly

RECOMMENDATION:
→ Use v2 for investment/trading decisions
→ v1 can be useful for quick market overview
→ Consider combining both for complete picture
→ For next phase: add crafting cost analysis to v2
""")

print("\n" + "=" * 110 + "\n")
