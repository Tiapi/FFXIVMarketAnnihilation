# FFXIV Market Annihilation

Analyze the FFXIV market board using the [Universalis API](https://docs.universalis.app/) to identify profitable trading opportunities and become a market tycoon.

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python main_v2.py` | Run history-based analysis (recommended) |
| `python reports_v2.py` | Generate comprehensive reports |
| `python compare_versions.py` | Compare v1 vs v2 approaches |
| `python legacy/main.py` | Run deprecated v1 analysis |
| `python scripts/debug_api.py` | Inspect API connectivity |

**Output:** `data/market_analysis_v2.csv`, console reports

---

## Quick Start

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd FFXIVMarketAnnihilation

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Analysis

```bash
# Run history-based market analysis (recommended)
python main_v2.py

# Generate comprehensive reports
python reports_v2.py

# Compare v1 vs v2 approaches (optional)
python compare_versions.py
```

## Output Files

- `data/market_analysis_v2.csv` – Detailed profitability analysis with pricing, volume, margins
- `data/reports_v2.txt` – Human-readable reports (top items, liquidity, volatility, risk analysis)

## Project Structure

```
FFXIVMarketAnnihilation/
├── main_v2.py              # Primary entry: history-based analysis
├── reports_v2.py           # Report generator (profitability, volume, margins, risk)
├── compare_versions.py     # Compare v1 (aggregated) vs v2 (history)
├── src/
│   ├── analyzer_v2.py      # History-based market analyzer (recommended)
│   ├── craft_cost.py       # Craft cost estimation (XIVAPI recipes + Universalis ingredients)
│   ├── item_mapper.py      # Item ID ↔ name resolution (XIVAPI + teamcraft)
│   └── universalis_client.py  # Universalis API client
├── legacy/                 # v1 aggregated approach (deprecated)
├── scripts/                # Debug/inspection scripts
├── data/                   # Generated CSVs and reports
├── requirements.txt        # Python dependencies
├── .gitignore              # Ignore venv, .env, __pycache__, etc.
└── INSTALL.md              # Full installation guide
```

## How It Works (v2)

**v2 (History-Based)** analyzes real transaction data:

1. **Fetch historical sales** from Universalis `/history` endpoint
2. **Calculate median prices** (P25 for buy, median recent 3 days for sell)
3. **Compute realistic daily volume** from actual sales over time span
4. **Estimate craft costs** (optional, via XIVAPI recipes + Universalis ingredient prices)
5. **Export profitability** metrics: margin, volume, daily profit, volatility

**Why v2 over v1?**
- **v1 (Aggregated):** Uses `averageSalePrice` (skewed by outliers), `minListing` (1 item only), DC-wide velocity (can overstate volume).
- **v2 (History):** Median pricing resistant to outliers; percentile-based buy/sell; realistic sales volume from actual transactions; price distribution metrics.

See [compare_versions.py](compare_versions.py) for a detailed comparison.

## Key Metrics

| Metric | Description |
|--------|-------------|
| **buy_price** | P25 of historical sales (realistic buy-in) |
| **sell_price** | Median of recent 3 days' sales (or overall if insufficient recent data) |
| **daily_volume** | Average sales/day from transaction history |
| **profitability** | `(sell_price - buy_price) × daily_volume` |
| **craft_cost** | Sum of ingredient costs via Universalis (optional) |
| **craft_profit_daily** | `(sell_price - craft_cost) × daily_volume` (if crafting) |

## Sample Output

From a recent run:

```
Top 15 items by profitability:
  item_id                     item_name   buy_price  sell_price  daily_volume  profitability
    46834 Felyne Support Team Cart Horn 31,662,500  33,399,995           2.2      3,894,793
    16564         Night Pegasus Whistle 13,000,000  13,999,000           2.5      2,544,440
    43590              Ty'aitya Whistle 80,744,999  83,635,000           0.9      2,504,619
    ...

Statistics:
Total items analyzed: 174
Average daily profitability per item: 140,713 gil
Items with positive profitability: 155
Items with realistic volume (>5/day): 87
```

## Configuration

Edit variables in [main_v2.py](main_v2.py):

```python
datacenter = "Chaos"          # Any DC: Aether, Primal, Crystal, Chaos, Light, etc.
num_items = 200               # Number of recently updated items to analyze
```

Supported datacenters: Aether, Primal, Crystal (NA); Chaos, Light (EU); Elemental, Gaia, Mana (JP); Materia (OCE); Dynamis, Meteor (beta).

## Advanced Usage

### Craft Cost Analysis

The analyzer automatically attempts to fetch recipes from XIVAPI and estimate craft costs using Universalis ingredient prices. Results are in `craft_cost` and `craft_profit_daily` columns.

**Note:** XIVAPI can be unstable (HTTP 500s). Missing craft costs are expected for some items or during API outages.

### Debug & Inspection

```bash
# Inspect Universalis API responses
python scripts/debug_api.py
python scripts/debug_api_response.py

# Deep dive into aggregated vs history data structures
python scripts/inspect_data.py
```

### Legacy v1 Analysis

```bash
# Run v1 aggregated analysis (deprecated)
python legacy/main.py

# Generate v1 reports
python legacy/reports.py
```

v1 outputs to `data/market_analysis.csv` and can overstate profitability. Use for quick overview only.

## API Limits

**Universalis API** rate limits:
- 25 requests/second (burst: 50)
- 100 items/request max
- 8 simultaneous connections/IP

The client automatically respects these with built-in rate limiting.

## Contributing

See [ONBOARDING.md](ONBOARDING.md) for contributor guidance. PRs welcome!

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Retrier with backoff for XIVAPI 500s to fill craft-cost gaps
- [ ] Web dashboard with real-time market monitoring
- [ ] Historical trend tracking (7-day moving averages)
- [ ] Category-based filtering (materia, materials, crafted gear, etc.)
- [ ] Multi-world comparison within a datacenter
- [ ] Price prediction ML model
- [ ] Alert system for profitable opportunities

## Disclaimer

This project is for analysis and educational purposes. Market prices fluctuate constantly. Past profitability does not guarantee future results. Use at your own risk.

## References

- [Universalis API Documentation](https://docs.universalis.app/)
- [XIVAPI](https://xivapi.com/)
- [FFXIV Teamcraft](https://ffxivteamcraft.com/)
- [FFXIV Data Mining](https://github.com/xivapi/ffxiv-datamining)

## License

See [LICENSE](LICENSE) for details.
