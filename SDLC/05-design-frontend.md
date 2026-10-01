# Design — Frontend

## Visual identity
- **Theme**: Paris/Eiffel Tower motif — indigo dusk, brass ironwork,
  awning rouge — used as the brand mark, a hero silhouette, and a
  diagonal cross-hatch background texture standing in for wrought-iron
  trusswork.
- **Palette** (`:root` CSS variables):
  | Token | Hex | Use |
  |---|---|---|
  | `--paper` | `#F7F2E6` | page background |
  | `--card` | `#FFFFFF` | cards/panels |
  | `--ink` / `--ink-dim` | `#1C2541` / `#5C6584` | primary/secondary text |
  | `--gold` / `--gold-dim` | `#B8923D` / `#8F701F` | brand accent, CTAs, brand mark |
  | `--wine` / `--wine-dim` | `#8C3B4A` / `#6E2E3A` | eyebrow labels, secondary accent |
  | `--iron` | `#26261F` | dark UI surfaces |
- **Typography**: Playfair Display (`--display`, serif) for headings,
  Jost (`--body`, sans) for UI text, JetBrains Mono (`--mono`) for
  prices, SKUs, and spec rows — a deliberate "boutique storefront meets
  receipt printout" contrast.
- **Brand mark**: the Eiffel Tower silhouette (`.tower-mark`) is drawn
  in pure CSS as a clipped stack of bars, not an image asset — zero
  extra network requests for the logo.

## Wireframe → component mapping
Each screen in `04-wireframes.md` maps 1:1 to a `render*()` function
(`renderAuth`, `renderShop`/`renderGrid`, `renderProductModal`,
`renderCartDrawer`, `renderCheckoutModal`, `renderTrack`/`renderOrders`,
`renderSell`/`renderAnalytics`, `renderAdmin`, `renderChatWidget`), each
returning an HTML string composed inside `render()`, the single render
entry point that re-draws the app from `state` on every change.

## Responsiveness
Layout is fluid rather than breakpoint-heavy: grids and flex layouts
reflow from desktop widths down to ~360px mobile viewports; modals and
the cart drawer become full-width sheets on narrow screens.

## Accessibility (WCAG 2.1 / ISO/IEC 40500)
- A skip-to-content link bypasses repeated navigation.
- Visible keyboard focus indicators throughout.
- Icon-only controls (cart, chat launcher, quantity steppers) carry
  descriptive `aria-label`s.
- Modals and the cart drawer use `role="dialog"` / `aria-modal="true"`
  and close on `Escape`, so they work with screen readers and keyboard
  navigation, not just pointer input.

## Interaction details worth noting
- Search input is **debounced** (`debounce()`) so filtering doesn't
  re-render on every keystroke.
- A lightweight 3D tilt effect (`initCardTilt3d()`) is applied to
  product cards for a boutique-catalogue feel, implemented in pure JS
  (pointer position → CSS transform), no animation library.
