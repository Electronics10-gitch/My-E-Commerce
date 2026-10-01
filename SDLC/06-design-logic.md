# Design — Logic

This is the "brain" of the client: pure functions that turn state and
input into decisions, independent of both the rendering layer
(`05-design-frontend.md`) and the simulated data layer
(`07-design-backend.md`).

## Product lookup — from O(n·m) to O(n+m)
`findProduct()` is an O(n) scan (catalogue + listings) per call. Placing
an order with *m* cart lines used to call it once per line — O(n·m)
total, effectively O(n²) as the catalogue grows with the cart.
`buildProductIndex()` instead does a single O(n) pass to build a
`productId → { product, isListing }` `Map`, so each of the *m* lookups
during order placement becomes O(1) — total cost O(n + m).

## Price comparison
- `comparePriceFor(price)` — a fixed +16% markup on ElectroMart's own
  price, used for the simple "typical marketplace price" badge.
- `competitorPricesFor(product)` — a richer, deterministic per-listing
  comparison across five named marketplaces (Konga, Jumia, AliExpress,
  Slot, Jiji). Each competitor's markup is derived from `seededUnit()`,
  a small string hash (`seed → 0.000–0.999`) keyed on
  `productId + '|' + marketplaceName`, so the same product always shows
  the same competitor prices across reloads without storing them.
  Markups are constrained to +9%–+34%, so ElectroMart is always shown as
  the cheapest option — clearly documented as **illustrative, not live,
  data** (see the footer disclaimer), not a claim of real-time scraping.

## Order progress
`computeOrderProgress(order)` derives the current tracking step from
elapsed real time (`Date.now() - order.createdAt`) against a fixed
`TRACKING_STEP_HOURS` table, walking it backwards to find the latest
step reached — so a tracked order advances realistically over time
rather than jumping straight to "Delivered." `deliveredAt` is set the
*first* time the delivered step is reached and never overwritten, so
the 7-day return window (enforced against `deliveredAt`) can't be
reset by revisiting the tracking page later.

## Seller analytics
`computeSellerAnalytics(db, seller)` aggregates a seller's orders in a
single O(orders) pass — each order's line items are scanned once, no
nested re-scans — accumulating revenue, units sold, a distinct-orders
count, and a per-listing breakdown (via a `name → {units, revenue}`
`Map`) together as it goes, then sorts and slices the top 6 listings by
revenue for the dashboard.

## Auth/validation logic
- `isValidEmail()` / `passwordStrength()` (length + character-class
  count → weak/medium/strong) / `validateCredentials()`.
- Registration enforces password strength; **login deliberately does
  not** — rejecting a login because an *existing* password no longer
  meets today's strength bar is poor, non-standard UX, so strength is
  only gated at the point a password is chosen.
- `makeToken()` / `userIdFromToken()` implement a minimal
  `local.<userId>.<random>` bearer-token scheme, checked in
  `requireAdmin()` and throughout `api()`.

## Misc
- `debounce()` — generic trailing-edge debounce, used for search input.
- `fmt()` — Naira currency formatting (`₦` + `toLocaleString('en-NG')`).
