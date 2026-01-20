# Onboarding Guide for Contributors

Welcome to **FFXIV Market Annihilation**! This guide will help you get up to speed quickly so you can contribute effectively.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Code Architecture](#code-architecture)
3. [Development Setup](#development-setup)
4. [Understanding the Codebase](#understanding-the-codebase)
5. [Common Tasks](#common-tasks)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Where to Get Help](#where-to-get-help)

---

## Project Overview

**Goal:** Analyze FFXIV market board data from Universalis to identify profitable trading opportunities.

**Current State:**
- **v2 (History-Based):** Recommended approach using actual sales transactions. Uses median pricing, percentile buy/sell, realistic volume.
- **v1 (Aggregated):** Deprecated. Uses DC-wide aggregated metrics (can overstate profitability). Kept in `legacy/` for reference.

**Key Data Sources:**
- [Universalis API](https://docs.universalis.app/) – Market board data (aggregated & history)
- [XIVAPI](https://xivapi.com/) – Recipe data for craft cost estimation
- [FFXIV Teamcraft](https://ffxivteamcraft.com/) – Fallback for item names

---

## Code Architecture

### Directory Structure

```
FFXIVMarketAnnihilation/
├── main_v2.py                     # Entry point: run v2 analysis
├── reports_v2.py                  # Generate comprehensive reports from v2 data
├── compare_versions.py            # Compare v1 vs v2 analysis
├── src/
│   ├── analyzer_v2.py             # Core v2 analyzer (history-based)
│   ├── craft_cost.py              # Craft cost estimation (XIVAPI + Universalis)
│   ├── item_mapper.py             # Item ID ↔ name mapping
│   └── universalis_client.py      # Universalis API client
├── legacy/                        # Deprecated v1 code (aggregated approach)
│   ├── analyzer.py
│   ├── main.py
│   └── reports.py
├── scripts/                       # Debug/inspection utilities
│   ├── debug_api.py
│   ├── debug_api_response.py
│   └── inspect_data.py
├── data/                          # Generated CSV/report outputs
│   ├── market_analysis_v2.csv     # Latest v2 analysis
│   └── reports_v2.txt             # Human-readable reports
├── requirements.txt               # Python dependencies
├── .gitignore                     # Excluded files (venv, .env, __pycache__)
├── INSTALL.md                     # Installation instructions
├── README.md                      # User-facing documentation
└── ONBOARDING.md                  # This file
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `analyzer_v2.py` | Fetches history data, calculates percentiles, computes profitability, exports CSV |
| `craft_cost.py` | Fetches recipe from XIVAPI, gets ingredient prices from Universalis, sums craft cost |
| `item_mapper.py` | Resolves item IDs → names via XIVAPI/Teamcraft; caches results |
| `universalis_client.py` | Wrapper for Universalis API with rate limiting and error handling |

---

## Development Setup

### 1. Clone Repository

```bash
git clone <your-fork-url>
cd FFXIVMarketAnnihilation
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `requests` – HTTP client for API calls
- `pandas` – Data manipulation and CSV export
- `python-dotenv` – Environment variable loading (optional)

### 4. Run Initial Analysis

```bash
# Run v2 analysis
python main_v2.py

# Generate reports
python reports_v2.py
```

**Expected Output:**
- `data/market_analysis_v2.csv` – ~174 items with profitability metrics
- Console output showing top 15 items by profitability

---

## Understanding the Codebase

### Data Flow (v2)

```
1. main_v2.py
   └─> analyzer_v2.MarketAnalyzer2
       ├─> get_recently_updated_items()      # Fetch 200 active items from Universalis
       ├─> fetch_history_data()              # Get sales history for each item
       ├─> calculate_profitability()         # Compute buy/sell/volume/profit
       │   ├─> item_mapper.fetch_item_names_batch()  # Resolve item IDs → names
       │   └─> craft_cost.estimate_craft_cost()      # Optional: recipe + ingredient costs
       └─> export to CSV

2. reports_v2.py
   └─> generate_reports()
       ├─> Read data/market_analysis_v2.csv
       ├─> Generate 7 different report sections
       └─> Output to console (can redirect to file)
```

### Key Algorithms

#### Profitability Calculation (v2)

```python
# From analyzer_v2.py
buy_price = percentile(prices, 25)        # P25 of all sales
sell_price = median(recent_3_days)        # Median of last 3 days (fallback: overall median)
daily_volume = total_quantity / days_span # Realistic average sales/day
profitability = (sell_price - buy_price) * daily_volume
```

#### Craft Cost Estimation

```python
# From craft_cost.py
1. Fetch recipe from XIVAPI (search by item ID)
2. Extract ingredient list (item_id, quantity)
3. For each ingredient:
   - Fetch minListing from Universalis aggregated
   - cost = minListing * quantity
4. craft_cost = sum(all ingredient costs)
```

---

## Common Tasks

### Add a New Report Section

**File:** `reports_v2.py`

1. Load the CSV:
   ```python
   df = pd.read_csv("data/market_analysis_v2.csv")
   ```

2. Filter/sort data as needed:
   ```python
   top_items = df.nlargest(15, 'profitability')
   ```

3. Format and print:
   ```python
   print("\n\nMY NEW REPORT")
   print("-" * 100)
   print(top_items[['item_name', 'profitability']].to_string(index=False))
   ```

### Change Analysis Parameters

**File:** `main_v2.py`

```python
# Edit these variables
datacenter = "Chaos"              # Change to your datacenter
num_items_to_fetch = 200          # Number of active items to analyze
entries_to_return = 100           # History entries per item (more = slower but more accurate)
```

### Add Error Handling for XIVAPI

**File:** `craft_cost.py`

XIVAPI returns HTTP 500 frequently. Current code logs warnings. To retry:

```python
import time

def estimate_craft_cost(item_id, client, max_retries=3):
    for attempt in range(max_retries):
        try:
            recipe = fetch_recipe(item_id)
            # ... process recipe
            return craft_cost
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            logger.warning(f"Failed after {max_retries} retries: {e}")
            return None
```

### Test with Small Dataset

**File:** `main_v2.py`

Change line selecting items:

```python
# Instead of 200 items
test_items = get_recently_updated_items(datacenter, num_items=20)
```

---

## Best Practices

### Code Style

- Follow PEP 8 conventions
- Use type hints where practical: `def func(x: int) -> str:`
- Docstrings for all public functions/classes
- Keep functions focused (single responsibility)

### Logging

Use Python's `logging` module (already configured):

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Processing batch 1...")
logger.warning("Failed to fetch item 12345")
logger.error("Critical error", exc_info=True)
```

### API Rate Limiting

Universalis has strict rate limits. **Always use `universalis_client.py`**—it handles rate limiting automatically.

```python
# Good
client = UniversalisClient(datacenter="Chaos")
data = client.get_history(item_ids)

# Bad (direct requests without rate limit)
response = requests.get("https://universalis.app/api/v2/...")
```

### Error Handling

APIs can fail. **Always handle exceptions:**

```python
try:
    data = client.get_history(item_ids)
except Exception as e:
    logger.error(f"Failed to fetch history: {e}")
    return None
```

### Data Validation

Market data can be incomplete. **Always check before use:**

```python
if not prices or len(prices) < 5:
    logger.warning(f"Insufficient data for item {item_id}")
    return None

buy_price = np.percentile(prices, 25) if prices else 0
```

---

## Troubleshooting

### XIVAPI Returns HTTP 500

**Symptom:** Many warnings like `Recipe fetch failed for item 44033: 500 Server Error`

**Cause:** XIVAPI is unstable and frequently returns 500s.

**Fix:**
- Accept missing craft costs for some items (normal)
- Add retry logic with exponential backoff (see "Add Error Handling" above)
- Use a local XIVAPI mirror if available

### No Items Returned

**Symptom:** `Found 0 recently updated items`

**Cause:** Datacenter name incorrect or API issue.

**Fix:**
- Verify datacenter spelling: `Chaos`, `Aether`, `Primal`, etc. (case-sensitive)
- Check Universalis API status: https://universalis.app/
- Try different datacenter

### High Memory Usage

**Symptom:** Script crashes or slows with >1000 items

**Cause:** Loading all history data into memory.

**Fix:**
- Reduce `num_items_to_fetch` in `main_v2.py`
- Reduce `entries_to_return` (default 100 is reasonable)
- Process in smaller batches

### CSV Export Fails

**Symptom:** `PermissionError` or file in use

**Cause:** CSV file open in Excel or another program.

**Fix:**
- Close file before running script
- Change output filename in `main_v2.py`

---

## Where to Get Help

1. **README.md** – User-facing documentation and quick reference
2. **INSTALL.md** – Detailed installation steps
3. **Code Comments** – Most functions have docstrings explaining logic
4. **compare_versions.py** – Explains differences between v1 and v2
5. **scripts/** – Debug scripts to inspect API responses

### External Resources

- [Universalis API Docs](https://docs.universalis.app/)
- [XIVAPI Docs](https://xivapi.com/docs)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

### Questions?

Open an issue on GitHub or ask in project discussions.

---

## Next Steps

Now that you're set up:

1. Run `python main_v2.py` to generate fresh data
2. Run `python reports_v2.py` to see all reports
3. Review `analyzer_v2.py` to understand core logic
4. Pick an issue from GitHub or propose your own enhancement
5. Make changes, test locally, submit a PR

**Happy coding!** 🎮📈
