# FFXIVMarketAnnihilation

Using the [Universalis API](https://docs.universalis.app/), analyze the FFXIV market board to identify the most profitable items and become a real tycoon.

## Overview

This project analyzes real-time market data from Final Fantasy XIV's market board using the Universalis API. It identifies profitable trading opportunities by analyzing:

- **Price margins**: Difference between listing prices and average selling prices
- **Sales velocity**: Volume of items sold per day
- **Profitability**: Margin × Sales = Daily profit potential

## Project Structure

```
.
├── main.py                  # Main script to run market analysis
├── reports.py              # Generate advanced analysis reports
├── requirements.txt        # Python dependencies
├── src/
│   ├── universalis_client.py  # Universalis API client
│   ├── analyzer.py            # Market analysis logic
│   └── item_mapper.py         # Item ID to name mapping
└── data/
    ├── market_analysis.csv    # Raw analysis results (auto-generated)
    └── item_cache.json        # Cached item names (auto-generated)
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Market Analysis

```bash
python main.py
```

This will:
- Select 200 active items from the Chaos datacenter
- Fetch current market data from Universalis
- Calculate profitability for each item
- Export results to `data/market_analysis.csv`

### 3. Generate Detailed Reports

```bash
python reports.py
```

This generates multiple analysis reports:
- **Top items by profitability**: Highest gil/day potential
- **Top items by margin**: Highest profit per unit
- **Top items by volume**: Highest daily sales (most liquid)
- **HQ analysis**: Profitability for High-Quality items
- **Steady income items**: Best items for consistent daily income
- **Summary statistics**: Overall market metrics

## Key Metrics

### Profitability Formula

```
Profitability = (Average Sale Price - Min Listing Price) × Daily Sales Velocity
```

- **NQ (Normal Quality)**: Primary analysis metric
- **HQ (High Quality)**: Secondary analysis for premium items

### What the Numbers Mean

From the sample run:
- **176 million gil/day** total profitability across 188 items
- **150 items** with positive NQ profitability
- **Crescent Moon Nightgown**: 47M gil/day (huge margin, low volume)
- **Craftsman's Command Materia XI**: 46M gil/day (small margin, massive volume)
- **Wind Crystal**: 1.28M gil/day (massive volume, tiny margin)

## API Rate Limits

The Universalis API has rate limits:
- **25 requests/second** (50 burst)
- **100 items** maximum per request
- **8 simultaneous connections** per IP

The script respects these limits automatically with rate limiting delays.

## Analysis Strategy

### Current Implementation

The current prototype:
1. Fetches 200 most recently updated items (proxy for active items)
2. Gets aggregated market data across the Chaos datacenter
3. Calculates profitability using DC-level data (fallback to region)
4. Sorts items by potential daily profit

### Future Improvements

Possible enhancements:
- [ ] Analyze crafting recipes (calculate true profit: revenue - material cost)
- [ ] Compare NQ vs HQ profitability separately
- [ ] Track historical trends (7-day moving averages)
- [ ] Filter by item category (materia, materials, equipment, etc.)
- [ ] Analyze all 16,670 marketable items (scan in batches)
- [ ] Web dashboard for real-time market monitoring
- [ ] Price prediction using historical data
- [ ] Support for multiple datacenters/worlds
- [ ] Subscription-like monitoring with alerts

## Configuration

Edit `src/analyzer.py` to change:
- **Datacenter**: Currently set to "Chaos" (Europe). Use any datacenter name.
- **Number of items**: Modify `num_random` and `num_top_sellers` in `main.py`

Supported datacenters:
- Japan: Elemental, Gaia, Mana
- North America: Aether, Primal, Crystal
- Europe: Chaos, Light
- Oceania: Materia
- Others: Dynamis, Meteor, Cloud DC (beta)

## Data Schema

### CSV Output Columns

```
- item_id: FFXIV item ID
- item_name: Human-readable item name
- nq_min_listing: Cheapest NQ item listed (buying cost)
- nq_avg_sale_price: Average NQ sale price (selling price)
- nq_margin_per_unit: Profit per unit sold (NQ)
- nq_daily_sales: Average sales per day (NQ)
- nq_profitability: Total daily profit potential (NQ)
- hq_*: Same metrics for High-Quality items
```

## Disclaimer

This project is for analysis and educational purposes. Market prices fluctuate constantly. Past profitability does not guarantee future results. Use at your own risk!

## References

- [Universalis API Documentation](https://docs.universalis.app/)
- [XIVAPI Item Database](https://xivapi.com/)
- [FFXIV Market Board](https://www.universalis.app/)
- [FFXIV Data Mining](https://github.com/xivapi/ffxiv-datamining)
