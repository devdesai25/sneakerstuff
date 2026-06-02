# Ecommerce Backend FastAPI

A full-stack ecommerce application built with FastAPI backend and React frontend. This project implements a complete ecommerce solution with user authentication, product management, shopping cart functionality, and admin dashboard capabilities.

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Data Flow](#data-flow)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Running the Application](#running-the-application)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

Ecommerce Backend FastAPI is a modern, production-ready ecommerce platform that provides a robust backend API and an interactive frontend interface. The application supports user registration and authentication, product catalog management, shopping cart operations, and administrative functions for managing products and users.

The project demonstrates best practices in full-stack development including REST API design, database management, authentication and authorization, and frontend state management.

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM for database)
- Pydantic (Data validation)
- Python-Jose (JWT authentication)
- Passlib (Password hashing)
- CORS Middleware (Cross-Origin Resource Sharing)
- Alembic (Database migrations)
- Mangum (ASGI to Lambda adapter for serverless deployment)

### Frontend
- React (UI library)
- Vite (Build tool and development server)
- React Router (Client-side routing)
- Axios (HTTP client)
- Context API (State management)
- ESLint (Code quality)

### Database
- SQLAlchemy ORM
- PostgreSQL (recommended for production)
- SQLite (default for development)

### DevOps
- Docker and Docker Compose (Containerization)
- Vercel (Frontend deployment)

## Architecture

The application follows a layered architecture pattern with clear separation of concerns:

```mermaid
graph TB
    Client["Client Layer<br/>(React Frontend)"]
    Router["HTTP Routing<br/>(FastAPI Routes)"]
    Service["Service Layer<br/>(Business Logic)"]
    Database["Data Layer<br/>(SQLAlchemy ORM)"]
    DB[(Database<br/>PostgreSQL/SQLite)]
    
    Client -->|API Requests| Router
    Router -->|Process Request| Service
    Service -->|Query/Update| Database
    Database -->|SQL Operations| DB
    DB -->|Data| Database
    Database -->|Objects| Service
    Service -->|Response Data| Router
    Router -->|JSON Response| Client
    
    style Client fill:#e1f5ff
    style Router fill:#f3e5f5
    style Service fill:#e8f5e9
    style Database fill:#fff3e0
    style DB fill:#fce4ec
```

### Component Architecture

```mermaid
graph LR
    subgraph Frontend["Frontend (React)"]
        UI["UI Components"]
        Pages["Pages<br/>Home, Login, Signup, Admin"]
        Context["Context<br/>AuthContext"]
        Services["API Services<br/>Axios"]
    end
    
    subgraph Backend["Backend (FastAPI)"]
        API["FastAPI Application"]
        Routes["Route Handlers"]
        Middleware["Middleware<br/>CORS, Auth"]
        BusinessLogic["Service Layer<br/>Auth, Cart, Products"]
        Models["Data Models"]
    end
    
    subgraph Data["Data Layer"]
        ORM["SQLAlchemy ORM"]
        Schema["Database Schema"]
    end
    
    UI -->|User Interaction| Pages
    Pages -->|State Management| Context
    Context -->|API Calls| Services
    Services -->|HTTP Requests| API
    API -->|Process| Routes
    Routes -->|Middleware Check| Middleware
    Middleware -->|Route Logic| BusinessLogic
    BusinessLogic -->|Query/Update| Models
    Models -->|ORM Operations| ORM
    ORM -->|SQL| Schema
    
    style Frontend fill:#e3f2fd
    style Backend fill:#f1f8e9
    style Data fill:#fff9c4
```

## Data Flow

### Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend as React Frontend
    participant API as FastAPI Backend
    participant Auth as Auth Service
    participant DB as Database
    
    User->>Frontend: Enter credentials (login/signup)
    Frontend->>API: POST /signup or /login
    API->>Auth: Validate credentials
    Auth->>DB: Query user by username
    DB-->>Auth: User record
    alt User exists on login
        Auth->>Auth: Verify password hash
        Auth-->>API: Valid credentials
        API-->>API: Generate JWT token
    else New user on signup
        Auth->>DB: Create new user record
        DB-->>Auth: User created
        Auth-->>API: User created successfully
        API-->>API: Generate JWT token
    end
    API-->>Frontend: Return JWT token
    Frontend->>Frontend: Store token in context
    Frontend-->>User: Redirect to dashboard
```

### Product Management Flow

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend as React Frontend
    participant API as FastAPI Backend
    participant Service as Product Service
    participant Auth as Auth Service
    participant DB as Database
    
    Admin->>Frontend: Submit new product
    Frontend->>API: POST /admin/create-product
    API->>Auth: Verify JWT & admin role
    Auth-->>API: Valid admin user
    API->>Service: Create product
    Service->>DB: Insert product record
    DB-->>Service: Product created
    Service-->>API: Product response
    API-->>Frontend: Success response
    Frontend-->>Admin: Show confirmation
```

### Shopping Cart Flow

```mermaid
sequenceDiagram
    actor Customer
    participant Frontend as React Frontend
    participant API as FastAPI Backend
    participant Cart as Cart Service
    participant Auth as Auth Service
    participant DB as Database
    
    Customer->>Frontend: Add product to cart
    Frontend->>API: POST /cart/create
    API->>Auth: Verify JWT token
    Auth-->>API: Valid user
    API->>Cart: Add to cart logic
    Cart->>DB: Create/update cart item
    DB-->>Cart: Cart item record
    Cart-->>API: Updated cart
    API-->>Frontend: Cart response
    Frontend-->>Customer: Update UI
```

## Features

### User Management
- User registration with username and password
- User login with JWT token authentication
- Password hashing using bcrypt
- Role-based access control (Admin and User roles)
- User profile retrieval

### Product Management
- Browse all products with details
- Create new products (Admin only)
- Update product information (Admin only)
- Delete products (Admin only)
- Product catalog with images and descriptions
- Product stock management

### Shopping Cart
- Add products to cart
- View cart items with quantities
- Update cart item quantities
- Remove items from cart
- Unique constraint on user-product combinations

### Admin Dashboard
- Manage products (CRUD operations)
- View all users
- Monitor orders and cart activities
- Admin-only protected routes

### Security Features
- JWT-based authentication
- Password hashing with bcrypt
- CORS middleware configuration
- Protected endpoints requiring authentication
- Role-based authorization for admin functions

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 14.0 or higher
- npm or yarn package manager
- Docker and Docker Compose (optional)
- PostgreSQL (for production) or SQLite (for development)

### Backend Installation

1. Clone the repository:
```bash
git clone https://github.com/devdesai25/ecommerce-backend-fastapi.git
cd ecommerce-backend-fastapi
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS and Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Return to root directory:
```bash
cd ..
```

## Configuration

### Backend Configuration

1. Create a `.env` file in the root directory:
```bash
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here-change-in-production
SECRET_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

2. Environment Variables:
- `DATABASE_URL`: Database connection string (e.g., `postgresql://user:password@localhost/dbname`)
- `SECRET_KEY`: Secret key for JWT token generation
- `SECRET_ALGORITHM`: Algorithm for JWT encoding (HS256 recommended)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time in minutes

### Frontend Configuration

1. Update the API endpoint in `frontend/src/App.jsx`:
```javascript
const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";
```

2. Create a `.env` file in the frontend directory:
```bash
REACT_APP_API_URL=http://localhost:8000
```

### Database Configuration

1. For SQLite (development):
No additional configuration required.

2. For PostgreSQL (production):
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/ecommerce_db
```

## API Endpoints

### Authentication Routes

- `POST /signup` - Register a new user
  - Body: `{username: string, password: string}`
  - Returns: `{id, username, role}`

- `POST /login` - User login
  - Body: `{username: string, password: string}`
  - Returns: `{access_token, token_type}`

- `GET /me` - Get current user profile
  - Headers: `Authorization: Bearer {token}`
  - Returns: `{id, username, role}`

### Product Routes

- `GET /products` - Get all products
  - Returns: `[{product_id, name, description, price, stock, images}]`

- `POST /admin/create-product` - Create product (Admin only)
  - Headers: `Authorization: Bearer {token}`
  - Body: `{name, description, price, stock, images}`
  - Returns: `{product_id, name, description, ...}`

- `PUT /admin/update/{id}` - Update product (Admin only)
  - Headers: `Authorization: Bearer {token}`
  - Body: `{name?, description?, price?, stock?, images?}`
  - Returns: `{product_id, name, description, ...}`

- `DELETE /admin/delete/{id}` - Delete product (Admin only)
  - Headers: `Authorization: Bearer {token}`
  - Returns: `{message: "Product deleted successfully"}`

### Cart Routes

- `POST /cart/create` - Add item to cart
  - Headers: `Authorization: Bearer {token}`
  - Body: `{product_id, quantity}`
  - Returns: `{user_id, product_id, quantity, ...}`

- `GET /cart` - Get cart items
  - Headers: `Authorization: Bearer {token}`
  - Returns: `[{product_id, quantity, created_at, updated_at}]`

- `PATCH /cart/{id}` - Update cart item
  - Headers: `Authorization: Bearer {token}`
  - Body: `{quantity}`
  - Returns: `{user_id, product_id, quantity, ...}`

- `DELETE /cart/{id}` - Remove item from cart
  - Headers: `Authorization: Bearer {token}`
  - Returns: `{message: "Item removed from cart"}`

## Database Schema

### Users Table
```
users
├── id (Integer, Primary Key)
├── username (String, Unique, Index)
├── hashed_password (String)
└── role (String, Default: 'user')
```

### Products Table
```
products
├── product_id (Integer, Primary Key)
├── name (String, Unique, Index)
├── description (String)
├── price (Float)
├── stock (Integer, Default: 0)
├── images (String)
├── created_by (Integer, Foreign Key to users)
├── created_at (DateTime)
└── updated_at (DateTime)
```

### Cart Items Table
```
cart_items
├── id (Integer, Primary Key)
├── user_id (Integer, Foreign Key to users)
├── product_id (Integer, Foreign Key to products)
├── quantity (Integer)
├── created_at (DateTime)
├── updated_at (DateTime)
└── Unique Constraint: (user_id, product_id)
```

## Project Structure

```
ecommerce-backend-fastapi/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database setup and session
│   ├── models/
│   │   ├── users.py           # User model
│   │   ├── products.py        # Product model
│   │   └── cart_items.py      # Cart items model
│   ├── schemas/
│   │   ├── users.py           # User request/response schemas
│   │   ├── product.py         # Product request/response schemas
│   │   └── cart_items.py      # Cart request/response schemas
│   ├── routes/
│   │   ├── login.py           # Login routes
│   │   ├── signup.py          # Signup routes
│   │   ├── me.py              # User profile routes
│   │   ├── products.py        # Product listing routes
│   │   ├── create_product.py  # Create product routes
│   │   ├── update_product.py  # Update product routes
│   │   ├── delete_product.py  # Delete product routes
│   │   ├── admin.py           # Admin routes
│   │   ├── cart.py            # Cart listing routes
│   │   ├── create_cart.py     # Create cart routes
│   │   ├── patch_cart.py      # Update cart routes
│   │   └── delete_cart.py     # Delete cart routes
│   └── services/
│       ├── auth.py            # Authentication and authorization
│       ├── product_service.py # Product business logic
│       └── cart_service.py    # Cart business logic
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main app component
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   └── Admin.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── alembic/                    # Database migrations
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Docker compose for development
├── vercel.json                 # Vercel deployment config
├── .env.example                # Example environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Running the Application

### Using Docker Compose (Recommended for Development)

1. Ensure Docker and Docker Compose are installed

2. Start the application:
```bash
docker-compose up -d
```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

4. Stop the application:
```bash
docker-compose down
```

### Running Locally

#### Backend

1. Ensure virtual environment is activated:
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

2. Start the FastAPI server:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

3. The API will be available at: http://localhost:8000

#### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Start the development server:
```bash
npm run dev
```

3. The frontend will be available at: http://localhost:5173

### Database Migrations

1. Create a new migration:
```bash
alembic revision --autogenerate -m "Migration description"
```

2. Apply migrations:
```bash
alembic upgrade head
```

3. Rollback migrations:
```bash
alembic downgrade -1
```

## Development

### Code Structure Best Practices

1. Models - Define database tables and relationships
2. Schemas - Define request/response validation
3. Routes - Handle HTTP requests and responses
4. Services - Implement business logic
5. Database - Manage connections and sessions

### Adding New Features

1. Create model in `backend/models/`
2. Create schema in `backend/schemas/`
3. Create service in `backend/services/`
4. Create routes in `backend/routes/`
5. Import and include router in `backend/main.py`
6. Create frontend components in `frontend/src/`

### Running Tests

Currently, the project does not have automated tests. For production deployment, add tests using:

- Backend: pytest
- Frontend: Jest and React Testing Library

Example test structure:
```bash
backend/
├── tests/
│   ├── test_auth.py
│   ├── test_products.py
│   └── test_cart.py

frontend/
├── __tests__
│   ├── Auth.test.jsx
│   └── Cart.test.jsx
```

## Deployment

### Backend Deployment

#### Option 1: Vercel (Recommended)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Configure environment variables in Vercel dashboard

#### Option 2: Heroku

1. Create Heroku account and install CLI

2. Deploy:
```bash
heroku create app-name
git push heroku main
```

#### Option 3: Docker

1. Build image:
```bash
docker build -t ecommerce-backend .
```

2. Run container:
```bash
docker run -p 8000:8000 -e DATABASE_URL=your_db_url ecommerce-backend
```

### Frontend Deployment

#### Vercel (Recommended)

1. Push code to GitHub

2. Import project to Vercel

3. Set environment variables:
```
REACT_APP_API_URL=your_backend_url
```

4. Deploy automatically on push

#### Netlify

1. Connect GitHub repository

2. Build command: `npm run build`

3. Publish directory: `dist`

4. Set environment variables

## Troubleshooting

### Backend Issues

1. Database Connection Error
   - Check DATABASE_URL in .env file
   - Ensure database server is running
   - Verify credentials and host

2. JWT Token Errors
   - Verify SECRET_KEY matches between sessions
   - Check token expiration
   - Ensure Authorization header format is correct

3. CORS Errors
   - Check frontend URL in CORS middleware
   - Verify request origin matches allowed origins
   - Check browser console for specific errors

### Frontend Issues

1. API Connection Failed
   - Verify backend server is running
   - Check API_URL configuration
   - Check browser network tab for details

2. Authentication Issues
   - Verify token is stored in context
   - Check token expiration
   - Clear browser cache and local storage

3. Build Errors
   - Delete node_modules and package-lock.json
   - Run `npm install` again
   - Check Node version compatibility

### Database Issues

1. Migration Errors
   - Check alembic history
   - Review migration files for SQL syntax
   - Rollback last migration if needed

2. Connection Pool Issues
   - Reduce database connections in production
   - Implement connection pooling
   - Monitor active connections

## Security Considerations

### Current Implementation

- JWT-based authentication
- Password hashing with bcrypt
- CORS middleware configuration
- Role-based access control

### Production Recommendations

1. Change SECRET_KEY to a strong random value
2. Use HTTPS for all communications
3. Implement rate limiting on API endpoints
4. Add request validation and sanitization
5. Use environment-specific configurations
6. Implement logging and monitoring
7. Add API versioning strategy
8. Use database SSL connections
9. Implement request signing for sensitive operations
10. Add API key authentication for service-to-service calls

## Performance Optimization

1. Database Query Optimization
   - Add indexes on frequently searched columns
   - Use eager loading for related data
   - Implement query result caching

2. API Optimization
   - Implement pagination for list endpoints
   - Add response compression
   - Use CDN for static assets
   - Implement API caching headers

3. Frontend Optimization
   - Code splitting with React.lazy
   - Image optimization and lazy loading
   - Bundle size analysis with Vite
   - Production build optimization

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Enhancements

- Order management system
- Payment gateway integration (Stripe, PayPal)
- Product reviews and ratings
- Search and filtering functionality
- Product recommendations
- Wishlist feature
- Email notifications
- Inventory management
- Analytics dashboard
- Admin user management panel

## License

This project is open source and available under the MIT License. See LICENSE file for details.

## Contact

For questions or support, please contact the project maintainer:
- GitHub: devdesai25
- Email: Please submit an issue on GitHub

## Acknowledgments

- FastAPI documentation and community
- React and Vite communities
- SQLAlchemy ORM team
- All contributors and users

---

Last Updated: June 2, 2026
Version: 1.0.0
