"""
Craft cost estimation using XIVAPI recipes and Universalis prices.
This is a best-effort estimator; data availability may vary.
"""
import logging
import requests
from typing import Dict, Any, List, Optional
from src.universalis_client import UniversalisClient

logger = logging.getLogger(__name__)

XIVAPI_SEARCH = "https://xivapi.com/search"
XIVAPI_RECIPE = "https://xivapi.com/recipe/{id}"


def fetch_recipe_for_item(item_id: int) -> Optional[Dict[str, Any]]:
    """Find a recipe that produces the given item_id and return recipe data."""
    try:
        params = {
            "indexes": "recipe",
            "filters": f"ItemResult.ID={item_id}",
            "page": 1
        }
        resp = requests.get(XIVAPI_SEARCH, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("Results", [])
        if not results:
            return None
        recipe_id = results[0].get("ID")
        if recipe_id is None:
            return None
        recipe_resp = requests.get(XIVAPI_RECIPE.format(id=recipe_id), timeout=15)
        recipe_resp.raise_for_status()
        return recipe_resp.json()
    except Exception as e:
        logger.warning(f"Recipe fetch failed for item {item_id}: {e}")
        return None


def extract_ingredients(recipe: Dict[str, Any]) -> List[Dict[str, int]]:
    """Extract ingredient item IDs and amounts from recipe structure."""
    ingredients = []
    for i in range(10):  # recipe typically has up to 10 ingredients
        item_key = f"ItemIngredient{i}TargetID"
        amount_key = f"AmountIngredient{i}"
        item_id = recipe.get(item_key)
        amount = recipe.get(amount_key)
        if item_id and amount:
            ingredients.append({"item_id": int(item_id), "amount": int(amount)})
    return ingredients


def estimate_craft_cost(item_id: int, client: UniversalisClient, datacenter: str) -> Optional[Dict[str, Any]]:
    """
    Estimate craft cost for an item by summing ingredient costs (min listing price per ingredient).
    Returns None if recipe or prices are unavailable.
    """
    recipe = fetch_recipe_for_item(item_id)
    if not recipe:
        return None
    ingredients = extract_ingredients(recipe)
    if not ingredients:
        return None

    ingredient_costs = []
    total_cost = 0.0

    for ing in ingredients:
        ing_id = ing["item_id"]
        amount = ing["amount"]
        try:
            # Use aggregated to get min listing for ingredient (DC level)
            resp = client.get_aggregated_data([ing_id])
            min_price = None
            if "results" in resp and resp["results"]:
                ing_res = resp["results"][0]
                # prefer DC minListing if present
                min_price = (
                    ing_res.get("nq", {})
                    .get("minListing", {})
                    .get("dc", {})
                    .get("price")
                ) or (
                    ing_res.get("nq", {})
                    .get("minListing", {})
                    .get("region", {})
                    .get("price")
                )
            if min_price is None:
                continue
            cost = min_price * amount
            ingredient_costs.append({"item_id": ing_id, "amount": amount, "unit_price": min_price, "cost": cost})
            total_cost += cost
        except Exception as e:
            logger.warning(f"Failed price for ingredient {ing_id}: {e}")
            continue

    if not ingredient_costs:
        return None

    return {
        "craft_cost": total_cost,
        "ingredients": ingredient_costs,
    }
