"""
Advanced reporting for v2 analysis with detailed metrics
"""
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_reports_v2(csv_file: str = "data/market_analysis_v2.csv"):
    """Generate detailed analysis reports from v2 data"""
    
    df = pd.read_csv(csv_file)
    
    print("\n" + "=" * 110)
    print("FFXIV Market Annihilation - Advanced Analysis Report v2 (History-Based)")
    print("=" * 110)
    
    # Report 1: Top profitable items
    print("\n\n1. TOP 20 ITEMS BY DAILY PROFITABILITY (Realistic)")
    print("-" * 110)
    top_profit = df[df['profitability'] > 0].nlargest(20, 'profitability')[
        ['item_id', 'item_name', 'buy_price', 'sell_price', 'margin_per_unit', 'daily_volume', 'profitability']
    ].copy()
    
    # Format for display
    top_profit['buy_price'] = top_profit['buy_price'].apply(lambda x: f"{x:,.0f}")
    top_profit['sell_price'] = top_profit['sell_price'].apply(lambda x: f"{x:,.0f}")
    top_profit['margin_per_unit'] = top_profit['margin_per_unit'].apply(lambda x: f"{x:,.0f}")
    top_profit['daily_volume'] = top_profit['daily_volume'].apply(lambda x: f"{x:.1f}")
    top_profit['profitability'] = top_profit['profitability'].apply(lambda x: f"{x:,.0f}")
    
    print(top_profit.to_string(index=False))
    
    # Report 2: Best volume items (most liquid)
    print("\n\n2. TOP 15 MOST LIQUID ITEMS (High Daily Volume)")
    print("-" * 110)
    print("Items that sell consistently every day")
    top_volume = df[df['daily_volume'] > 5].nlargest(15, 'daily_volume')[
        ['item_id', 'item_name', 'buy_price', 'sell_price', 'margin_per_unit', 'daily_volume', 'profitability']
    ].copy()
    
    top_volume['buy_price'] = top_volume['buy_price'].apply(lambda x: f"{x:,.0f}")
    top_volume['sell_price'] = top_volume['sell_price'].apply(lambda x: f"{x:,.0f}")
    top_volume['margin_per_unit'] = top_volume['margin_per_unit'].apply(lambda x: f"{x:,.0f}")
    top_volume['daily_volume'] = top_volume['daily_volume'].apply(lambda x: f"{x:.1f}")
    top_volume['profitability'] = top_volume['profitability'].apply(lambda x: f"{x:,.0f}")
    
    print(top_volume.to_string(index=False))
    
    # Report 3: Highest margin items
    print("\n\n3. TOP 15 ITEMS BY PROFIT MARGIN PER UNIT")
    print("-" * 110)
    top_margin = df[df['margin_per_unit'] > 0].nlargest(15, 'margin_per_unit')[
        ['item_id', 'item_name', 'buy_price', 'sell_price', 'margin_per_unit', 'daily_volume', 'profitability']
    ].copy()
    
    top_margin['buy_price'] = top_margin['buy_price'].apply(lambda x: f"{x:,.0f}")
    top_margin['sell_price'] = top_margin['sell_price'].apply(lambda x: f"{x:,.0f}")
    top_margin['margin_per_unit'] = top_margin['margin_per_unit'].apply(lambda x: f"{x:,.0f}")
    top_margin['daily_volume'] = top_margin['daily_volume'].apply(lambda x: f"{x:.1f}")
    top_margin['profitability'] = top_margin['profitability'].apply(lambda x: f"{x:,.0f}")
    
    print(top_margin.to_string(index=False))
    
    # Report 4: Best for steady income (balanced)
    print("\n\n4. BEST ITEMS FOR STEADY INCOME (Volume > 10/day, Margin > 0)")
    print("-" * 110)
    steady = df[(df['daily_volume'] > 10) & (df['margin_per_unit'] > 0)].nlargest(15, 'profitability')[
        ['item_id', 'item_name', 'buy_price', 'sell_price', 'margin_per_unit', 'daily_volume', 'profitability']
    ].copy()
    
    if len(steady) > 0:
        steady['buy_price'] = steady['buy_price'].apply(lambda x: f"{x:,.0f}")
        steady['sell_price'] = steady['sell_price'].apply(lambda x: f"{x:,.0f}")
        steady['margin_per_unit'] = steady['margin_per_unit'].apply(lambda x: f"{x:,.0f}")
        steady['daily_volume'] = steady['daily_volume'].apply(lambda x: f"{x:.1f}")
        steady['profitability'] = steady['profitability'].apply(lambda x: f"{x:,.0f}")
        print(steady.to_string(index=False))
    else:
        print("No items found matching criteria.")
    
    # Report 5: Price volatility analysis
    print("\n\n5. PRICE VOLATILITY ANALYSIS (Price Range)")
    print("-" * 110)
    print("Items with large price ranges (opportunities for smart trading)")
    
    df['price_range'] = df['price_max'] - df['price_min']
    df['volatility_ratio'] = df['price_range'] / (df['median_price'] + 1)
    
    volatility = df[df['volatility_ratio'] > 0.3].nlargest(15, 'volatility_ratio')[
        ['item_id', 'item_name', 'price_min', 'price_p25', 'median_price', 'price_p75', 'price_max', 'volatility_ratio']
    ].copy()
    
    for col in ['price_min', 'price_p25', 'median_price', 'price_p75', 'price_max']:
        volatility[col] = volatility[col].apply(lambda x: f"{x:,.0f}")
    volatility['volatility_ratio'] = volatility['volatility_ratio'].apply(lambda x: f"{x:.1%}")
    
    print(volatility.to_string(index=False))
    
    # Report 6: Summary Statistics
    print("\n\n6. COMPREHENSIVE STATISTICS")
    print("-" * 110)
    
    print(f"\nTotal items analyzed: {len(df)}")
    print(f"Items with positive profitability: {(df['profitability'] > 0).sum()}")
    print(f"Items with realistic daily volume (>5): {(df['daily_volume'] > 5).sum()}")
    print(f"Items with strong daily volume (>100): {(df['daily_volume'] > 100).sum()}")
    
    print(f"\nProfitability Metrics:")
    print(f"  - Total daily profitability (sum): {df['profitability'].sum():,.0f} gil")
    print(f"  - Average per item: {df['profitability'].mean():,.0f} gil")
    print(f"  - Median per item: {df['profitability'].median():,.0f} gil")
    print(f"  - Max: {df['profitability'].max():,.0f} gil")
    print(f"  - Min: {df['profitability'].min():,.0f} gil")
    
    print(f"\nVolume Metrics:")
    print(f"  - Average daily volume: {df['daily_volume'].mean():.1f} units")
    print(f"  - Median daily volume: {df['daily_volume'].median():.1f} units")
    print(f"  - Max daily volume: {df['daily_volume'].max():.1f} units")
    print(f"  - Total historical sales: {df['total_quantity_in_history'].sum():,.0f} units")
    
    print(f"\nMargin Metrics:")
    print(f"  - Average margin per unit: {df['margin_per_unit'].mean():,.0f} gil")
    print(f"  - Median margin per unit: {df['margin_per_unit'].median():,.0f} gil")
    print(f"  - Max margin per unit: {df['margin_per_unit'].max():,.0f} gil")
    
    print(f"\nData Quality:")
    print(f"  - Average transactions per item: {df['total_sales_in_history'].mean():.0f}")
    print(f"  - Average history timespan: {df['days_span'].mean():.1f} days")
    
    # Report 7: Risk/Reward Matrix
    print("\n\n7. RISK/REWARD ANALYSIS")
    print("-" * 110)
    print("Classification by risk level (based on volume consistency)")
    
    high_volume = df[df['daily_volume'] > 100]
    medium_volume = df[(df['daily_volume'] > 10) & (df['daily_volume'] <= 100)]
    low_volume = df[df['daily_volume'] <= 10]
    
    print(f"\nHIGH VOLUME (>100 units/day): {len(high_volume)} items")
    if len(high_volume) > 0:
        print(f"  - Average profitability: {high_volume['profitability'].mean():,.0f} gil/day")
        print(f"  - Total profitability: {high_volume['profitability'].sum():,.0f} gil/day")
        print(f"  - Examples: {', '.join(high_volume.nlargest(3, 'profitability')['item_name'].tolist())}")
    
    print(f"\nMEDIUM VOLUME (10-100 units/day): {len(medium_volume)} items")
    if len(medium_volume) > 0:
        print(f"  - Average profitability: {medium_volume['profitability'].mean():,.0f} gil/day")
        print(f"  - Total profitability: {medium_volume['profitability'].sum():,.0f} gil/day")
        print(f"  - Examples: {', '.join(medium_volume.nlargest(3, 'profitability')['item_name'].tolist())}")
    
    print(f"\nLOW VOLUME (<10 units/day): {len(low_volume)} items")
    if len(low_volume) > 0:
        print(f"  - Average profitability: {low_volume['profitability'].mean():,.0f} gil/day")
        print(f"  - Total profitability: {low_volume['profitability'].sum():,.0f} gil/day")
        print(f"  - Examples: {', '.join(low_volume.nlargest(3, 'profitability')['item_name'].tolist())}")
    
    print("\n" + "=" * 110 + "\n")

if __name__ == "__main__":
    generate_reports_v2()
