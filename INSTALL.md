# Installation Guide - FFXIV Market Annihilation

## Prerequisites

- Python 3.11 or higher
- Git (for cloning the repository)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd FFXIVMarketAnnihilation
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux/MacOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

Create a `.env` file in the root directory (optional for API keys):

```bash
# Add any API keys or configuration here if needed
# DATACENTER=Chaos
```

### 5. Run the Analysis

**Basic Market Analysis (v2 - History-Based):**
```bash
python main_v2.py
```

**Generate Advanced Reports:**
```bash
python reports_v2.py
```

**Compare v1 vs v2:**
```bash
python compare_versions.py
```

## Project Structure

```
FFXIVMarketAnnihilation/
├── src/
│   ├── analyzer_v2.py      # Main history-based market analyzer
│   ├── craft_cost.py        # Craft cost estimation
│   ├── item_mapper.py       # Item name resolution
│   └── universalis.py       # Universalis API client
├── data/                    # Output CSV files
├── main_v2.py              # Entry point for v2 analysis
├── reports_v2.py           # Advanced report generator
├── requirements.txt        # Python dependencies
└── .env                    # Configuration (create this)
```

## Output Files

- `data/market_analysis_v2.csv` - Detailed market analysis with profitability metrics
- `data/reports_v2.txt` - Human-readable comprehensive reports

## Troubleshooting

### XIVAPI 500 Errors
If you see many warnings about recipe fetch failures, this is normal - XIVAPI can be unstable. The analysis will continue with available data.

### Missing Item Names
The tool automatically fetches item names from XIVAPI and ffxiv-teamcraft. If some names are missing, it will use item IDs instead.

### Virtual Environment Not Activating
Make sure you're using the correct activation command for your operating system (see step 2).

## Contributing

Feel free to open issues or submit pull requests to improve the analyzer!

## Data Source

This tool uses the [Universalis API](https://universalis.app/) for market data and [XIVAPI](https://xivapi.com/) for item/recipe information.
