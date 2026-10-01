# Testing Plan — Alpha / Beta / UAT

This is a plan and checklist, not a fabricated results log — check each
box as it is actually run, in the environment named, and record the
date/tester/outcome in the "Result" column.

## Alpha — inside the development environment
Run in the same browser/machine the app is developed in, immediately
after each feature change.

| Area | Check | Result |
|---|---|---|
| Auth | Register (buyer), register (seller), login, logout, session survives reload | |
| Catalogue | Browse, filter by category, search (debounced), price comparison badge shows 5 marketplaces, cheapest is always ElectroMart | |
| Cart | Add, change quantity (respects stock), remove, subtotal correct | |
| Checkout | Address/phone required, all 3 payment methods (card validation, transfer RRR, POD), stock decrements on order | |
| Tracking | Tracking ID returned on order, progress advances over elapsed time (not instantly) | |
| Feedback/Returns | Feedback prompt appears once delivered; return form only accepted inside 7-day window | |
| Seller | Publish a listing, listing appears in shared catalogue tagged with seller name, analytics reflect a real sale | |
| Admin | Login as seeded admin, remove/restore a listing, disable/enable a user | |
| Accessibility | Skip link, keyboard-only navigation through a full purchase, modals trap focus and close on Escape | |
| Policies | Terms/Privacy/Returns/Requirements/Standards all open from the footer and render fully | |

## Beta — outside the development environment
Run after deploying (see `10-deployment-plan.md`) to a real static host,
on at least one device/browser combination the developer doesn't
normally use.

| Area | Check | Result |
|---|---|---|
| Cross-browser | Full purchase flow on a second browser engine (e.g. Safari if built on Chrome) | |
| Cross-device | Full purchase flow on a real mobile device, not just a resized desktop window | |
| Fresh state | First load with no existing `localStorage` seeds correctly (admin account present, empty cart) | |
| Persistence | Data survives a real page reload and a browser restart | |
| Network | Page loads and fonts render on a throttled/mobile connection | |

## UAT — user acceptance
Have someone who is *not* the developer walk through the app against
the functional requirements listed in the app's own **Requirements**
page, without being told how to use it first.

| Acceptance criterion | Pass/Fail | Notes |
|---|---|---|
| Can register and understand which role (buyer/seller) they picked | | |
| Can find a product and understand the price-comparison badge's meaning | | |
| Can complete a purchase without confusion over payment options | | |
| Can find and understand the tracking status of an order | | |
| Can locate Terms, Privacy, Returns, Requirements and Standards without help | | |
| (Seller) Can list a product and find their sales analytics | | |
| Overall: would use again / recommend | | |

## Sign-off
Testing is considered complete for the course deliverable once every
Alpha row passes, at least one full Beta pass is recorded, and UAT
feedback has been reviewed (not necessarily 100% pass — genuine UAT
feedback, including friction points, is more valuable than a clean
sheet).
