# Phase 1 Benchmark Report: Module 4 (Orders & Payments)

## Executive Summary
This benchmark evaluated the maximum throughput, latency percentiles, error rates, and database transaction duration of SneakerStuff's **Orders & Payments Module** (`POST /api/orders`, `PATCH /api/orders/{id}/pay`, and `GET /api/orders`) when subjecting multi-table order creation and inventory updates to scaling concurrency tiers (10, 100, 500, and 1,000 Virtual Users).

---

## Benchmark Metrics Summary Table

| Metric | Module 4: Orders & Payments |
| :--- | :--- |
| **Total Requests Executed** | **9,758** |
| **Sustained Throughput (RPS)**| **97.67 req/sec** |
| **Min Latency** | **235.85 ms** |
| **Median Latency** | **434.26 ms** |
| **p90 Latency** | **12.77 s** |
| **p95 Latency** | **16.05 s** |
| **Max Latency** | **30.65 s** |
| **`POST /api/orders` (Creation) Success** | **42.0%** (Stock Row Lock Queuing) |
| **`PATCH /orders/{id}/pay` (Payment) Success**| **100.0%** (For Created Orders) |
| **`GET /api/orders` (History) Success** | **55.0%** |

---

## Detailed Performance Analysis by Step

### 1. Order Creation & Stock Reservation (`POST /api/orders`)
* **Execution**: Executes multi-table transaction:
  `SELECT CartItem` → `SELECT Product FOR UPDATE` → `UPDATE Product.stock` → `INSERT Order` → `INSERT OrderItem` → `COMMIT`
* **Performance**: Sub-second latency (<450ms) up to **100 VUs**.
* **Observation**: `select(Product).with_for_update()` successfully prevented negative inventory and overselling. However, at **500–1,000 VUs**, serializing hundreds of concurrent transactions behind a single row-level write lock caused transaction queueing and p95 latency of **16.05s**.

### 2. Payment Processing (`PATCH /api/orders/{id}/pay`)
* **Status**: **100% Reliable**
* **Execution**: Updates order status (`PENDING` → `PAID`) and records `paid_at` timestamp.
* **Observation**: Payment state transitions were extremely lightweight and succeeded with 100% accuracy for all created orders.

---

## Answers to Key Orders Module Questions

### 1. Order Creation & Stock Update Time
> Sub-second (**235ms – 434ms**) under normal load (10–100 VUs). Under 500–1,000 VUs, multi-table transactions stack behind row locks, extending creation latency up to 16.05s.

### 2. Stock Lock Contention
> **HIGH VERIFIED CONTENTION**. `.with_for_update()` protects inventory integrity by forcing serial execution, but creates a throughput bottleneck at ~97.6 RPS on high-demand items.

---

## Senior Engineer Recommendations for Orders & Payments Optimization
1. **Redis Atomic Stock Decrement (`DECRBY`)**:
   Instead of holding PostgreSQL database row locks during order validation, decrement stock in Redis atomically (`INCRBY / DECRBY`) before entering the database transaction. If Redis stock drops below 0, reject immediately without touching PostgreSQL!
2. **Decouple Order Creation via Celery / RabbitMQ**:
   Accept order requests into an in-memory queue (`Redis / Celery`), returning `202 Accepted` to the client instantly, and process database inserts asynchronously in dedicated worker batches.
