# IV. Requirement Analysis and Elicitation

## 4.1 Elicitation Techniques

Requirements were (or should be) gathered using the fact-gathering techniques specified in the assignment brief, applied to ElectroMart's stakeholders (prospective buyers, sellers, and the platform administrator):

- Interviews with prospective buyers and sellers of electronics to understand buying habits, pain points with existing marketplaces, and desired seller tools.
- Questionnaires distributed to a wider sample of online shoppers to quantify preferences (e.g., preferred payment methods, importance of price comparison, trust concerns).
- Observation of how buyers and sellers currently navigate comparable platforms (Konga, Jumia, AliExpress, Slot, Jiji) to identify usability patterns worth keeping or improving on.
- Document analysis of competitor platforms' policies (returns, seller onboarding, pricing display) and of applicable regulations (NDPA 2023, consumer-protection and e-commerce rules).
- Online research into cross-platform development options (Python/Flet, Flutter) and into standard e-commerce architecture patterns for authentication, cart, checkout and order management.

These techniques feed directly into the Software Requirements Specification (SRS) below, separated into functional and non-functional requirements, followed by the system requirements needed to build and run the application.

## 4.2 Functional Requirements

Functional requirements describe what ElectroMart must do:

| Requirement Area | Description |
|---|---|
| **User Management** | Register, log in and log out securely as a buyer, seller or admin; manage profile details; recover/reset forgotten passwords. |
| **Product Management** | Sellers can create, edit, categorise, price and remove electronics listings, including images, descriptions and stock levels. |
| **Search & Discovery** | Buyers can search and filter products by category, price range, brand and seller rating. |
| **Price Comparison** | Display comparative pricing for a listed item against reference platforms (Konga, Jumia, AliExpress, Slot, Jiji) to inform buyer decisions. |
| **Shopping Cart** | Buyers can add, update quantities in, and remove items from a cart before checkout. |
| **Checkout & Payment** | Buyers can complete purchases through a secure payment flow supporting standard payment methods. |
| **Order Management** | Buyers and sellers can view order status, history and details; sellers can update fulfilment status. |
| **Order Tracking & Feedback** | Buyers can track order/delivery progress and submit post-delivery feedback or ratings; buyers/sellers can initiate returns. |
| **Communication** | A quick-response chat widget lets buyers and sellers (or buyers and support) communicate about listings or orders. |
| **Administration & Reporting** | An admin role can moderate listings/users and generate basic sales/activity reports. |

## 4.3 Non-Functional Requirements

Non-functional requirements define the quality attributes the system must exhibit, grouped here by security, performance and compliance as requested, with the remaining quality attributes (usability, reliability, scalability, maintainability, availability) covered alongside them.

### 4.3.1 Security

- Authenticate users with securely hashed and salted passwords; support session timeout and, optionally, multi-factor authentication for sellers/admins.
- Enforce role-based access control so buyers, sellers and admins can only perform actions permitted to their role.
- Encrypt data in transit (HTTPS/TLS) and sensitive data at rest (e.g., payment tokens, personal details).
- Never store raw card details; integrate with a PCI-DSS-compliant payment gateway instead of handling card data directly.
- Validate and sanitise all user input to prevent SQL injection, cross-site scripting (XSS) and cross-site request forgery (CSRF).
- Maintain audit logs of sensitive actions (logins, listing changes, order status changes, admin actions) for traceability.

### 4.3.2 Performance

- Key pages (product search, listing detail, cart, checkout) should render within a target response time (e.g., 2–3 seconds) under normal load.
- The system should support a defined number of concurrent users during peak periods (e.g., promotions) without significant degradation, using caching and database indexing where needed.
- Search and price-comparison queries should be optimised (indexed database fields, pagination) to remain responsive as the product catalogue grows.
- The architecture should allow horizontal scaling (e.g., additional web/application server instances) as demand increases.

### 4.3.3 Compliance

- Comply with the Nigeria Data Protection Act (NDPA) 2023 for the collection, storage and processing of personal data, including clear consent and a published privacy policy.
- Align with GDPR principles where the platform serves or stores data on users outside Nigeria.
- Follow applicable consumer-protection and e-commerce rules for pricing transparency, returns/refunds and dispute handling.
- Reflect ISO/SON-oriented product-quality expectations for electronics listings (accurate specifications, warranty information) and follow accessibility guidance (e.g., WCAG) so the interface is usable by people with disabilities.

### 4.3.4 Other Quality Attributes

- **Usability:** a consistent, intuitive interface across Web, Desktop and Mobile, given the shared Flet/Flutter-based codebase.
- **Reliability & Availability:** the platform should remain available for buyers and sellers with minimal downtime, with backups for order and product data.
- **Maintainability:** modular code structure so features (e.g., chat, price comparison) can be updated or extended independently.
- **Scalability:** the data model and architecture should accommodate growth in products, sellers and orders without redesign.

## 4.4 System Requirements

System requirements specify the environment needed to develop, run and deploy ElectroMart, split into software and hardware requirements.

**Software / platform requirements**

| Item | Requirement |
|---|---|
| Development language/framework | Python with the Flet UI framework (Flutter-based rendering) for a single, cross-platform codebase. |
| Client platforms | Web (deployable as SPA, PWA or MPA), Desktop (Windows, Linux, macOS), and Mobile (Android and iOS). |
| Backend/data layer | A database engine (relational or NoSQL) for products, users, orders and reviews, accessed via a defined API layer. |
| Payment integration | A third-party, PCI-DSS-compliant payment gateway supporting the target market's common payment methods. |
| Hosting/deployment | A web/application server environment (e.g., cloud VM or PaaS) with HTTPS/TLS enabled, plus app-store/package distribution for Desktop and Mobile builds. |
| Development tools | Version control (Git), an IDE, testing tools, and diagramming tools for the required flowcharts and system design. |

**Hardware requirements**

| Item | Requirement |
|---|---|
| Client hardware (buyers/sellers) | Standard desktop/laptop or smartphone capable of running a modern browser or the ElectroMart mobile app, with an internet connection. |
| Development hardware | A development machine capable of running Python, the Flet/Flutter toolchain, a local database instance and emulators/simulators for mobile testing. |
| Server hardware | Server or cloud instance sized to the expected concurrent user load, with sufficient storage for product images and transactional data, and provision for backups. |
