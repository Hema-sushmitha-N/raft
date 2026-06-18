# Baseline Latency Report — Week 1
## WR-Raft Project | Intern C | 5-Node Uniform Cluster

---

## Setup

| Parameter | Value |
|---|---|
| Cluster size | 5 nodes |
| Hardware | Uniform (Docker containers, Windows 11 host) |
| Storage | tmpfs (RAM-backed WAL, no real disk I/O) |
| Benchmark | YCSB Workload-A (50% read / 50% write) |
| Target throughput | 1000 ops/sec |
| Duration | 60 seconds |
| Total ops completed | 58,454 |

---

## Baseline Latency Table

### Write Latency (nanoseconds)

| Node | p50 | p99 | p999 |
|------|-----|-----|------|
| node1 (9091) | 539,500 | 1,209,500 | 3,910,100 |
| node2 (9092) | 537,900 | 1,316,800 | 3,923,300 |
| node3 (9093) | 538,100 | 1,547,300 | 5,453,500 |
| node4 (9094) | 538,700 | 1,446,400 | 5,459,600 |
| node5 (9095) | 537,500 | 1,398,000 | 6,200,000 |

### Read Latency (nanoseconds)

| Node | p50 | p99 | p999 |
|------|-----|-----|------|
| node1 (9091) | 538,600 | 1,487,600 | 4,353,600 |
| node2 (9092) | 538,400 | 1,388,400 | 3,542,000 |
| node3 (9093) | 538,700 | 1,306,800 | 3,793,600 |
| node4 (9094) | 538,900 | 1,337,000 | 4,149,400 |
| node5 (9095) | 538,500 | 1,420,600 | 3,742,700 |

### fsync Latency — WAL Storage Layer (nanoseconds)

| Node | p50 | p99 | p999 |
|------|-----|-----|------|
| node1 (9091) | 128,000 | 512,000 | 1,024,000 |
| node2 (9092) | 128,000 | 512,000 | 2,048,000 |
| node3 (9093) | 128,000 | 512,000 | 1,024,000 |
| node4 (9094) | 128,000 | 512,000 | 2,048,000 |
| node5 (9095) | 128,000 | 512,000 | 2,048,000 |

---

## Key Observations

### 1. Cluster is Uniform
All 5 nodes show nearly identical p50 write latency (~538,000 ns).
This confirms the baseline is a fair starting point before
injecting heterogeneity in Week 2.

### 2. fsync is Fast on tmpfs
p50 fsync = 128,000 ns (~0.13ms). This is expected since tmpfs
is RAM-backed — no real disk I/O occurs. Real SSDs would show
higher and more variable latency.

### 3. Tail Latency Variance is Normal
p999 write latency varies from 3.9ms to 6.2ms across nodes.
This is normal OS scheduling jitter on a shared Windows host
running Docker containers. Not a concern for baseline.

### 4. p99 Write Latency: ~1.2ms to 1.5ms
Reasonable for a network round-trip + fsync inside Docker
on a single machine. This will be our comparison baseline
when WR-Raft is introduced in later weeks.

---

## What This Baseline Proves

- Vanilla Raft on uniform hardware has uniform commit latency
- All nodes contribute equally to the quorum
- No node is faster or slower than others
- This is the "before" state — Week 2 will inject latency
  differences to simulate heterogeneous hardware

---

## Prometheus Dashboard

Metrics exposed at:
- node1: http://localhost:9091/metrics
- node2: http://localhost:9092/metrics
- node3: http://localhost:9093/metrics
- node4: http://localhost:9094/metrics
- node5: http://localhost:9095/metrics

Key metric: fsync_duration_ns histogram (buckets, sum, count)

---

*Generated: 2026-06-18 | Intern C | WR-Raft Week 1*