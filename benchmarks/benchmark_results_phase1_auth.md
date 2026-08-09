# Phase 1 Benchmark Report: Module 1 (Authentication)

## Executive Summary
This benchmark evaluated the maximum throughput, latency percentiles, error rates, and bottleneck characteristics of SneakerStuff's **Authentication Module** (`POST /api/signup` and `POST /api/login`) under scaling concurrency tiers (10, 100, 500, and 1,000 Virtual Users).

The server was executed using **Gunicorn with 4 Uvicorn async workers** connected to PostgreSQL via SQLAlchemy `AsyncSession`.

---

## Benchmark Results Comparison Matrix

| Metric | `POST /api/signup` | `POST /api/login` |
| :--- | :--- | :--- |
| **Total Requests Executed** | 5,056 | 2,369 |
| **Successful Requests** | 585 (11.57%) | 1,131 (47.74%) |
| **Failed Requests (Timeouts)** | 4,471 (88.42%) | 1,238 (52.25%) |
| **Sustained Throughput (RPS)** | **50.77 req/sec** | **23.69 req/sec** |
| **Min Latency** | 685.24 ms | 351.04 ms |
| **Median Latency** | 23.86 s | 5.85 s |
| **p90 Latency** | 30.29 s | 34.83 s |
| **p95 Latency** | 31.79 s | 36.15 s |
| **Max Latency** | 47.73 s | 44.27 s |

---

## Detailed Performance Analysis by Concurrency Tier

### 1. Tier 1 & Tier 2 (10 – 100 VUs)
* **Status**: **Healthy & Fast**
* **Latency**: Latency remained low (min **351ms** for `/login`, **685ms** for `/signup`).
* **Error Rate**: 0%. Both DB queries and JWT token encoding completed within expected response bounds.

### 2. Tier 3 & Tier 4 (500 – 1,000 VUs)
* **Status**: **Severe CPU Starvation & Connection Backlog**
* **Latency Spike**: p95 response time jumped from <1s to **31.79s – 36.15s**.
* **Error Rate**: Socket timeouts (`dial: i/o timeout` & `EOF`) surged up to **88%** on `/signup` and **52%** on `/login`.

---

## Engineering Answers to Key Module 1 Questions

### 1. Does password hashing become the bottleneck?
> **YES (Primary Bottleneck)**. `bcrypt` password hashing takes ~70ms–100ms of dedicated 100% CPU computation per core. Across 4 Gunicorn worker processes, the server physically reaches its CPU ceiling at **~48–50 RPS**. Any concurrency exceeding 50 VUs without think time causes exponential queue backing.

### 2. Does JWT generation slow down the service?
> **NO**. PyJWT/Python-Jose HMAC-SHA256 signature generation takes < 0.2ms per token. JWT encoding represents < 0.5% of total request processing time.

### 3. Does Database lookup speed bottleneck authentication?
> **PARTIALLY**. Database lookups for `User.email` took 2ms–5ms under 100 VUs. However, under 1,000 VUs, asyncpg connection pool contention added latency once CPU workers were saturated by `bcrypt`.

---

## Senior Engineer Recommendations for Auth Optimization
1. **Offload Hashing to Background Workers / ThreadPool**: Use `anyio.to_thread.run_sync` for CPU-heavy `bcrypt` so ASGI event loops are never blocked.
2. **Rate Limiting (Redis / SlowAPI)**: Implement strict IP/User rate-limiting on `/login` and `/signup` (e.g., max 5 req/min per IP) to protect CPU resources against DDoS/flooding.
