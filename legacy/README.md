# Legacy v1 Analysis (Aggregated)

This directory contains the original **v1** aggregated-data approach. It's deprecated in favor of **v2** (history-based), but kept for reference and comparison.

## Files

- **analyzer.py** – Original aggregated-data analyzer
- **main.py** – v1 entry point
- **reports.py** – v1 report generator

## Why v1 is Deprecated

v1 uses Universalis `/aggregated` endpoint:
- `averageSalePrice` can be skewed by outliers (e.g., one collector paying 10M for a vanity item)
- `minListing` represents only 1 item (not sustainable volume)
- `dailySaleVelocity` is datacenter-wide and may overstate realistic purchasing volume

**Result:** Overstates profitability and suggests unrealistic opportunities (e.g., "47M gil/day from Crescent Moon Nightgown").

## v2 Improvements

v2 uses Universalis `/history` endpoint:
- **Median pricing** (resistant to outliers)
- **Percentile-based buy/sell** (P25 for buying, median recent for selling)
- **Realistic volume** from actual transaction counts over time
- **Price distribution metrics** (P25, P50, P75) for volatility analysis

See [compare_versions.py](../compare_versions.py) for detailed comparison.

## Running v1 (For Comparison)

```bash
# Run v1 analysis
python legacy/main.py

# Generate v1 reports
python legacy/reports.py
```

**Output:** `data/market_analysis.csv` (v1 format with NQ/HQ columns)

## When to Use v1

- Quick market overview without needing precise profitability
- Comparing aggregated vs history-based approaches
- Testing API endpoints and data structure

**For actual trading decisions, use v2.**
