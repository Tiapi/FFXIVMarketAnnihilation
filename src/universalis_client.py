"""
Client for Universalis API - FFXIV Market Board data
"""
import requests
import time
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UniversalisClient:
    BASE_URL = "https://universalis.app/api/v2"
    RATE_LIMIT_DELAY = 0.05  # 50ms between requests to stay under 25 req/s limit
    
    def __init__(self, datacenter: str = "Chaos"):
        self.datacenter = datacenter
        self.session = requests.Session()
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Respect API rate limit of 25 req/s"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def get_worlds(self) -> List[Dict[str, Any]]:
        """Get all available worlds"""
        self._rate_limit()
        url = f"{self.BASE_URL}/worlds"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_data_centers(self) -> List[Dict[str, Any]]:
        """Get all available datacenters"""
        self._rate_limit()
        url = f"{self.BASE_URL}/data-centers"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_marketable_items(self) -> List[int]:
        """Get all marketable item IDs"""
        logger.info("Fetching all marketable items...")
        self._rate_limit()
        url = f"{self.BASE_URL}/marketable"
        response = self.session.get(url)
        response.raise_for_status()
        items = response.json()
        logger.info(f"Found {len(items)} marketable items")
        return items
    
    def get_aggregated_data(self, item_ids: List[int]) -> Dict[str, Any]:
        """
        Get aggregated market board data for items.
        API supports up to 100 item IDs per request.
        
        Returns data including:
        - minListing: minimum listing price
        - medianListing: median listing price
        - recentPurchase: recent sale price and timestamp
        - averageSalePrice: average sale price (last 4 days)
        - dailySaleVelocity: average sales per day (last 4 days)
        """
        if len(item_ids) > 100:
            raise ValueError("Maximum 100 items per request")
        
        self._rate_limit()
        item_ids_str = ",".join(map(str, item_ids))
        url = f"{self.BASE_URL}/aggregated/{self.datacenter}/{item_ids_str}"
        
        logger.info(f"Fetching data for {len(item_ids)} items...")
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_history(self, item_ids: List[int], entries_to_return: int = 100) -> Dict[str, Any]:
        """
        Get historical data for items (sales history)
        """
        if len(item_ids) > 100:
            raise ValueError("Maximum 100 items per request")
        
        self._rate_limit()
        item_ids_str = ",".join(map(str, item_ids))
        url = f"{self.BASE_URL}/history/{self.datacenter}/{item_ids_str}"
        params = {
            "entriesToReturn": entries_to_return
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_tax_rates(self) -> Dict[str, int]:
        """Get market tax rates for the datacenter"""
        self._rate_limit()
        # Get a world from the datacenter to fetch tax rates
        worlds = self.get_worlds()
        dc_worlds = [w for w in worlds if w.get('dataCenter') == self.datacenter]
        
        if not dc_worlds:
            logger.warning(f"No worlds found for datacenter {self.datacenter}")
            return {}
        
        world_name = dc_worlds[0]['name']
        url = f"{self.BASE_URL}/tax-rates"
        params = {"world": world_name}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
