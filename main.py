"""
Main script for FFXIV Market Annihilation analysis
"""
import sys
import logging
from src.analyzer import MarketAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run the market analysis"""
    analyzer = MarketAnalyzer(datacenter="Chaos")
    
    # Run analysis: 100 random items + 100 top sellers
    print("=" * 60)
    print("FFXIV Market Annihilation - Market Analysis")
    print("=" * 60)
    print(f"Datacenter: Chaos")
    print(f"Analysis: 100 random items + 100 top sellers")
    print()
    
    try:
        df = analyzer.analyze_and_export(
            output_file="data/market_analysis.csv",
            num_random=100,
            num_top_sellers=100
        )
        
        print("\n" + "=" * 60)
        print(f"Total items analyzed: {len(df)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
