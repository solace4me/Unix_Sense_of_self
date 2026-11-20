"""
sense_of_self.py
----------------
Core algorithm for the Sense of Self replication.

Implements the three building blocks from Forrest et al. (1996):
  1. Trace parsing   — extracts syscall names from strace output
  2. Database build  — builds a set of unique n-grams from normal traces
  3. Mismatch score  — counts foreign n-grams in a test trace

Also provides a database growth tracker for reproducing Figure 1.
"""

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Trace Parsing
# ---------------------------------------------------------------------------

def parse_trace(filepath):
    """
    Read a strace output file and return an ordered list of syscall names.

    strace lines look like:
        12345 openat(AT_FDCWD, "/etc/hostname", O_RDONLY) = 3
        12345 read(3, "myhost\\n", 4096)                  = 7

    We extract only the syscall name (the identifier before the first '(').
    Lines that are signals, exit notices, unfinished calls, or resumed
    calls are skipped because they do not represent complete syscall events.
    """
    syscalls = []
    pattern = re.compile(r'^\s*(?:\d+\s+)?([a-z_][a-z0-9_]*)\s*\(')

    with open(filepath, 'r', errors='replace') as f:
        for line in f:
            stripped = line.strip()
            # Skip non-syscall lines
            if stripped.startswith(('---', '+++')):
                continue
            if '<unfinished' in line or 'resumed>' in line:
                continue
            m = pattern.match(line)
            if m:
                syscalls.append(m.group(1))

    return syscalls


# ---------------------------------------------------------------------------
# 2. N-gram Database
# ---------------------------------------------------------------------------

def build_ngram_database(syscall_sequences, n=6):
    """
    Build a set of unique n-grams from one or more syscall sequences.

    A syscall sequence is a list of syscall name strings. A window of
    length n is slid across each sequence one step at a time; each window
    becomes a tuple that is added to the database set.

    Args:
        syscall_sequences : list of lists — one list of names per trace file
        n                 : window size (Forrest tested 5, 6, and 11)

    Returns:
        frozenset of tuples — the normal database
    """
    database = set()
    for sequence in syscall_sequences:
        for i in range(len(sequence) - n + 1):
            ngram = tuple(sequence[i : i + n])
            database.add(ngram)
    return frozenset(database)


# ---------------------------------------------------------------------------
# 3. Mismatch Scoring
# ---------------------------------------------------------------------------

def score_trace(syscalls, database, n=6):
    """
    Count how many n-gram windows in a test trace are NOT in the database.

    Args:
        syscalls  : list of syscall name strings (from parse_trace)
        database  : frozenset of n-gram tuples (from build_ngram_database)
        n         : window size — must match the size used to build the db

    Returns:
        dict with keys:
            mismatches  — raw count of foreign n-grams
            total       — total windows checked
            percentage  — mismatches / total * 100, rounded to 2 dp
    """
    mismatches = 0
    total = 0

    for i in range(len(syscalls) - n + 1):
        ngram = tuple(syscalls[i : i + n])
        total += 1
        if ngram not in database:
            mismatches += 1

    percentage = round((mismatches / total * 100), 2) if total > 0 else 0.0
    return {
        'mismatches': mismatches,
        'total':      total,
        'percentage': percentage,
    }


# ---------------------------------------------------------------------------
# 4. Database Growth Tracking  (reproduces Figure 1)
# ---------------------------------------------------------------------------

def track_database_growth(syscalls, n=6, step=200):
    """
    Simulate building the database one syscall at a time and record its
    size at regular intervals. The resulting (x, y) data reproduce the
    shape of Figure 1 in the paper: rapid growth early, then a plateau.

    Args:
        syscalls : list of syscall name strings from concatenated normal traces
        n        : window size
        step     : how often (in syscalls) to record a data point

    Returns:
        x : list of syscall-count values
        y : list of database-size values at each x
    """
    database = set()
    x = []
    y = []

    for i in range(len(syscalls) - n + 1):
        ngram = tuple(syscalls[i : i + n])
        database.add(ngram)
        if i % step == 0:
            x.append(i)
            y.append(len(database))

    # Always include the final point
    x.append(len(syscalls) - n)
    y.append(len(database))

    return x, y
