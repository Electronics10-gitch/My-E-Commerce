# VII. Backend Design — API and Data Access

## 7.1 Architecture Overview

ElectroMart's backend follows a **layered architecture**:

```
Client (Web / Desktop / Mobile — Flet frontend)
        │  HTTPS/JSON
        ▼
   API Layer (REST endpoints, auth, validation)
        │
        ▼
  Service / Logic Layer (business rules, algorithms from Section VI)
        │
        ▼
  Data Access Layer (repositories / ORM)
        │
        ▼
     Database (relational or NoSQL) + Cache
```

This separation allows the frontend (any of the three platforms) to talk to one consistent API, keeps business logic out of the UI layer, and lets the data access layer be swapped or optimised (e.g., adding caching) without changing API contracts.

## 7.2 API Design Principles

- **RESTful resources**: users, products, categories, cart, orders, reviews and chat messages are modelled as resources with standard HTTP verbs (GET, POST, PUT/PATCH, DELETE).
- **Stateless authentication**: each request carries a token (e.g., JWT) identifying the user and role; the server does not rely on server-side session state for API calls.
- **Role-based authorization**: endpoints are guarded by role (buyer, seller, admin) in addition to authentication, matching the security non-functional requirements.
- **Consistent response shape**: every response returns a predictable envelope (status, data, error) so the frontend can handle success/error uniformly across platforms.
- **Versioning**: endpoints are prefixed (e.g., `/api/v1/...`) so future changes do not break existing clients.
- **Pagination & filtering**: list endpoints (products, orders) accept `page`, `pageSize` and filter query parameters rather than returning entire tables.

## 7.3 Core API Endpoints

### Authentication & Users

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register a new buyer or seller account |
| POST | `/api/v1/auth/login` | Authenticate and issue an access token |
| POST | `/api/v1/auth/password-reset` | Request/complete a password reset |
| GET | `/api/v1/users/me` | Get the authenticated user's profile |
| PUT | `/api/v1/users/me` | Update profile details |

### Products & Catalogue

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/products` | Search/list products (query params: keyword, category, minPrice, maxPrice, brand, minRating, sort, page) |
| GET | `/api/v1/products/{id}` | Get a single product's detail, including price-comparison data |
| POST | `/api/v1/products` | Create a new listing (seller role) |
| PUT | `/api/v1/products/{id}` | Update a listing (seller role, own listings only) |
| DELETE | `/api/v1/products/{id}` | Remove a listing (seller/admin role) |
| GET | `/api/v1/categories` | Get the category tree |

### Cart & Checkout

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/cart` | Get the current user's cart |
| POST | `/api/v1/cart/items` | Add an item to the cart |
| PATCH | `/api/v1/cart/items/{productId}` | Update quantity of a cart item |
| DELETE | `/api/v1/cart/items/{productId}` | Remove an item from the cart |
| POST | `/api/v1/checkout` | Submit payment details and place an order |

### Orders

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/orders` | List the authenticated user's orders (buyer) or received orders (seller) |
| GET | `/api/v1/orders/{id}` | Get order detail and status history |
| PATCH | `/api/v1/orders/{id}/status` | Update order status (seller/admin role) |
| POST | `/api/v1/orders/{id}/feedback` | Submit post-delivery rating/review |
| POST | `/api/v1/orders/{id}/return` | Initiate a return request |

### Chat & Notifications

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/chats/{threadId}/messages` | Get messages in a chat thread |
| POST | `/api/v1/chats/{threadId}/messages` | Send a message |
| GET | `/api/v1/notifications` | Get notifications for the authenticated user |

### Admin

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/admin/reports/sales` | Aggregate sales/activity report |
| GET | `/api/v1/admin/moderation/listings` | List flagged listings pending review |
| PATCH | `/api/v1/admin/moderation/listings/{id}` | Approve/reject a flagged listing |

## 7.4 Data Access Layer

- **Repository pattern**: each resource (User, Product, Order, Review, ChatMessage) has a repository responsible for all reads/writes to that resource, so the service layer never issues raw queries directly.
- **ORM / query layer**: an ORM (or equivalent query builder) maps repository calls to the underlying database, keeping SQL/query strings out of the business logic and reducing injection risk when combined with parameterised queries.
- **Caching layer**: frequently read, slow-changing data (category tree, cached external price-comparison values, product listings) is cached (e.g., in-memory or a dedicated cache store) with a defined expiry, refreshed by the background job described in Section VI.
- **Transactions**: multi-step writes that must succeed or fail together (e.g., stock decrement + order creation + payment capture in `PlaceOrder`) are wrapped in a database transaction to preserve consistency.
- **Connection pooling**: the data access layer maintains a pool of database connections rather than opening a new connection per request, supporting the performance non-functional requirements under concurrent load.

## 7.5 Core Data Model (Entities)

| Entity | Key Fields | Relationships |
|---|---|---|
| **User** | id, name, email, passwordHash, role (buyer/seller/admin) | 1—many Products (as seller), 1—many Orders (as buyer) |
| **Product** | id, sellerId, name, description, category, price, stock, images, averageRating | many—1 User (seller), many—1 Category |
| **Category** | id, name, parentCategoryId | self-referencing tree structure |
| **CartItem** | userId, productId, quantity | many—1 User, many—1 Product |
| **Order** | id, buyerId, items, total, status, statusHistory, paymentTransactionId | many—1 User (buyer), 1—many OrderItems |
| **OrderItem** | orderId, productId, quantity, unitPriceAtPurchase | many—1 Order, many—1 Product |
| **Review** | id, productId, buyerId, rating, comment, createdAt | many—1 Product, many—1 User |
| **ChatMessage** | id, threadId, senderId, content, timestamp | many—1 User (sender), many—1 ChatThread |

## 7.6 Security in the API/Data Layer

- All endpoints (except registration/login) require a valid token; role checks are enforced server-side, not assumed from the client.
- Input is validated and sanitised at the API boundary before reaching the service/data layer, preventing injection and malformed-data issues.
- Passwords are never returned in API responses; only hashed values are stored, never raw passwords.
- Payment details are passed through to the payment gateway and are not persisted in ElectroMart's own database (PCI-DSS alignment).
- Sensitive actions (status changes, moderation, admin report access) are logged for audit purposes at the service layer.

## 7.7 Deployment Considerations

- The API layer is stateless, allowing multiple instances to run behind a load balancer to meet the performance/scalability non-functional requirements.
- The database and cache are provisioned separately from the API instances so they can be scaled or backed up independently.
- Environment-specific configuration (database credentials, payment-gateway keys) is externalised (environment variables/secrets manager), never hard-coded, to support secure deployment across environments.
