"""
Market analysis and profitability calculation
"""
import random
from typing import List, Dict, Any
import logging
import pandas as pd
from src.universalis_client import UniversalisClient
from src.item_mapper import fetch_item_names_batch

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    def __init__(self, datacenter: str = "Chaos"):
        self.client = UniversalisClient(datacenter)
        self.datacenter = datacenter
    
    def get_test_items(self, num_random: int = 100, num_top_sellers: int = 100) -> List[int]:
        """
        Get a mix of random items and top sellers
        
        Args:
            num_random: number of random items to select
            num_top_sellers: number of top-selling items to select
        
        Returns:
            List of item IDs
        """
        logger.info(f"Selecting {num_random + num_top_sellers} active items from the market...")
        
        all_items_set = set()
        
        try:
            # Use the datacenter name directly - it's recognized by the API
            # Get most recently updated items - these have recent market activity
            url = f"{self.client.BASE_URL}/extra/stats/most-recently-updated"
            params = {"dcName": self.datacenter, "entries": 200}
            
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
        
        # Convert to list and shuffle to get diverse items
        active_items = list(all_items_set)
        random.shuffle(active_items)
        
        # Take the requested number
        test_items = active_items[:num_random + num_top_sellers]
        logger.info(f"Selected {len(test_items)} active items for analysis")
        return test_items
    
    def fetch_item_data(self, item_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Fetch aggregated market data for items
        """
        logger.info(f"Fetching market data for {len(item_ids)} items...")
        
        all_data = {}
        
        # Process in batches of 100 (API limit)
        for i in range(0, len(item_ids), 100):
            batch = item_ids[i:i+100]
            logger.info(f"Processing batch {i//100 + 1}: items {i+1} to {min(i+100, len(item_ids))}")
            
            try:
                response = self.client.get_aggregated_data(batch)
                
                if 'results' in response:
                    for result in response['results']:
                        item_id = result['itemId']
                        all_data[item_id] = result
                
                if 'failedItems' in response and response['failedItems']:
                    logger.warning(f"Failed to fetch {len(response['failedItems'])} items")
            
            except Exception as e:
                logger.error(f"Error fetching batch: {e}")
        
        logger.info(f"Successfully fetched data for {len(all_data)} items")
        return all_data
    
    def calculate_profitability(self, item_data: Dict[int, Dict[str, Any]], 
                                item_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Calculate profitability metrics for items
        
        Profitability is calculated as:
        - Margin per unit = Average selling price - Minimum listing price (cost to buy)
        - Profitability = Margin per unit * Daily sales velocity
        
        This shows the potential profit from buying items and reselling them.
        """
        results = []
        
        # Fetch item names in batch
        item_names = fetch_item_names_batch(item_ids)
        
        for item_id in item_ids:
            if item_id not in item_data:
                continue
            
            data = item_data[item_id]
            
            try:
                # Extract NQ and HQ data separately
                nq_data = data.get('nq', {})
                hq_data = data.get('hq', {})
                
                # For NQ: use average sale price and min listing (what we can buy at)
                nq_min_listing = nq_data.get('minListing', {}).get('dc', {}).get('price', 0)
                nq_avg_sale = nq_data.get('averageSalePrice', {}).get('dc', {}).get('price', 0)
                nq_daily_velocity = nq_data.get('dailySaleVelocity', {}).get('dc', {}).get('quantity', 0)
                
                # If no DC-level min listing, try region
                if nq_min_listing == 0:
                    nq_min_listing = nq_data.get('minListing', {}).get('region', {}).get('price', 0)
                
                # If no DC-level average, try region  
                if nq_avg_sale == 0:
                    nq_avg_sale = nq_data.get('averageSalePrice', {}).get('region', {}).get('price', 0)
                
                if nq_daily_velocity == 0:
                    nq_daily_velocity = nq_data.get('dailySaleVelocity', {}).get('region', {}).get('quantity', 0)
                
                # For HQ: same approach
                hq_min_listing = hq_data.get('minListing', {}).get('dc', {}).get('price', 0)
                hq_avg_sale = hq_data.get('averageSalePrice', {}).get('dc', {}).get('price', 0)
                hq_daily_velocity = hq_data.get('dailySaleVelocity', {}).get('dc', {}).get('quantity', 0)
                
                if hq_min_listing == 0:
                    hq_min_listing = hq_data.get('minListing', {}).get('region', {}).get('price', 0)
                
                if hq_avg_sale == 0:
                    hq_avg_sale = hq_data.get('averageSalePrice', {}).get('region', {}).get('price', 0)
                    
                if hq_daily_velocity == 0:
                    hq_daily_velocity = hq_data.get('dailySaleVelocity', {}).get('region', {}).get('quantity', 0)
                
                # Calculate margin: profit per unit = what we sell for - what we buy for
                # Using average sale price as what we can sell for
                nq_margin_per_unit = nq_avg_sale - nq_min_listing if (nq_avg_sale > 0 and nq_min_listing > 0) else 0
                nq_profitability = nq_margin_per_unit * nq_daily_velocity
                
                hq_margin_per_unit = hq_avg_sale - hq_min_listing if (hq_avg_sale > 0 and hq_min_listing > 0) else 0
                hq_profitability = hq_margin_per_unit * hq_daily_velocity
                
                # Skip items with no market activity
                if nq_daily_velocity == 0 and hq_daily_velocity == 0:
                    continue
                
                result = {
                    'item_id': item_id,
                    'item_name': item_names.get(item_id, f"Item_{item_id}"),
                    'nq_min_listing': nq_min_listing,
                    'nq_avg_sale_price': nq_avg_sale,
                    'nq_daily_sales': nq_daily_velocity,
                    'nq_margin_per_unit': nq_margin_per_unit,
                    'nq_profitability': nq_profitability,
                    'hq_min_listing': hq_min_listing,
                    'hq_avg_sale_price': hq_avg_sale,
                    'hq_daily_sales': hq_daily_velocity,
                    'hq_margin_per_unit': hq_margin_per_unit,
                    'hq_profitability': hq_profitability,
                }
                results.append(result)
            
            except Exception as e:
                logger.warning(f"Error processing item {item_id}: {e}")
        
        return results
    
    def analyze_and_export(self, output_file: str = "data/market_analysis.csv",
                          num_random: int = 100, num_top_sellers: int = 100):
        """
        Complete analysis pipeline: fetch items, analyze, and export
        """
        # Get test items
        test_items = self.get_test_items(num_random, num_top_sellers)
        
        # Fetch market data
        item_data = self.fetch_item_data(test_items)
        
        # Calculate profitability
        results = self.calculate_profitability(item_data, test_items)
        
        logger.info(f"Total items with market activity: {len(results)}")
        
        # Sort by profitability (NQ primary metric)
        results_sorted = sorted(results, key=lambda x: x['nq_profitability'], reverse=True)
        
        # Create DataFrame and export
        df = pd.DataFrame(results_sorted)
        
        if len(df) > 0:
            # Select columns for export (prioritize NQ metrics)
            export_columns = [
                'item_id', 'item_name', 
                'nq_min_listing', 'nq_avg_sale_price',
                'nq_margin_per_unit', 'nq_daily_sales', 'nq_profitability',
                'hq_min_listing', 'hq_avg_sale_price',
                'hq_margin_per_unit', 'hq_daily_sales', 'hq_profitability'
            ]
            
            # Filter to only columns that exist
            export_columns = [col for col in export_columns if col in df.columns]
            df = df[export_columns]
            df.to_csv(output_file, index=False)
            
            logger.info(f"Analysis complete! Results exported to {output_file}")
            
            # Show top items by profitability
            logger.info(f"\nTop 15 items by NQ profitability:")
            top_cols = ['item_id', 'item_name', 'nq_margin_per_unit', 'nq_daily_sales', 'nq_profitability']
            top_cols = [col for col in top_cols if col in df.columns]
            print("\n" + df[top_cols].head(15).to_string(index=False))
            
            # Show statistics
            print(f"\n\nStatistics:")
            print(f"Total items analyzed: {len(df)}")
            if 'nq_profitability' in df.columns:
                print(f"Average profitability (NQ): {df['nq_profitability'].mean():.0f} gil/day")
                print(f"Max profitability (NQ): {df['nq_profitability'].max():.0f} gil/day")
                print(f"Items with positive NQ profitability: {(df['nq_profitability'] > 0).sum()}")
                
            if 'hq_profitability' in df.columns:
                print(f"Average profitability (HQ): {df['hq_profitability'].mean():.0f} gil/day")
                print(f"Max profitability (HQ): {df['hq_profitability'].max():.0f} gil/day")
                print(f"Items with positive HQ profitability: {(df['hq_profitability'] > 0).sum()}")
        else:
            logger.warning("No items with market activity found")
        
        return df
