# SneakDrop ⚡
> **Bot-Free Sneaker Raffle & Limited Drop Platform**  
> *A high-concurrency, raffle-based e-commerce platform built to eliminate scalper bots, guarantee fair allocation for limited-hype releases, and streamline order processing from entry to checkout.*

[![Backend Framework](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Database](https://img.shields.io/badge/PostgreSQL-AsyncPG-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org)
[![Frontend](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![Task Queue](https://img.shields.io/badge/Celery-Redis-37814A.svg?style=flat&logo=celery)](https://docs.celeryq.dev)
[![Deployment](https://img.shields.io/badge/Vercel-Deployment-000000.svg?style=flat&logo=vercel)](https://vercel.com)

---

## 📖 Overview

### The Problem
The limited-edition sneaker and streetwear industry (Air Jordans, Yeezys, Travis Scott collabs) is plagued by automated checkout bots, scalpers, and server crashes. Traditional first-come, first-served e-commerce checkout flows are weaponized by scripts executing thousands of requests per second, locking out genuine sneaker enthusiasts and overwhelming infrastructure.

### The Solution
**SneakDrop** solves this by shifting from standard instant checkout to a **transparent, concurrency-safe raffle draw system**:
1. **Browse & Discover**: Sneakerheads explore upcoming, active, or closed sneaker drops.
2. **Bot-Free Entry**: Authenticated, verified users register a single draw entry per drop with a validated shipping address before the timer expires.
3. **Async Winner Selection**: When a drop closes, background Celery workers trigger a deterministic, concurrency-safe draw algorithm using database row locks (`SELECT FOR UPDATE`).
4. **Reservation & Price Snapshotting**: Selected winners receive a temporary, price-locked inventory reservation.
5. **Checkout & Fulfillment**: Winners convert their reservation into a confirmed order, settling payment seamlessly via Razorpay integration.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend API** | FastAPI | High-performance async Python REST framework with automatic OpenAPI docs |
| **Database ORM** | SQLAlchemy 2.0 (Async) | Async object-relational mapping with PostgreSQL dialect support |
| **DB Driver** | `asyncpg` | Ultra-fast native async driver for PostgreSQL |
| **Database** | PostgreSQL / Supabase | Relational data store supporting row-level concurrency locking |
| **Task Queue** | Celery + Redis | Asynchronous background worker processing for automated drop draw execution |
| **Caching / Broker** | Redis | High-speed message broker and semantic cache for drop state & sessions |
| **Payment Gateway** | Razorpay SDK | Secure online payment settlement (amounts computed in paise) |
| **Frontend UI** | React 19 + Vite | SPA built with modern hooks, fast HMR, and Nike/Foot Locker athletic styling |
| **State & Data Fetching** | TanStack React Query | Client-side cache management, optimistic updates, and background refetching |
| **Styling & Motion** | Vanilla CSS + Framer Motion | Custom streetwear design tokens, micro-interactions, and SNKRS drop timers |
| **Testing** | pytest + `httpx.AsyncClient` | Custom test suite built from scratch covering unit, route, and task integration |
| **Deployment** | Vercel | Production deployment configured with Vercel Python serverless & static SPA rewrites |

---

## 🏗️ Architecture & Key Engineering Decisions

### High-Level Architecture

```
                    ┌──────────────────────────────────────────┐
                    │               React 19 SPA               │
                    │      (Nike/SNKRS Athletic Styling)       │
                    └────────────────────┬─────────────────────┘
                                         │ HTTP / REST (JWT Bearer)
                                         ▼
                    ┌──────────────────────────────────────────┐
                    │          FastAPI ASGI Server             │
                    │   (Async Routes, Pydantic Validation)    │
                    └────────────┬────────────────────┬────────┘
                                 │                    │
             Async Query (asyncpg)                    │ Trigger Tasks
                                 ▼                    ▼
    ┌──────────────────────────────────────┐   ┌───────────────────────────────┐
    │       PostgreSQL Database            │   │      Redis Message Broker     │
    │  (Row Locks SELECT FOR UPDATE)       │   └──────────────┬────────────────┘
    └──────────────────▲───────────────────┘                  │
                       │                                      │ Dispatch
                       │ NullPool Session Connection          ▼
                       └───────────────────────────┌───────────────────────────┐
                                                   │    Celery Async Worker    │
                                                   │   (Drop Draw Processing)  │
                                                   └───────────────────────────┘
```

### Key Architectural Decisions

1. **Async SQLAlchemy + `asyncpg` for High Throughput**:
   All database operations use non-blocking async/await calls. This ensures FastAPI handles thousands of concurrent draw entries without blocking main execution threads during high-velocity shock drops.

2. **NullPool Engine for Celery Background Workers**:
   To prevent PostgreSQL event-loop binding conflicts across Celery process forks, the worker uses a dedicated SQLAlchemy engine configured with `NullPool`. This avoids inter-process socket reuse issues while maintaining strict transaction isolation.

3. **Concurrency-Safe Winner Selection (`SELECT FOR UPDATE`)**:
   During automated raffle draw processing, the database row for each eligible entry and product inventory is locked via `SELECT FOR UPDATE`. This guarantees zero race conditions or over-allocations when multiple workers evaluate inventory allocations simultaneously.

4. **Price Snapshotting on Reservation & Order Propagation**:
   When a raffle winner is drawn, a `Reservation` is created with a hardcoded snapshot of the product price at draw time (`unit_price`). This price propagates strictly down to `Order`, `OrderItem`, and Razorpay charge calculations, protecting users from mid-checkout price mutations.

5. **Single Source of Truth for Order Status**:
   Order lifecycle states are collapsed into a unified status enum (`PENDING_PAYMENT`, `PAID`, `CANCELLED`, `COMPLETED`), eliminating state sync bugs between payment webhooks and inventory allocation tables.

6. **Non-Blocking Razorpay Payment Processing (`asyncio.to_thread`)**:
   Razorpay's official Python SDK relies on synchronous HTTP requests. To avoid blocking FastAPI's async event loop during payment order creation or verification, SDK calls are safely dispatched via `asyncio.to_thread()`.

---

## ✨ Core Features

- 👟 **Drop Management & Publishing**: Admin control panel for staging drops in `DRAFT`, scheduling launch windows, locking dedicated inventory, and transitioning status (`SCHEDULED` ➔ `ENTRY_OPEN` ➔ `ENTRY_CLOSED` ➔ `COMPLETED`).
- 🎟️ **Bot-Free Raffle Entry System**: Enforces 1 entry per authenticated user per drop with shipping address verification.
- 🎲 **Automated Winner Draw Algorithm**: Celery background task randomly selects winners up to the specified `drop_inventory` count, automatically creating reserved allocations.
- 💳 **Razorpay Checkout Integration**: Seamless payment processing supporting test and live modes. Automatic conversion of USD/INR values into integer paise for precision.
- 📊 **Order Lifecycle Management**: Order creation from winning reservations, tracking payment status, and automated inventory reconciliation.

---

## 🛠️ Backend Structure & Database Schema

### Database Models & Relationships

```
┌───────────────┐        1:N        ┌───────────────┐
│     User      │──────────────────>│    Entry      │
└───────┬───────┘                   └───────┬───────┘
        │ 1:N                               │
        ▼                                   ▼ 1:1
┌───────────────┐        1:1        ┌───────────────┐
│     Drop      │──────────────────>│  Reservation  │
└───────┬───────┘                   └───────┬───────┘
        │ 1:1                               │
        ▼                                   ▼ 1:1
┌───────────────┐        1:N        ┌───────────────┐
│    Product    │<──────────────────│    Order      │
└───────────────┘                   └───────────────┘
```

- **User**: Authentication credentials (`username`, `email`, `hashed_password`), role (`user` / `admin`).
- **Product**: Master inventory record (`product_id`, `name`, `price`, `stock`, `images`).
- **Drop**: Raffle drop window (`opens_at`, `closes_at`, `drop_inventory`, `status`).
- **Entry**: User raffle submission (`drop_id`, `user_id`, `address`, `created_at`).
- **Reservation**: Winning raffle allocation (`entry_id`, `user_id`, `unit_price`, `expires_at`).
- **Order / OrderItem**: Purchased order records (`total_amount`, `status`, `razorpay_order_id`).

---

## 🎨 Frontend Design & Styling

SneakDrop features a custom-built React 19 UI tailored to match the high-energy, athletic-streetwear aesthetic of **Nike SNKRS** and **FootLocker.com**:

- **Brand Logo**: Custom `<SneakDropLogo />` SVG wordmark combining sharp geometric typography with an aggressive swoosh/lightning icon.
- **Color Palette**: High-contrast Pitch Black (`#0A0A0A`), Electric Voltage Red (`#FF2A00`), Volt Green (`#CCFF00`), and Pure White (`#FFFFFF`).
- **Typography**: Heavy condensed display headlines using `Bebas Neue` paired with `Inter` for clear descriptions and pricing.
- **SNKRS Drop Clock**: Interactive live countdown timers (Hours : Mins : Secs) with smooth state transitions.
- **Micro-Interactions**: Hover scale image zoom on drop cards (`.hover-zoom`), button press feedback, and real-time toast notifications.

---

## 🧪 Testing Suite & Bug Case Studies

The SneakDrop test suite was **built completely from scratch** using `pytest`, `pytest-asyncio`, and `httpx.AsyncClient`, achieving deep coverage across services, API routes, and background Celery tasks.

### 🐛 Production Bugs Surfaced by Test Suite

Building tests against the codebase exposed critical edge-case bugs that were fixed prior to release:

1. **Off-by-One Error in Drop Publishing Logic**:
   - *Bug*: Inventory validation in `drop_publish` checked `if drop.drop_inventory < 0:` instead of `<= 0`.
   - *Impact*: Allowed admins to publish drops with `0` allocated inventory, breaking subsequent winner draws.
   - *Fix*: Corrected assertion to strictly disallow zero or negative drop inventory.

2. **Status Assignment vs. Comparison Bug in Winner Selection**:
   - *Bug*: A conditional check in the draw service mistakenly performed variable assignment `if drop.status = DropStatus.ENTRY_CLOSED:` instead of equality comparison `==`.
   - *Impact*: Overwrote drop status during draw execution, corrupting state transitions.
   - *Fix*: Corrected to proper equality evaluation `drop.status == DropStatus.ENTRY_CLOSED`.

3. **Phantom Stock Inflation during Drop Cancellation**:
   - *Bug*: Cancelling or deleting a drop unconditionally refunded `drop_inventory` back to `product.stock`, even if stock had never been reserved in the first place.
   - *Impact*: Artificially inflated overall product stock on every cancellation cycle.
   - *Fix*: Added status checks (`STOCK_RESERVED_STATES`) to ensure stock is only restored if it was previously deducted during publishing.

### Running Tests Locally

Run the complete backend test suite from the project root:

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: C:\Users\desai\venv\Scripts\Activate.ps1

# Run pytest
python -m pytest -v
```

---

## 📋 Requirements & Prerequisites

Ensure the following tools are installed on your environment:
- **Python**: `v3.10+`
- **Node.js**: `v18.0+`
- **PostgreSQL**: `v14+` (or Supabase URI)
- **Redis**: `v6+`
- **Razorpay Account**: Test key ID & secret key for sandbox payments

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/devdesai25/sneakerstuff.git
cd sneakerstuff
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 3. Environment Variables Configuration
Create a `.env` file in the root directory:

```env
# Database & Redis
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/sneakdrop
REDIS_URL=redis://localhost:6379/0

# Security & JWT
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Razorpay Sandbox Credentials
RAZORPAY_KEY_ID=rzp_test_YourKeyIdHere
RAZORPAY_KEY_SECRET=YourKeySecretHere

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

### 4. Database Migrations
```bash
# Run Alembic migrations to create tables
alembic upgrade head
```

### 5. Start Backend API Server
```bash
# Run FastAPI server with hot reload
uvicorn backend.main:app --reload --port 8000
```

### 6. Start Celery Worker & Redis
```bash
# Terminal 1: Ensure Redis is running
redis-server

# Terminal 2: Start Celery Worker
celery -A backend.celery_app worker --loglevel=info
```

### 7. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📁 Project Structure

```
ecommerce-backend-fastapi/
├── alembic/                  # Database migration scripts
├── backend/
│   ├── api/
│   │   └── index.py          # Vercel Python serverless entrypoint
│   ├── auth/                 # JWT token encoding & password hashing
│   ├── models/               # SQLAlchemy ORM models (User, Drop, Entry, Order)
│   ├── routes/               # FastAPI route handlers (/drops, /cart, /orders)
│   ├── schemas/              # Pydantic request/response validation DTOs
│   ├── services/             # Core business logic & database transactions
│   ├── tasks/                # Celery background draw tasks
│   ├── tests/                # Complete backend pytest test suite
│   ├── celery_app.py         # Celery instance configuration
│   ├── database.py           # Async SQLAlchemy engine & session maker
│   └── main.py               # FastAPI application initialization
├── frontend/
│   ├── public/               # Favicons & static assets
│   ├── src/
│   │   ├── components/       # Reusable components (ProductCard, Navbar, Logo)
│   │   ├── context/          # Auth & user session context provider
│   │   ├── pages/            # Page views (Home, Drops, Cart, ProductDetails)
│   │   ├── services/         # Axios API client setup
│   │   ├── index.css         # Nike/SNKRS streetwear design tokens
│   │   └── App.jsx           # Main React router & layout structure
│   └── package.json
├── vercel.json               # Vercel deployment & SPA routing rewrites
├── docker-compose.yml        # Docker setup for local PostgreSQL/Redis
└── README.md                 # Project documentation
```

---

## 🚀 Example API Requests

### 1. Register Entry for Raffle Drop (`POST /api/drops/{id}/entries`)
```bash
curl -X POST "http://localhost:8000/api/drops/1/entries" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"address": "742 Evergreen Terrace, Springfield"}'
```

### 2. Create Razorpay Payment Order (`POST /api/orders`)
```bash
curl -X POST "http://localhost:8000/api/orders" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"reservation_id": 10}'
```

---

## 🔮 Future Roadmap

- 📱 **Native Push Notifications**: Integrate WebPush and FCM for instant shock drop alerts.
- ⚡ **WebSocket Live Draw**: Real-time canvas animation during active raffle winner selection.
- 🛡️ **Advanced Fraud Detection**: IP rate-limiting and device fingerprinting to enforce 100% human drawing entries.

---

## 📄 License & Author

Built with ❤️ by **Dev Desai** ([@devdesai25](https://github.com/devdesai25)).  
This project is licensed under the **MIT License**.
