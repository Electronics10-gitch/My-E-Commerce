# System Requirements

Functional and non-functional requirements are documented inside the app
itself (footer → **Requirements**) and are not repeated here. This file
covers the third leg of requirements elicitation: what the *system*
needs to run, independent of what it does.

## Client environment
- A modern evergreen browser with JavaScript enabled (Chrome, Edge,
  Firefox, Safari — current or one major version back). No plugins,
  extensions, or app installation required.
- `localStorage` available and not blocked (used for the session token,
  cart, and the simulated database `emp_db_v1`); private/incognito
  windows that block storage will lose the cart and session on close.
- Minimum viewport width of ~360px is supported responsively; the layout
  is optimised down to typical mobile widths and up to desktop.
- A network connection is required once, to load the page (fonts are
  fetched from Google Fonts over a `preconnect`); after load, all
  simulated "API" calls run locally and do not require connectivity.

## Hosting / server environment
- No application server, database server, or backend runtime is
  required — the deliverable is a single static `.html` file.
- Any static file host (see `10-deployment-plan.md`) that serves HTML
  over HTTPS is sufficient.
- No environment variables, secrets, or server-side configuration exist
  in this build, since there is no server-side code.

## Data
- All persistent state (accounts, listings, orders, cart, feedback,
  return requests) lives in the browser's `localStorage` under the
  `emp_db_v1` key and per-user cart keys, seeded on first load by
  `ADMIN_SEED()`.
- Data does not sync across browsers or devices — it is local to the
  browser profile that created it. This is an explicit, documented
  simplification for the course deliverable, not an oversight; a
  production version would replace `api()`'s local implementation with
  real HTTP calls to a hosted API and database.

## Third-party dependencies
- Google Fonts (Playfair Display, Jost, JetBrains Mono) — the only
  external network dependency.
- No npm packages, CDNs, or JavaScript frameworks — the app is
  dependency-free vanilla HTML/CSS/JS by design (see
  `08-development-decisions.md`).

## Compatibility constraints
- No Internet Explorer support (uses modern JS: `async/await`, template
  literals, arrow functions, `Map`/`Set`).
- No server-side rendering; the app renders entirely client-side after
  the initial HTML/CSS/JS payload loads.
