# III. Feasibility Study

The feasibility study evaluates whether ElectroMart is practical to build and operate, using two complementary lenses: a SMART framing of the project goal, and a SWOT analysis of the project's internal and external position, alongside the five standard feasibility dimensions (technical, economic, operational, legal and schedule).

## 3.1 SMART Goal Analysis

| Criterion | Application to ElectroMart |
|---|---|
| **Specific** | Design and build a Python/Flet marketplace e-commerce application ("ElectroMart") for electronics, providing secure authentication, product/service listing and management, search, shopping cart, checkout and order management for buyers and sellers. |
| **Measurable** | Success is measured against a defined feature set in the SRS (e.g., number of functional requirements implemented and passing test cases), performance targets (page/response times), and deliverables completed: feasibility study, fact-finding report, SRS, algorithms, flowcharts, pseudocode, working application, test evidence and user documentation. |
| **Achievable** | The scope is bounded to a single core domain (electronics) and uses an existing, learnable technology stack (Python/Flet with Flutter-based cross-platform support), making the goal realistic within the developer's current skills and the coursework timeframe. |
| **Relevant** | The project directly satisfies the assignment brief (a marketplace e-commerce application using a structured software engineering approach) and addresses a genuine market need for a focused, transparent electronics marketplace. |
| **Time-bound** | Work is organised into the phases required by the assignment — feasibility and fact-finding, requirements and design (algorithms/flowcharts/pseudocode), implementation, and testing/documentation — each with its own milestone before the final submission deadline. |

## 3.2 Feasibility by Dimension

| Dimension | Assessment |
|---|---|
| **Technical** | Python (with the Flet framework) plus Flutter-based cross-platform tooling can target Web, Desktop (Windows, Linux, macOS) and Mobile (Android, iOS) from a single codebase. The required skills (Python, UI/UX with Flet, relational/NoSQL database design, REST APIs, payment-gateway integration) are attainable within an academic timeframe with existing coursework knowledge. Feasible, with a phased rollout (Web first, then Desktop/Mobile). |
| **Economic** | Development costs are mainly time and learning effort rather than licensing, since Python, Flet and supporting libraries are open-source. Recurring costs (hosting, domain, payment-gateway fees, SSL) are modest for an MVP. Benefits include a reusable portfolio asset and, if extended, a viable niche marketplace. Feasible at MVP scale; a full commercial launch would need a funded plan for marketing and logistics. |
| **Operational** | Target users (buyers and sellers of electronics) are already familiar with e-commerce platforms such as Jumia and Konga, lowering the learning curve. Clear onboarding, a familiar cart/checkout flow and responsive support/chat features support user acceptance. Feasible, provided the interface stays simple and mobile-friendly. |
| **Legal** | The system must comply with the Nigeria Data Protection Act (NDPA) 2023 and, for any international users, GDPR principles, plus consumer-protection rules for online retail and ISO/SON product-quality expectations for electronics. Feasible provided privacy policies, consent flows, secure payment handling and return/refund terms are built in from the design stage rather than added later. |
| **Schedule** | The coursework timeline requires feasibility study, fact-finding, SRS, algorithms, flowcharts, pseudocode, design, implementation, testing and documentation. This is achievable within an academic term if work is phased: analysis and design first, then a core-feature MVP (auth, listings, cart, checkout), followed by secondary features (chat, tracking, comparison) and finally testing/documentation. Feasible with disciplined, incremental delivery. |

## 3.3 SWOT Analysis

| STRENGTHS | WEAKNESSES |
|---|---|
| • Single Python/Flet codebase deployable across Web, Desktop and Mobile, reducing development duplication<br>• Focused, electronics-only niche (ElectroMart – "All Kind of Electronics") allows deeper category specialisation than general marketplaces<br>• Built-in price comparison against established platforms (Konga, Jumia, AliExpress, Slot, Jiji) gives buyers immediate value<br>• Structured SE approach (SRS, algorithms, flowcharts, pseudocode) reduces rework and design errors | • Solo/small-team academic project with limited time and manpower<br>• Flet/Flutter cross-platform tooling is less mature than native frameworks, so some platform-specific polish may be limited<br>• No existing brand recognition or seller base compared to incumbents<br>• Payment gateway and logistics integrations depend on third-party providers outside the developer's control |
| **OPPORTUNITIES** | **THREATS** |
| • Growing smartphone and internet penetration in Nigeria increases the addressable market for online electronics retail<br>• Gap for a trusted, electronics-specialised marketplace with transparent price comparison<br>• Potential to add value-added services later (warranty tracking, verified-seller badges, financing)<br>• Academic project can evolve into a real MVP or portfolio product | • Intense competition from well-funded incumbents (Jumia, Konga, AliExpress)<br>• Evolving data-protection and e-commerce regulation (NDPA 2023) raising compliance overhead<br>• Payment fraud, counterfeit electronics and buyer/seller trust risks common to marketplaces<br>• Dependence on internet/power infrastructure reliability for target users |

**Overall feasibility verdict:** ElectroMart is feasible as a coursework MVP across all five dimensions, provided scope is phased — core marketplace functionality first, secondary features (chat, price comparison, tracking) next — and compliance/security are designed in from the start rather than retrofitted.
