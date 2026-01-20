"""
Main script for market analysis v2 (history-based)
"""
import sys
import logging
from src.analyzer_v2 import MarketAnalyzerV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run the improved market analysis"""
    analyzer = MarketAnalyzerV2(datacenter="Chaos")
    
    print("=" * 80)
    print("FFXIV Market Annihilation - Market Analysis v2 (History-Based)")
    print("=" * 80)
    print(f"Datacenter: Chaos")
    print(f"Analysis: Using historical sales data")
    print(f"Metrics: Median price, realistic volume, percentile-based margins")
    print()
    
    try:
        df = analyzer.analyze_and_export(
            output_file="data/market_analysis_v2.csv",
            num_items=200
        )
        
        print("\n" + "=" * 80)
        print(f"Total items analyzed: {len(df)}")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
