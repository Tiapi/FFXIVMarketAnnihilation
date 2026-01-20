"""
Market analysis v2 using historical data instead of aggregated data
This provides more realistic profitability calculations
"""
import statistics
from typing import List, Dict, Any, Tuple
import logging
import pandas as pd
from datetime import datetime, timedelta
import time
from src.universalis_client import UniversalisClient
from src.item_mapper import fetch_item_names_batch
from src.craft_cost import estimate_craft_cost

logger = logging.getLogger(__name__)

class MarketAnalyzerV2:
    """
    Improved market analyzer using historical sales data
    
    Key improvements:
    1. Uses MEDIAN price instead of AVERAGE (resistant to outliers)
    2. Calculates realistic volume from actual transactions
    3. Analyzes true buying/selling scenarios
    4. Shows price distribution instead of just one number
    """
    
    def __init__(self, datacenter: str = "Chaos"):
        self.client = UniversalisClient(datacenter)
        self.datacenter = datacenter
    
    def get_test_items(self, num_items: int = 200) -> List[int]:
        """
        Get active items from the market
        """
        logger.info(f"Selecting {num_items} active items from the market...")
        
        all_items_set = set()
        
        try:
            url = f"{self.client.BASE_URL}/extra/stats/most-recently-updated"
            params = {"dcName": self.datacenter, "entries": 300}
            
            import requests
            self.client._rate_limit()
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            recent_data = response.json()
            if 'items' in recent_data and recent_data['items']:
                for item in recent_data['items']:
                    all_items_set.add(item['itemID'])
                logger.info(f"Found {len(all_items_set)} recently updated items on {self.datacenter}")
        
        except Exception as e:
            logger.warning(f"Could not fetch recently updated items: {e}")
        
        active_items = list(all_items_set)
        return active_items[:num_items]
    
    def analyze_item_history(self, item_id: int, history_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single item's history to extract realistic metrics based on actual sales.

        Pricing model (to avoid overvalued listings):
        - buy_price: 25th percentile of recent sales (what we realistically pay to acquire)
        - sell_price: median of recent sales (what buyers actually pay)
        We also compute p75 for reference but do not assume we can sell at p75 by default.

        Volume model:
        - daily_volume: average quantity sold per day from actual sales timestamps
        """
        
        try:
            entries = history_data.get('entries', [])
            
            if not entries:
                return None
            
            # Extract all prices and quantities from history
            prices = []
            prices_recent = []  # last 3 days for a fresher sell-price estimate
            total_quantity = 0
            latest_ts = history_data.get('lastUploadTime', 0) / 1000  # seconds
            three_days_ago = latest_ts - 3 * 86400 if latest_ts else None
            
            for entry in entries:
                if entry.get('hq'):  # Skip HQ for now, focus on NQ
                    continue
                
                price = entry.get('pricePerUnit', 0)
                quantity = entry.get('quantity', 0)
                timestamp = entry.get('timestamp', 0)

                if price > 0 and quantity > 0:
                    prices.append(price)
                    total_quantity += quantity
                    if three_days_ago and timestamp >= three_days_ago:
                        prices_recent.append(price)
            
            if not prices:
                return None
            
            # Get timestamps to calculate days (span of observed history)
            timestamps = [e.get('timestamp', 0) for e in entries if e.get('timestamp', 0) > 0]
            if timestamps:
                oldest_timestamp = min(timestamps)
                latest_timestamp = max(timestamps)
                days_span = max((latest_timestamp - oldest_timestamp) / 86400, 1)  # At least 1 day
            else:
                days_span = 1
            
            # Calculate price metrics (using sales, not listings)
            prices_sorted = sorted(prices)

            # Percentiles
            if len(prices_sorted) > 3:
                q1, q2, q3 = statistics.quantiles(prices_sorted, n=4)
            else:
                q1 = min(prices_sorted)
                q2 = statistics.median(prices_sorted)
                q3 = max(prices_sorted)

            # Recent median (last 3 days) to avoid stale/overpriced sells
            if len(prices_recent) >= 5:
                sell_price = statistics.median(prices_recent)
            else:
                sell_price = q2

            buy_price = q1
            median_price = q2
            p75_price = q3
            
            daily_volume = total_quantity / days_span
            
            result = {
                'item_id': item_id,
                'buy_price': buy_price,  # 25th percentile of sales
                'median_price': median_price,  # Overall median
                'sell_price': sell_price,  # Median of last 3 days if available, else overall median
                'sell_price_p75': p75_price,
                'margin_per_unit': sell_price - buy_price,
                'daily_volume': daily_volume,
                'profitability': (sell_price - buy_price) * daily_volume,
                'price_min': min(prices_sorted),
                'price_max': max(prices_sorted),
                'price_p25': buy_price,
                'price_p75': p75_price,
                'total_sales_in_history': len(prices),
                'total_quantity_in_history': total_quantity,
                'days_span': days_span,
            }
            
            return result
        
        except Exception as e:
            logger.warning(f"Error analyzing item {item_id}: {e}")
            return None
    
    def fetch_and_analyze(self, item_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Fetch history data for items and analyze profitability
        """
        logger.info(f"Fetching history for {len(item_ids)} items...")
        
        all_results = []
        
        # Process in batches of 100
        for i in range(0, len(item_ids), 100):
            batch = item_ids[i:i+100]
            logger.info(f"Processing batch {i//100 + 1}: items {i+1} to {min(i+100, len(item_ids))}")
            
            try:
                response = self.client.get_history(batch, entries_to_return=100)
                
                # Response can be either a single item or multiple
                if 'itemID' in response:
                    # Single item response
                    result = self.analyze_item_history(response['itemID'], response)
                    if result:
                        all_results.append(result)
                
                elif 'items' in response:
                    # Multiple items response
                    for item_id, item_data in response['items'].items():
                        result = self.analyze_item_history(int(item_id), item_data)
                        if result:
                            all_results.append(result)
            
            except Exception as e:
                logger.error(f"Error fetching batch: {e}")
        
        logger.info(f"Successfully analyzed {len(all_results)} items")
        
        # Fetch item names
        item_ids_to_fetch = [r['item_id'] for r in all_results]
        item_names = fetch_item_names_batch(item_ids_to_fetch)
        
        for result in all_results:
            result['item_name'] = item_names.get(result['item_id'], f"Item_{result['item_id']}")
        
        return all_results
    
    def analyze_and_export(self, output_file: str = "data/market_analysis_v2.csv",
                          num_items: int = 200):
        """
        Complete analysis pipeline using history data
        """
        # Get test items
        test_items = self.get_test_items(num_items)
        
        # Analyze history
        results = self.fetch_and_analyze(test_items)

        # Optional: craft cost estimation (best-effort; may fail for non-craftables)
        for r in results:
            craft_info = estimate_craft_cost(r['item_id'], self.client, self.datacenter)
            if craft_info:
                r['craft_cost'] = craft_info['craft_cost']
                r['craft_profit'] = r['sell_price'] - craft_info['craft_cost']
                r['craft_profit_per_unit'] = r['sell_price'] - craft_info['craft_cost']
                r['craft_profit_daily'] = (r['sell_price'] - craft_info['craft_cost']) * r['daily_volume']
        
        # Sort by profitability
        results_sorted = sorted(results, key=lambda x: x['profitability'], reverse=True)
        
        # Create DataFrame and export
        df = pd.DataFrame(results_sorted)
        
        if len(df) > 0:
            export_columns = [
                'item_id', 'item_name',
                'buy_price', 'median_price', 'sell_price', 'sell_price_p75',
                'margin_per_unit', 'daily_volume', 'profitability',
                'price_min', 'price_p25', 'price_p75', 'price_max',
                'total_sales_in_history', 'total_quantity_in_history', 'days_span',
                'craft_cost', 'craft_profit', 'craft_profit_daily'
            ]
            
            export_columns = [col for col in export_columns if col in df.columns]
            df = df[export_columns]
            df.to_csv(output_file, index=False)
            
            logger.info(f"Analysis complete! Results exported to {output_file}")
            logger.info(f"\nTop 15 items by profitability:")
            top_cols = ['item_id', 'item_name', 'buy_price', 'sell_price', 'daily_volume', 'profitability']
            top_cols = [col for col in top_cols if col in df.columns]
            print("\n" + df[top_cols].head(15).to_string(index=False))
            
            # Statistics
            print(f"\n\nStatistics:")
            print(f"Total items analyzed: {len(df)}")
            if 'profitability' in df.columns:
                print(f"Average daily profitability per item: {df['profitability'].mean():,.0f} gil")
                print(f"Total daily profitability (sum): {df['profitability'].sum():,.0f} gil")
                print(f"Max daily profitability: {df['profitability'].max():,.0f} gil")
                print(f"Median daily profitability: {df['profitability'].median():,.0f} gil")
                print(f"Items with positive profitability: {(df['profitability'] > 0).sum()}")
                print(f"Items with realistic volume (>5/day): {(df['daily_volume'] > 5).sum()}")
        else:
            logger.warning("No items were successfully analyzed")
        
        return df
