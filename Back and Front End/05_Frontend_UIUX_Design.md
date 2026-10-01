# V. Frontend Design — UI/UX

## 5.1 Design Approach

ElectroMart's frontend is built with Python's Flet framework (Flutter-based rendering), which allows one UI codebase to be compiled to Web, Desktop and Mobile. The UI/UX design therefore follows a **responsive, component-based** approach: shared widgets (product card, cart item, nav bar) are built once and adapt their layout to screen size (mobile single-column vs. desktop/tablet grid) rather than maintaining separate designs per platform.

Design principles applied:

- **Consistency** — the same navigation structure, color scheme and component styling appear on every screen and platform.
- **Clarity** — product information (image, name, price, seller, rating) is scannable at a glance, especially in list/grid views.
- **Minimal friction** — cart, checkout and search are always reachable within one or two taps/clicks from any screen.
- **Trust signals** — seller ratings, price-comparison badges, and secure-checkout indicators are visible where buying decisions happen.
- **Accessibility** — sufficient color contrast, scalable text, and screen-reader-friendly labels (WCAG-aligned), consistent with the compliance requirements in the SRS.

## 5.2 Information Architecture / Navigation

```
Home
 ├── Search / Category Browse
 │     └── Product Listing Page
 │           └── Product Detail Page
 │                 ├── Add to Cart
 │                 └── Price Comparison Panel
 ├── Cart
 │     └── Checkout
 │           └── Order Confirmation
 ├── Orders
 │     └── Order Detail / Tracking / Feedback
 ├── Chat / Support
 ├── Seller Dashboard (seller role)
 │     ├── My Listings (Create / Edit / Delete)
 │     └── Seller Orders
 ├── Admin Dashboard (admin role)
 │     ├── User & Listing Moderation
 │     └── Reports
 └── Account
       ├── Profile / Settings
       └── Login / Register / Password Reset
```

## 5.3 Key Screens

| Screen | Purpose | Key UI Elements |
|---|---|---|
| **Login / Register** | Authenticate or onboard a user | Email/password fields, role selection (buyer/seller), validation messages, password-reset link |
| **Home** | Entry point, discovery | Search bar, category chips, featured/trending products, banner for promotions |
| **Product Listing (Search Results)** | Browse/filter products | Grid/list of product cards, filter panel (category, price range, brand, rating), sort control |
| **Product Detail** | Decision-making | Image gallery, title, price, seller info & rating, description, quantity selector, "Add to Cart", price-comparison panel (Konga/Jumia/AliExpress/Slot/Jiji), reviews |
| **Cart** | Review before purchase | Line items with quantity steppers, subtotal, remove/save-for-later, "Proceed to Checkout" |
| **Checkout** | Complete purchase | Shipping details form, payment method selection, order summary, secure-payment badge, confirm button |
| **Order Tracking** | Post-purchase visibility | Status timeline (placed → processing → shipped → delivered), delivery ETA, feedback/rating prompt |
| **Chat Widget** | Buyer–seller/support communication | Message thread, quick-reply suggestions, unread badge |
| **Seller Dashboard** | Manage listings and orders | Listing table (create/edit/delete), stock indicators, incoming-order queue |
| **Admin Dashboard** | Platform oversight | User/listing moderation queue, flagged-content list, sales/activity report widgets |

## 5.4 Visual & Interaction Design

- **Color scheme**: a neutral base (white/light gray) with one accent color for primary actions (Add to Cart, Checkout, Confirm) and a secondary color reserved for warnings/errors (e.g., out-of-stock, payment failure).
- **Typography**: a single readable sans-serif family with a clear size hierarchy (page titles > section headers > body text > captions/metadata).
- **Cards & grids**: products are shown as cards (image, name, price, rating) in a responsive grid that collapses to a single column on mobile.
- **Feedback states**: every action (add to cart, place order, submit review) shows immediate visual feedback (snackbar/toast, loading spinner, success/error state) so the user is never left uncertain whether an action succeeded.
- **Forms**: inline validation (e.g., invalid email, weak password, empty required field) with messages shown next to the relevant field rather than only on submit.
- **Empty/error states**: designed explicitly for "no search results," "empty cart," and "connection error" so the interface never appears broken.

## 5.5 Cross-Platform Adaptation

| Platform | Adaptation |
|---|---|
| **Web (SPA/PWA/MPA)** | Full navigation bar, multi-column product grid, hover states on cards/buttons |
| **Desktop (Windows/Linux/macOS)** | Same layout as web with native window chrome; keyboard shortcuts for search and cart |
| **Mobile (Android/iOS)** | Bottom navigation bar, single-column product list, larger touch targets, swipe gestures on cart items |

## 5.6 Usability Validation

Wireframes/prototypes should be walked through with a small sample of prospective buyers and sellers (tying back to the interviews/questionnaires used in requirement elicitation) to confirm that: the search-to-checkout path is completable without guidance, the price-comparison panel is noticed and understood, and seller listing creation is achievable without a manual.
