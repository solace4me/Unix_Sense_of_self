# Day 2 — Environment Setup and First Trace

## Overview

The goal of Day 2 is to get strace running, stand up a simple Python HTTP
server as the target process, and produce the first raw syscall trace files
that will feed into the n-gram builder on Day 3. No analysis happens today —
this day is purely about collecting data and understanding what it looks like.

---

## 1. Confirming strace is installed

Before anything else, confirm strace is available on the machine:

```bash
strace --version
```

If strace is missing, install it:

```bash
# Ubuntu / Debian
sudo apt-get install strace

# Fedora / RHEL / CentOS
sudo yum install strace

# Arch
sudo pacman -S strace
```

---

## 2. Creating the working directory structure

All project files live under a single root folder. The `server/` subdirectory
holds the target process code; `traces/` will hold every raw strace output
file collected during the project.

```bash
mkdir ~/sense-of-self
cd ~/sense-of-self
mkdir server traces
```

---

## 3. The Python HTTP server

The target process for this replication is a minimal Python HTTP server
defined in [server/httpserver.py](server/httpserver.py).

The server exposes three routes that deliberately produce different syscall
patterns during normal operation:

- `GET /` — returns a static string; exercises socket write syscalls only
- `GET /status` — same as above, different response byte
- `GET /read` — opens `/etc/hostname` from disk and returns its content;
  exercises `openat`, `read`, and `close` syscalls in addition to the socket
  writes

This variation across routes is the modern equivalent of Forrest et al.'s
112 email message types — it ensures the normal database captures a range of
legitimate syscall sequences rather than just one narrow path through the
server's code.

---

## 4. Running a quick test without strace

Before attaching strace, confirm the server works correctly on its own.

**Terminal A** — start the server:

```bash
python3 server/httpserver.py
```

**Terminal B** — send test requests:

```bash
curl http://localhost:8080/
curl http://localhost:8080/status
curl http://localhost:8080/read
curl http://localhost:8080/doesnotexist
```

Confirm that `/` and `/status` return 200, `/read` returns the hostname, and
any unknown path returns 404. Then stop the server with `Ctrl+C` in Terminal A.

---

## 5. Running the server under strace

Start the server again, this time with strace wrapping it:

```bash
strace -f \
       -e trace=all \
       -o traces/normal_run_01.txt \
       python3 server/httpserver.py
```

Flag reference:

| Flag | Meaning |
|------|---------|
| `-f` | Follow child processes if the server forks |
| `-e trace=all` | Capture every syscall, no filtering |
| `-o <file>` | Write output to a file instead of the terminal |

---

## 6. Sending the controlled normal corpus

With the server running under strace, send the following sequence of requests
from Terminal B. This is the Day 2 version of Forrest et al.'s normal corpus —
a controlled set of inputs that exercises all legitimate routes:

```bash
curl http://localhost:8080/
curl http://localhost:8080/status
curl http://localhost:8080/
curl http://localhost:8080/read
curl http://localhost:8080/status
curl http://localhost:8080/
curl http://localhost:8080/read
curl http://localhost:8080/doesnotexist
curl http://localhost:8080/
curl http://localhost:8080/status
```

Stop the server with `Ctrl+C` in Terminal A when done.

Then repeat Steps 5 and 6 and save the second run as `traces/normal_run_02.txt`.
Having two independent normal traces lets Day 3 verify that the n-gram database
is stable — the two runs should produce nearly identical sets of sequences,
which is the core claim of Figure 1 in the paper.

---

## 7. Examining the raw trace output

```bash
head -50 traces/normal_run_01.txt
```

Each line in the output follows this format:

```
[pid]  syscall_name(arguments) = return_value
```

For example:

```
12345 openat(AT_FDCWD, "/etc/hostname", O_RDONLY) = 3
12345 read(3, "myhost\n", 4096)         = 7
12345 close(3)                          = 0
12345 write(5, "HTTP/1.0 200 OK\r\n", 17) = 17
```

To see which syscalls appear most frequently, extract and count them:

```bash
grep -oP '^\d+ +\K\w+' traces/normal_run_01.txt | sort | uniq -c | sort -rn
```

The most frequent names will be `read`, `write`, `accept4`, `epoll_wait`,
`openat`, and `close`. These will form the backbone of the n-gram sequences
built on Day 3.

---

## End of Day 2

By the end of this day the following is in place:

- strace confirmed working
- `server/httpserver.py` running cleanly as the target process
- Two raw trace files in `traces/` representing two independent normal runs
- A clear picture of what raw strace output looks like before any parsing

Day 3 picks up by writing the Python n-gram builder that reads these trace
files and constructs the normal database described in Section 3 of the paper.
