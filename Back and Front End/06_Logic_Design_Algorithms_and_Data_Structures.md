# VI. Logic Design — Algorithms and Data Structures

## 6.1 Overview

This section defines the core logic behind ElectroMart's major modules, expressed as algorithms with supporting data structures, ahead of implementation. Each algorithm is chosen to match the operation it supports (search, filtering, comparison, cart totals, order state) so the system stays responsive as the product catalogue and order volume grow.

## 6.2 Core Data Structures

| Structure | Used For | Why |
|---|---|---|
| **Hash Map / Dictionary** | Product catalogue lookup by ID, user session lookup, shopping cart (product_id → quantity) | O(1) average lookup, insert and update — ideal for frequent add/remove/update operations in the cart and catalogue. |
| **Array / List** | Search result sets, order history, product image lists | Ordered, iterable collections that support pagination and sorting. |
| **Tree (Category Tree)** | Product category/subcategory hierarchy (e.g., Electronics → Phones → Smartphones) | Natural hierarchical representation; supports efficient category-scoped search by traversing only relevant subtrees. |
| **Priority Queue / Heap** | Ranking search results by relevance or price, ranking sellers by rating for a listing | Efficiently retrieves top-N items (e.g., "cheapest 10," "top-rated sellers") without fully sorting large datasets. |
| **Queue (FIFO)** | Order-processing pipeline, notification/chat message delivery | Preserves first-in-first-out order, matching real-world order fulfilment and message sequencing. |
| **Graph (optional, for recommendations)** | "Buyers who viewed this also viewed…" relationships between products | Captures many-to-many relationships between products/users for recommendation traversal. |

## 6.3 Key Algorithms

### 6.3.1 Product Search & Filtering

**Purpose:** return matching products for a keyword plus optional filters (category, price range, brand, rating).

```
ALGORITHM SearchProducts(keyword, filters, sortOption)
INPUT: keyword (string), filters (category, minPrice, maxPrice, brand, minRating), sortOption
OUTPUT: ranked list of matching products

1. results ← empty list
2. FOR each product IN productIndex (hash map keyed by normalized keywords):
       IF keyword is empty OR product.searchTokens CONTAINS keyword:
           IF product.category matches filters.category (or filters.category is null) AND
              product.price BETWEEN filters.minPrice AND filters.maxPrice AND
              (filters.brand is null OR product.brand = filters.brand) AND
              product.rating >= filters.minRating:
               ADD product TO results
3. SORT results BY sortOption (price ascending/descending, rating descending, relevance score)
4. RETURN paginate(results, pageNumber, pageSize)
END ALGORITHM
```

*Complexity:* O(n) filter pass over the indexed candidate set plus O(n log n) sort; an inverted index (keyword → product IDs) keeps the candidate set small rather than scanning the entire catalogue.

### 6.3.2 Price Comparison

**Purpose:** compare a listed product's price against reference platforms (Konga, Jumia, AliExpress, Slot, Jiji).

```
ALGORITHM ComparePrice(product)
INPUT: product (with matched external listings, fetched/cached per platform)
OUTPUT: comparison summary (platform, price, delta, cheapest flag)

1. comparisons ← empty list
2. FOR each platform IN [Konga, Jumia, AliExpress, Slot, Jiji]:
       externalPrice ← lookupCachedPrice(platform, product.matchKey)
       IF externalPrice is available:
           delta ← product.price - externalPrice
           ADD {platform, externalPrice, delta} TO comparisons
3. cheapest ← MIN(comparisons ∪ {ElectroMart price}, by price)
4. RETURN {comparisons, cheapest}
END ALGORITHM
```

*Note:* external prices are periodically fetched and cached (not queried live on every page view) to keep product-detail response times fast and to avoid rate-limiting from external sources.

### 6.3.3 Shopping Cart Management

**Purpose:** add/update/remove items and compute totals.

```
ALGORITHM UpdateCart(cart, productId, quantityChange)
INPUT: cart (hash map: productId → {quantity, unitPrice}), productId, quantityChange
OUTPUT: updated cart and total

1. IF productId EXISTS IN cart:
       cart[productId].quantity ← cart[productId].quantity + quantityChange
       IF cart[productId].quantity <= 0:
           REMOVE productId FROM cart
   ELSE IF quantityChange > 0:
       cart[productId] ← {quantity: quantityChange, unitPrice: lookupPrice(productId)}
2. total ← 0
3. FOR each (productId, item) IN cart:
       total ← total + item.quantity * item.unitPrice
4. RETURN {cart, total}
END ALGORITHM
```

*Complexity:* O(1) for add/update/remove (hash map), O(k) to recompute the total where k = number of distinct items in the cart.

### 6.3.4 Checkout & Order Creation

```
ALGORITHM PlaceOrder(cart, buyer, paymentDetails)
INPUT: cart, buyer, paymentDetails
OUTPUT: order confirmation or error

1. FOR each (productId, item) IN cart:
       IF stock(productId) < item.quantity:
           RETURN error "Insufficient stock for productId"
2. paymentResult ← callPaymentGateway(paymentDetails, total(cart))
3. IF paymentResult.status ≠ "success":
       RETURN error paymentResult.message
4. FOR each (productId, item) IN cart:
       decrementStock(productId, item.quantity)
5. order ← createOrder(buyer, cart, paymentResult.transactionId, status = "processing")
6. ENQUEUE order INTO fulfilmentQueue
7. CLEAR cart
8. RETURN order confirmation
END ALGORITHM
```

*Data structure note:* the fulfilment queue is a FIFO queue so orders are processed by sellers/admin in the sequence they were placed; stock decrement and payment capture are treated as a single logical transaction to avoid overselling.

### 6.3.5 Order Status Tracking

**Purpose:** move an order through a fixed sequence of states and expose that sequence to the buyer as a timeline.

```
ALGORITHM AdvanceOrderStatus(order, nextStatus)
INPUT: order, nextStatus (one of: placed, processing, shipped, delivered, returned, cancelled)
OUTPUT: updated order with status history

1. IF NOT isValidTransition(order.status, nextStatus):
       RETURN error "Invalid status transition"
2. order.status ← nextStatus
3. APPEND {status: nextStatus, timestamp: now()} TO order.statusHistory   // array acting as an append-only log
4. notifyBuyer(order, nextStatus)
5. RETURN order
END ALGORITHM
```

*Data structure note:* `statusHistory` is a simple append-only list, giving an O(1) write and a natural chronological timeline for the tracking UI.

### 6.3.6 Seller/Product Rating Aggregation

```
ALGORITHM UpdateRating(entity, newRatingValue)
INPUT: entity (product or seller) with {ratingSum, ratingCount}
OUTPUT: updated average rating

1. entity.ratingSum ← entity.ratingSum + newRatingValue
2. entity.ratingCount ← entity.ratingCount + 1
3. entity.averageRating ← entity.ratingSum / entity.ratingCount
4. RETURN entity.averageRating
END ALGORITHM
```

*Complexity:* O(1) incremental update — avoids recomputing the average over all historical ratings on every new review.

## 6.4 Flowchart Reference (Standard Symbols)

Each algorithm above should be represented as a flowchart using standard symbols before implementation:

- **Start/End** — oval, marks entry and exit of the process (e.g., "Start Checkout" / "Order Confirmed").
- **Process** — rectangle, a computation or action (e.g., "Compute cart total").
- **Input/Output** — parallelogram, data entering or leaving the process (e.g., "Read payment details").
- **Decision** — diamond, a branching condition (e.g., "Stock available?", "Payment successful?").
- **Connector** — circle, links flowchart segments across a page or between diagrams (e.g., linking the checkout flowchart to the order-tracking flowchart).

## 6.5 Pseudocode-to-Implementation Mapping

| Pseudocode Algorithm | Suggested Implementation Layer |
|---|---|
| SearchProducts | Backend search service, backed by an indexed database query or search engine (e.g., an inverted index/full-text index) |
| ComparePrice | Scheduled background job (cache refresh) + fast read from cache at request time |
| UpdateCart | Session-scoped or database-backed cart service, keyed by user/session ID |
| PlaceOrder | Transactional backend operation wrapping stock check, payment call, and order creation |
| AdvanceOrderStatus | Backend order service, restricted to seller/admin roles, triggering buyer notifications |
| UpdateRating | Triggered on review submission, updating denormalized rating fields for fast reads |
