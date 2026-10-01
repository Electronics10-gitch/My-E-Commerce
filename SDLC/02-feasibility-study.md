# Feasibility Study

Applying SMART to the problem in `01-problem-statement.md`, scoped to
what is achievable as a single course deliverable.

## Specific
Build one e-commerce web app, ElectroMart, that lets buyers browse a
shared catalogue with per-product price comparison, buy from either the
platform or independent sellers, track and return orders, and lets
sellers list products and see sales analytics — all documented against
recognised standards (ISO 9001, ISO/IEC 27001, ISO/IEC 25010, ISO/IEC
40500/WCAG 2.1, SON/SONCAP) and Nigerian/EU data-protection law (NDPA
2023, GDPR).

## Measurable
- Every functional requirement in the app's **Requirements** page has a
  corresponding, working feature (auth, browsing, price comparison,
  cart, checkout, order tracking, feedback, returns, seller listings,
  seller analytics, admin moderation).
- Every non-functional requirement (performance, usability, reliability,
  security, persistence, maintainability, compatibility, compliance) is
  either testable in the browser or verifiable by reading the code.
- Test coverage is tracked against a fixed checklist in
  `09-testing-plan.md`, not by feel.

## Achievable
Technically achievable within the course's constraints because:
- The whole app is a single static HTML/CSS/JS file — no server, build
  step, or paid infrastructure required to run or grade it.
- A simulated backend (`api()` over an in-memory/`localStorage`-backed
  `DB`) stands in for a real API and database, so the full
  request/response/validation flow can be demonstrated without standing
  up real infrastructure.
- The scope (one buyer/seller marketplace, one currency, one region's
  compliance framing) is bounded rather than open-ended.

## Relevant
Directly answers the course's applied deliverable: an e-commerce app
built by following Theories → Principles → Standards through the SDLC,
using an AI coding agent as the primary "worker" in an AI-native
development workflow.

## Time-bound
Fits a single-term course project timeline because each SDLC phase
produces one bounded artifact (a problem statement, a design doc set, a
test plan, a deployment plan) rather than an open-ended body of work,
and the app was built incrementally, one feature at a time, which keeps
each increment small enough to finish and verify before starting the
next.

## Conclusion
The project is feasible within the course timeline and technology
constraints. The main risk is scope creep across "just one more
feature" — mitigated by keeping the running feature list in
`03-system-requirements.md` and the app's own Requirements page as the
single source of truth for what is in scope.
