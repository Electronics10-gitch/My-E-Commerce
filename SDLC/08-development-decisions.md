# Development — Tooling & Environment Decisions

## Language & framework: vanilla HTML/CSS/JS, no framework
**Decision**: no React/Vue/etc., no build step, one `.html` file.
**Why**: the deliverable needs to run by opening a file or hosting it
statically — zero install, zero build, zero framework version drift for
a grader to hit. A framework buys structure at the cost of a build
pipeline and dependencies, which trades against the course's "ship a
working PoC fast" goal. Complexity is managed instead via consistently
named functions per functional area (see `06-design-logic.md`,
`07-design-backend.md`), which is what a framework's file structure
would otherwise give for free.

## Development environment
IDE/editor + browser devtools for manual testing, with an AI coding
agent (Claude) as the primary "worker," matching the course's three-
layer model (agent / skills / underlying LLM) and its "AI-native
software development" framing — using AI tools to drive the engineering
process rather than only to autocomplete inside it.

## Working style: one feature at a time
Each feature (buyer/seller marketplace split, price comparison, the
quick-response chat widget, NDPA/GDPR policy pages, ISO/SON standards
page, order tracking with feedback and returns, the 3D card-tilt
effect) was specified and built as its own surgical change — one
instruction, one feature, nothing else touched — rather than large
rewrites. This kept each increment small enough to verify in the
browser before the next one started, which is also why the codebase
reads as a set of clearly bounded, independently named functions rather
than a few large ones.

## Debugging
Manual, browser-devtools-based: exercising each flow (register → list a
product → buy it → track it → return it) end-to-end in the browser
after each change, plus `validateResource()`'s `console.warn`-level
schema checks to surface data-shape drift early without breaking the
running demo.

## Build / dependency management
None required — no `package.json`, no bundler, no transpilation. The
only external dependency is the Google Fonts stylesheet link. This is a
deliberate simplification appropriate to the course's scope, documented
here so it reads as a decision rather than a gap (a production system
would introduce real dependency management once it needs a real
backend — see `07-design-backend.md`'s migration note).
