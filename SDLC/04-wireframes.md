# UI Wireframes & Proof of Concept

The Proof of Concept for this course deliverable **is** ElectroMart.html
itself — a working, click-through prototype rather than a slide deck.
The sketches below are the low-fidelity layout each screen was built
from, kept here as the wireframe artifact the Analysis phase asks for,
each mapped to the render function that implements it.

## Auth screen — `renderAuth()`
```
+-----------------------------------------+
|   [Tower mark]  ElectroMart              |
|-------------------------------------------
|   [ Sign in ]      [ Register ]  <tabs>  |
|                                           |
|   Email    [_______________________]     |
|   Password [_______________________]     |
|                                           |
|            [   Continue   ]              |
+-----------------------------------------+
```

## Shop (catalogue) — `renderShop()` / `renderGrid()`
```
+-----------------------------------------------------------+
| Search [___________]   Category v          [Cart (n)]     |
|-------------------------------------------------------------
| [img] Product name        [img] Product name       ...    |
|  ₦price  compare: ₦x       ₦price  compare: ₦x             |
|  [SON badge] [View]        [SON badge] [View]              |
+-----------------------------------------------------------+
```

## Product modal — `renderProductModal()`
```
+---------------------------------------+
| Product name                      [x] |
|----------------------------------------
|  [image]     Specs: ...               |
|  ₦price      Our price vs marketplace |
|              comparison table          |
|              [ Add to cart ]           |
+---------------------------------------+
```

## Cart drawer — `renderCartDrawer()`
```
+----------------------------+
| Your cart              [x]|
|----------------------------|
| item  qty [-1][ ][+1]  ₦.. |
| item  qty [-1][ ][+1]  ₦.. |
|----------------------------|
| Subtotal            ₦....  |
|      [ Checkout ]          |
+----------------------------+
```

## Checkout modal — `renderCheckoutModal()`
```
+----------------------------------------+
| Checkout                            [x]|
|------------------------------------------
| Address [____________]  Phone [______] |
| Payment: (o) Card  ( ) Transfer ( ) POD|
|   Card fields shown only if Card chosen|
|              [ Place order ]           |
+----------------------------------------+
```

## Order tracking — `renderTrack()` / `renderOrders()`
```
+-------------------------------------------+
| Track by ID [_____________] [ Track ]     |
|---------------------------------------------
| o--o--o--o--o   (progress advances over   |
| Placed .. Delivered   real elapsed time)  |
|  -> post-delivery feedback / return form  |
+-------------------------------------------+
```

## Seller — listing + analytics — `renderSell()` / `renderAnalytics()`
```
+----------------------------------------------+
| New listing: name/category/price/stock/desc  |
|                [ Publish ]                    |
|------------------------------------------------
| Analytics: revenue | units sold | orders      |
| Top listings (bar-style ranked list)          |
| Low stock / out of stock counts               |
+----------------------------------------------+
```

## Admin — `renderAdmin()`
```
+-------------------------------------------+
| Tabs: [Reports] [Listings] [Users]        |
|---------------------------------------------
| Row: listing/user   [Remove/Restore] etc. |
+-------------------------------------------+
```

## Quick-response chat widget — `renderChatWidget()`
```
                                   +----------------+
                                   | Support (bot)  |
                                   |----------------|
                                   | bot: Hi! ...   |
                                   | [quick replies]|
                                   | [type a msg__] |
                                   +----------------+
                              [chat launcher bubble]
```

These carried straight into the build with only spacing/visual-identity
decisions added at the Design stage (`05-design-frontend.md`) — no
structural surprises between wireframe and shipped screen.
