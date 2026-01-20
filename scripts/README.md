# Debug & Inspection Scripts

Utilities for inspecting Universalis API responses and understanding data structure.

## Scripts

### `debug_api.py`

Fetches world and datacenter lists from Universalis to verify API connectivity and datacenter names.

**Usage:**
```bash
python scripts/debug_api.py
```

**Output:**
- List of worlds
- List of datacenters
- Verification of datacenter existence (e.g., "Chaos")

---

### `debug_api_response.py`

Fetches aggregated market data for a few items and pretty-prints the JSON response.

**Usage:**
```bash
python scripts/debug_api_response.py
```

**Output:**
- Raw JSON structure from `/aggregated` endpoint
- Shows fields like `minListing`, `averageSalePrice`, `dailySaleVelocity`

---

### `inspect_data.py`

Deep dive comparing aggregated vs history endpoints. Explains differences and recommends history-based approach.

**Usage:**
```bash
python scripts/inspect_data.py
```

**Output:**
1. Sample aggregated data structure
2. Sample history data structure
3. Detailed explanation of pros/cons

**Purpose:**
- Understand why v2 (history) is more accurate than v1 (aggregated)
- See actual API response formats
- Debug data issues

---

## When to Use

- Troubleshooting API connectivity
- Understanding data schema before writing new analyzers
- Comparing aggregated vs history data for specific items
- Verifying datacenter names and world IDs

## Requirements

Same as main project (`requirements.txt`). Run from project root after activating venv.
