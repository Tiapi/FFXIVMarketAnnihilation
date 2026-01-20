"""
Deprecated entrypoint (v1) — use main_v2.py instead.

This file is kept to avoid breaking references. For the
aggregated v1 analysis, see legacy/main.py. For the
history-based v2 analysis, run main_v2.py.
"""
import sys

if __name__ == "__main__":
    print("This entrypoint is deprecated. Run: python main_v2.py", file=sys.stderr)
    sys.exit(2)
