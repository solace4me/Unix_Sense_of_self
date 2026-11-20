"""
run_analysis.py
---------------
Runner script for Day 3.

Loads the two normal trace files from traces/, builds the n-gram database
for window sizes 5, 6, and 11, and prints a summary table showing:
  - database size for each window size
  - mismatch percentage when each normal trace is scored against its own database
    (these should be near 0% — confirming the database is stable)

Run from the project root:
    python3 analysis/run_analysis.py
"""

import sys
from pathlib import Path

# Allow importing sense_of_self from the same directory
sys.path.insert(0, str(Path(__file__).parent))

from sense_of_self import parse_trace, build_ngram_database, score_trace

TRACES_DIR = Path(__file__).parent.parent / 'traces'
WINDOW_SIZES = [5, 6, 11]

def main():
    normal_files = sorted(TRACES_DIR.glob('normal_run_*.txt'))

    if not normal_files:
        print(f"No normal_run_*.txt files found in {TRACES_DIR}")
        sys.exit(1)

    print(f"Found {len(normal_files)} normal trace file(s):")
    for f in normal_files:
        print(f"  {f.name}")
    print()

    # Parse all normal traces once
    sequences = {f.name: parse_trace(f) for f in normal_files}
    for name, seq in sequences.items():
        print(f"  {name}: {len(seq):,} syscalls extracted")
    print()

    # Build and score for each window size
    for n in WINDOW_SIZES:
        print(f"{'='*50}")
        print(f"Window size n = {n}")
        print(f"{'='*50}")

        db = build_ngram_database(list(sequences.values()), n=n)
        print(f"  Normal database size : {len(db):,} unique {n}-grams")
        print()

        print(f"  {'Trace file':<30} {'Mismatches':>12} {'Total':>10} {'%':>8}")
        print(f"  {'-'*30} {'-'*12} {'-'*10} {'-'*8}")

        for name, seq in sequences.items():
            result = score_trace(seq, db, n=n)
            print(f"  {name:<30} {result['mismatches']:>12,} {result['total']:>10,} {result['percentage']:>7.2f}%")

        print()

if __name__ == '__main__':
    main()
