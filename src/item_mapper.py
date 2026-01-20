"""
Cache and mapping utilities for item names
"""
import json
import os
import logging
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

ITEM_CACHE_FILE = "data/item_cache.json"

def load_item_cache() -> Dict[int, str]:
    """Load cached item name mappings"""
    if os.path.exists(ITEM_CACHE_FILE):
        try:
            with open(ITEM_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                # Convert string keys back to integers
                return {int(k): v for k, v in cache.items()}
        except Exception as e:
            logger.warning(f"Could not load item cache: {e}")
    return {}

def save_item_cache(cache: Dict[int, str]):
    """Save item name mappings to cache"""
    try:
        os.makedirs("data", exist_ok=True)
        with open(ITEM_CACHE_FILE, 'w', encoding='utf-8') as f:
            # Convert integer keys to strings for JSON
            json.dump({str(k): v for k, v in cache.items()}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Could not save item cache: {e}")

def fetch_item_names_batch(item_ids: List[int]) -> Dict[int, str]:
    """
    Fetch item names from XIVAPI in batch
    This is more efficient than individual requests
    """
    names = {}
    cache = load_item_cache()
    
    # Load from cache first
    items_to_fetch = []
    for item_id in item_ids:
        if item_id in cache:
            names[item_id] = cache[item_id]
        else:
            items_to_fetch.append(item_id)
    
    if not items_to_fetch:
        return names
    
    # Fetch missing items from XIVAPI
    # Note: XIVAPI's batch endpoint has a limit, so we process in smaller batches
    logger.info(f"Fetching {len(items_to_fetch)} item names from XIVAPI...")
    
    try:
        # Try using the ffxiv-teamcraft JSON dump (more reliable)
        logger.info("Attempting to load item names from ffxiv-teamcraft...")
        response = requests.get(
            "https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/libs/data/src/lib/json/items.json",
            timeout=30
        )
        response.raise_for_status()
        
        items_json = response.json()
        
        for item_id in items_to_fetch:
            if str(item_id) in items_json:
                item_name = items_json[str(item_id)].get('en', f"Item_{item_id}")
                names[item_id] = item_name
                cache[item_id] = item_name
        
        # Save updated cache
        save_item_cache(cache)
        logger.info(f"Loaded {len(names)} item names")
    
    except Exception as e:
        logger.warning(f"Could not fetch item names from JSON: {e}")
        # Use item IDs as fallback
        for item_id in items_to_fetch:
            names[item_id] = f"Item_{item_id}"
    
    return names
