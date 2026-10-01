# Design — Backend

ElectroMart is a **monolith by explicit decision** (see
`08-development-decisions.md`): UI, logic, and data access ship as one
file. This document describes the data-access layer as if it were a
separate service, since it is built to that contract even though it
runs in-process.

## Simulated API
`api(path, opts)` is the single entry point for every "network" call in
the app (`GET/POST/PATCH` against paths like `/auth/login`,
`/products`, `/orders`, `/listings`, `/admin/users`). It:
1. Awaits `wait(280–500ms)` — a stand-in for network latency, so
   loading states are real and testable, not instant.
2. Parses the JSON body the same way `fetch()` would.
3. Routes on `path` + `method` to the matching handler.
4. Returns/throws the same shape a real REST/JSON API would
   (`apiError(message, status)` for failures).

Swapping this function's internals for real `fetch()` calls to a hosted
API is the entire migration path to a real backend — nothing above this
layer (logic or frontend) would need to change.

## Data contract — `DATA_EXCHANGE_STANDARD`
A versioned (`version: '1.0'`) JSON Schema (draft-2020-12-style) set
describing every resource `api()` returns: `User`, `Product`, `Order`,
`ApiError` — each with `required` fields and property types/enums
(e.g. `User.role` ∈ `buyer|seller|admin`). `validateResource()` is a
lightweight, non-blocking structural check against these schemas —
used to catch shape drift during development (`console.warn`) without
ever interrupting the demo. It's a consistency contract, not a hard
gate, matching how a real service would validate at its API boundary
without necessarily 500-ing on every edge case during development.

## Storage — `DB_KEY = 'emp_db_v1'`
- `loadDB()` reads `localStorage[DB_KEY]`; on missing/corrupt data it
  seeds a fresh `{ users: [ADMIN_SEED()], orders: [], stock: {},
  listings: [] }` and persists it.
- `ADMIN_SEED()` seeds one admin account (`admin@electromart.demo`) so
  the admin dashboard is reachable without a manual setup step.
- `saveDB(db)` also **upgrades older saved databases in place** —
  backfilling `listings: []` for DBs saved before the marketplace "sell"
  feature existed, and re-inserting the admin user for DBs saved before
  the admin dashboard existed — a small forward-migration pattern so a
  returning user's browser data doesn't break when the app gains
  features.

## Auth
Bearer tokens are `local.<userId>.<random>` strings (`makeToken()` /
`userIdFromToken()`); `requireAdmin()` checks the token's user has
`role === 'admin'` before allowing admin-path calls. Handlers only ever
act on the calling user's own cart, orders, listings, feedback, and
return requests — never another user's, by construction of which `id`
each query filters on.

## Cross-cutting
- `publicUser()` / `publicUserWithStatus()` strip `password` before any
  user object reaches the frontend — the password never leaves the
  "backend" boundary, even though that boundary is in the same file.
- `buildProductIndex()` (see `06-design-logic.md`) is called from the
  order-placement handler so multi-line orders resolve products in
  O(n + m) instead of O(n·m).
