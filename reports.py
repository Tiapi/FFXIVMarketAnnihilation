"""
Advanced reporting and analysis of market data
"""
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_reports(csv_file: str = "data/market_analysis.csv"):
    """Generate multiple analysis reports from the market data"""
    
    df = pd.read_csv(csv_file)
    
    print("\n" + "=" * 100)
    print("FFXIV Market Annihilation - Advanced Analysis Report")
    print("=" * 100)
    
    # Report 1: Top profitable items
    print("\n\n1. TOP 20 ITEMS BY TOTAL PROFITABILITY (NQ)")
    print("-" * 100)
    top_profit = df[df['nq_profitability'] > 0].nlargest(20, 'nq_profitability')[
        ['item_id', 'item_name', 'nq_min_listing', 'nq_avg_sale_price', 'nq_margin_per_unit', 'nq_daily_sales', 'nq_profitability']
    ]
    top_profit['nq_profitability'] = top_profit['nq_profitability'].apply(lambda x: f"{x:,.0f}")
    top_profit['nq_daily_sales'] = top_profit['nq_daily_sales'].apply(lambda x: f"{x:.2f}")
    print(top_profit.to_string(index=False))
    
    # Report 2: Highest margin items
    print("\n\n2. TOP 15 ITEMS BY PROFIT MARGIN PER UNIT (NQ)")
    print("-" * 100)
    top_margin = df[df['nq_margin_per_unit'] > 0].nlargest(15, 'nq_margin_per_unit')[
        ['item_id', 'item_name', 'nq_min_listing', 'nq_avg_sale_price', 'nq_margin_per_unit', 'nq_daily_sales']
    ]
    top_margin['nq_margin_per_unit'] = top_margin['nq_margin_per_unit'].apply(lambda x: f"{x:,.0f}")
    top_margin['nq_daily_sales'] = top_margin['nq_daily_sales'].apply(lambda x: f"{x:.2f}")
    print(top_margin.to_string(index=False))
    
    # Report 3: Highest volume items
    print("\n\n3. TOP 15 ITEMS BY DAILY SALES VOLUME (NQ)")
    print("-" * 100)
    top_volume = df[df['nq_daily_sales'] > 0].nlargest(15, 'nq_daily_sales')[
        ['item_id', 'item_name', 'nq_min_listing', 'nq_avg_sale_price', 'nq_margin_per_unit', 'nq_daily_sales', 'nq_profitability']
    ]
    top_volume['nq_daily_sales'] = top_volume['nq_daily_sales'].apply(lambda x: f"{x:.2f}")
    top_volume['nq_profitability'] = top_volume['nq_profitability'].apply(lambda x: f"{x:,.0f}")
    print(top_volume.to_string(index=False))
    
    # Report 4: HQ Analysis
    print("\n\n4. TOP 10 ITEMS BY HQ PROFITABILITY")
    print("-" * 100)
    top_hq = df[df['hq_profitability'] > 0].nlargest(10, 'hq_profitability')[
        ['item_id', 'item_name', 'hq_min_listing', 'hq_avg_sale_price', 'hq_margin_per_unit', 'hq_daily_sales', 'hq_profitability']
    ]
    if len(top_hq) > 0:
        top_hq['hq_profitability'] = top_hq['hq_profitability'].apply(lambda x: f"{x:,.0f}")
        top_hq['hq_daily_sales'] = top_hq['hq_daily_sales'].apply(lambda x: f"{x:.2f}")
        print(top_hq.to_string(index=False))
    else:
        print("No items with positive HQ profitability found.")
    
    # Summary Statistics
    print("\n\n5. SUMMARY STATISTICS")
    print("-" * 100)
    print(f"Total items analyzed: {len(df)}")
    print(f"\nNQ Analysis:")
    print(f"  - Items with positive profitability: {(df['nq_profitability'] > 0).sum()}")
    print(f"  - Total daily profitability (sum): {df['nq_profitability'].sum():,.0f} gil")
    print(f"  - Average daily profitability per item: {df['nq_profitability'].mean():,.0f} gil")
    print(f"  - Median daily profitability: {df['nq_profitability'].median():,.0f} gil")
    print(f"  - Max margin per unit: {df['nq_margin_per_unit'].max():,.0f} gil")
    print(f"  - Max daily sales: {df['nq_daily_sales'].max():.2f} units")
    
    print(f"\nHQ Analysis:")
    hq_profitable = df[df['hq_profitability'] > 0]
    if len(hq_profitable) > 0:
        print(f"  - Items with positive profitability: {len(hq_profitable)}")
        print(f"  - Total daily profitability (sum): {hq_profitable['hq_profitability'].sum():,.0f} gil")
        print(f"  - Average daily profitability per item: {hq_profitable['hq_profitability'].mean():,.0f} gil")
    else:
        print(f"  - No items with positive HQ profitability")
    
    # Report 6: Items with realistic profit/volume ratio
    print("\n\n6. BEST ITEMS FOR STEADY INCOME (High Volume + Positive Margin)")
    print("-" * 100)
    print("(Filtered: min 5 sales/day, margin > 0)")
    steady_income = df[(df['nq_daily_sales'] >= 5) & (df['nq_margin_per_unit'] > 0)].nlargest(15, 'nq_profitability')[
        ['item_id', 'item_name', 'nq_margin_per_unit', 'nq_daily_sales', 'nq_profitability']
    ]
    if len(steady_income) > 0:
        steady_income['nq_profitability'] = steady_income['nq_profitability'].apply(lambda x: f"{x:,.0f}")
        steady_income['nq_daily_sales'] = steady_income['nq_daily_sales'].apply(lambda x: f"{x:.2f}")
        print(steady_income.to_string(index=False))
    else:
        print("No items found matching criteria.")
    
    print("\n" + "=" * 100 + "\n")

if __name__ == "__main__":
    generate_reports()
