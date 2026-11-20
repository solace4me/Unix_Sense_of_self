# Day 3 — N-gram Builder and Normal Database

## Overview

Day 3 is where the core algorithm from Forrest et al. (1996) comes to life
in Python. The goal is to read the strace output files collected on Day 2,
extract the sequence of syscall names, build a database of normal n-grams,
and confirm that the two normal traces are consistent with each other.

By the end of the day, running the analysis against the two normal trace
files should produce near-zero mismatch percentages — which is the Day 3
equivalent of the flat region in Figure 1 of the paper.

---

## 1. Creating the analysis directory

All Python analysis scripts live in a dedicated folder to keep them
separate from the server code and trace files:

```bash
mkdir ~/sense-of-self/analysis
```

---

## 2. The core algorithm — `sense_of_self.py`

The main implementation is in [analysis/sense_of_self.py](analysis/sense_of_self.py).
It contains four functions that together reproduce the paper's methodology:

**`parse_trace(filepath)`**
Reads a strace output file line by line and extracts only the syscall name
from each line. Lines that represent signals (`--- SIGTERM ---`), process
exits (`+++ exited +++`), or incomplete calls (`<unfinished...>`) are
skipped because they do not represent a complete syscall event. The result
is a plain Python list of syscall name strings in the order they were
executed.

**`build_ngram_database(syscall_sequences, n=6)`**
Takes one or more syscall sequences (one per trace file) and slides a
window of length `n` across each one. Every window becomes a tuple that
is added to a set. The final set is the normal database — a compact
representation of every short-range syscall pattern seen during normal
operation. This directly implements Section 3 of the paper. Forrest et al.
tested window sizes of 5, 6, and 11; the same three values are used here.

**`score_trace(syscalls, database, n=6)`**
Slides the same window across a test trace and counts how many windows
produce an n-gram that is not in the database. These are mismatches. The
function returns the raw mismatch count, the total windows checked, and the
mismatch percentage. A near-zero percentage means the trace looks normal;
a high percentage flags anomalous behaviour.

**`track_database_growth(syscalls, n=6, step=200)`**
Records how many unique n-grams have been seen after every `step` syscalls.
The (x, y) output is used on Day 4 to plot the Figure 1 equivalent — a
curve that rises steeply early in the trace and then flattens as the normal
database saturates.

---

## 3. The runner script — `run_analysis.py`

[analysis/run_analysis.py](analysis/run_analysis.py) ties everything
together for Day 3. It:

1. Scans the `traces/` directory for all `normal_run_*.txt` files
2. Parses each file into a syscall sequence
3. Builds the normal database for window sizes 5, 6, and 11
4. Scores each normal trace against its own database and prints the result

Run it from the project root:

```bash
cd ~/sense-of-self
python3 analysis/run_analysis.py
```

Expected output shape (numbers will differ but the pattern should match):

```
Found 2 normal trace file(s):
  normal_run_01.txt
  normal_run_02.txt

  normal_run_01.txt: 18,432 syscalls extracted
  normal_run_02.txt: 17,901 syscalls extracted

==================================================
Window size n = 6
==================================================
  Normal database size : 312 unique 6-grams

  Trace file                     Mismatches      Total        %
  ------------------------------ ------------ ---------- --------
  normal_run_01.txt                         0     18,427    0.00%
  normal_run_02.txt                         0     17,896    0.00%
```

A 0.00% mismatch rate for both normal traces confirms that the database
captures all normal behaviour seen in those runs — exactly what the paper
demonstrates in Figure 1.

---

## 4. What the results mean at this stage

The near-zero mismatch results here are intentional and expected. The normal
traces are being scored against a database that was built from those same
traces — so by construction, every n-gram in the test trace already exists
in the database.

The more interesting result comes on Day 5, when traces from a different
process or from anomalous behaviour are scored against this database. Those
traces will produce significant mismatch percentages, reproducing Tables 2
and 3 from the paper.

---

## End of Day 3

By the end of this day the following is in place:

- `analysis/sense_of_self.py` — the four core algorithm functions
- `analysis/run_analysis.py` — the runner that produces the summary table
- Confirmed that both normal traces score at or near 0% mismatch
- A clear understanding of what the database contains before moving to
  anomaly testing

Day 4 picks up by building the normal corpus more systematically (the
equivalent of Forrest et al.'s 112-message suite) and generating the
Figure 1 growth plot using `track_database_growth`.
