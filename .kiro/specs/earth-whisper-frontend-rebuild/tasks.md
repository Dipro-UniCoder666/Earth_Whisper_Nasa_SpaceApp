# Implementation Plan: Earth Whisper Frontend Rebuild (Prompt 1)

## Overview

A complete visual and UX reset of the existing React + TypeScript + Vite application. Work proceeds in dependency order: design system tokens first, then shell components, then constants and routing, then landing page sections, then inner pages, and finally build verification. No files under `src/features/`, `src/data/`, or any Leaflet/map component are touched. All new components use named exports and `@/` path aliases throughout.

---

## Tasks

- [ ] 1. Repository Audit
  - [ ] 1.1 Audit existing repo structure and document preserved files
    - Verify all files under `src/features/evidence/services/`, `src/features/investigation/`, `src/features/casefile/`, `src/features/investigator/`, `src/data/`, and Leaflet map components exist and are untouched
    - Confirm `src/components/app/AppShell.tsx`, `AppNavbar.tsx`, `InvestigationWelcome.tsx`, `InvestigationHeader.tsx`, `HeroEarth.tsx`, `HeroCTA.tsx`, `GlassCard.tsx`, `IconButton.tsx`, `LoadingScreen.tsx`, and `AquaByteMark.tsx` are present and unchanged
    - Record any missing or unexpected files before writing any new code
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - [ ] 1.2 Verify preserved files compile without errors
    - Run `tsc --noEmit` (or `tsc -b`) in `app/` and confirm zero TypeScript errors originate from preserved backend files before any new code is added
    - Note and document any pre-existing errors so they are not attributed to Prompt 1 changes
    - _Requirements: 1.5_

- [ ] 2. Design System
  - [ ] 2.1 Rewrite `src/styles/globals.css` with the full token set
    - Replace the existing partial `@theme` block with the complete token definitions from the design spec: all background, brand, semantic, text, border, and utility color tokens; full type scale (`--text-xs` through `--text-5xl`); `--font-display` and `--font-sans`; spacing scale (`--space-1` through `--space-24`); layout tokens (`--max-width-content`, `--max-width-narrow`, `--page-gutter-mobile`, `--page-gutter-desktop`); breakpoints (`--breakpoint-sm` through `--breakpoint-2xl`)
    - Keep existing Leaflet control overrides and `@layer base` body/focus/selection rules; update token references in those rules to the new names
    - Add the `.skip-link` utility class as specified in the design (hidden until `:focus-visible`, positioned absolute, z-index 9999)
    - Add backward-compatibility aliases in a `:root` block: `--color-sky → var(--color-border-subtle)`, `--color-white → var(--color-surface)`, `--color-muted → var(--color-text-muted)`, `--color-earth-green → var(--color-scientific-positive)` so preserved components continue to compile and render correctly
    - Remove the top-level `@import url(…fonts…)` line from `globals.css` (fonts will move to `index.html`)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 4.1, 4.2, 4.3, 4.4, 3.1, 3.2, 3.4_
  - [ ] 2.2 Update `src/styles/animations.css` with missing classes and reduced-motion overrides
    - The file already contains most keyframes and classes; verify `ew-anim-fade`, `ew-draw` with `--ew-dash`, and the four ambient loop classes are present with the exact durations and easings from the design spec (`ew-orbit-slow` 90s, `ew-orbit-slow-reverse` 130s, `ew-drift` 7s, `ew-pulse-ring` 3.2s)
    - Confirm the `@media (prefers-reduced-motion: reduce)` block at the bottom sets `animation: none !important` on all four ambient classes
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 3. Branding and Identity
  - [ ] 3.1 Update `src/components/branding/EarthWhisperLogo.tsx` with size and variant props
    - Extend the props interface to add `size?: 'sm' | 'md' | 'lg'` (default `'md'`) and `variant?: 'default' | 'inverse'` (default `'default'`)
    - Implement size mapping for mark pixel size and wordmark rem size per design spec table (`sm`: 22px / 1.1rem; `md`: 28px / 1.35rem; `lg`: 36px / 1.75rem)
    - Implement variant mapping: `default` uses `--color-navy` text and standard mark colors; `inverse` uses `--color-text-inverse` text and white/aqua mark colors
    - Render wordmark as two DOM `<span>` elements ("EARTH" and "WHISPER") using `--font-display`, with `role="img"` on the wrapper div and `aria-hidden="true"` on the spans; when used as a nav link the parent `<Link>` will supply `aria-label="Earth Whisper home"` and the inner div will be `aria-hidden="true"`
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  - [ ] 3.2 Update `public/favicon.svg` with the Earth Whisper mark SVG
    - Replace the existing favicon with the 32×32 SVG specified in the design doc: navy circle (`#073B66`), aqua arc path (`#18B7C9`), blue latitude arc (`#0B5EA8`), with correct `xmlns`, `viewBox="0 0 32 32"`, and `fill="none"`
    - _Requirements: 6.5_
  - [ ] 3.3 Update `index.html` with Google Fonts preconnect and stylesheet links
    - Remove any existing Google Fonts `@import` from CSS (done in 2.1) and add the three `<link>` tags to `<head>`: `rel="preconnect"` to `fonts.googleapis.com`, `rel="preconnect" crossorigin` to `fonts.gstatic.com`, and the full stylesheet link loading Fraunces (ital, opsz, wght) and Inter (wght 400–700) with `display=swap`
    - _Requirements: 3.3_

- [ ] 4. Shell Components
  - [ ] 4.1 Create `src/components/common/SkipLink.tsx`
    - Render `<a href="#main-content" className="skip-link">Skip to main content</a>` with no props
    - The `.skip-link` CSS class (added in 2.1) handles the hide-until-focused behavior; this component is a thin wrapper
    - Export as named export `SkipLink`
    - _Requirements: 17.3_
  - [ ] 4.2 Create `src/components/layout/AppLayout.tsx`
    - Render `<SkipLink />`, `<GlobalNav />`, `<main id="main-content" tabIndex={-1}><Outlet /></main>`, and `<Footer />` in that order, with a Fragment wrapper (no extra DOM div)
    - Import `SkipLink` from `@/components/common/SkipLink`, `GlobalNav` from `@/components/navigation/GlobalNav`, `Footer` from `@/components/common/Footer`, `Outlet` from `react-router-dom`
    - Export as named export `AppLayout`
    - _Requirements: 13.2, 14.2, 17.1, 17.3_
  - [ ] 4.3 Create `src/components/navigation/GlobalNav.tsx`
    - Implement scroll-aware behavior: `useState(false)` for `scrolled`, `useEffect` attaches `window` scroll listener, sets `scrolled = true` when `window.scrollY > 80`, applies CSS class `global-nav--scrolled` which adds `background-color: rgba(247, 251, 255, 0.92)`, `backdrop-filter: blur(12px)`, `border-bottom`, and `box-shadow`
    - Implement active link detection via `useLocation()` from `react-router-dom`; active link receives `font-weight: 600` and a `border-bottom: 2px solid var(--color-primary)` underline (non-color indicator per a11y requirement)
    - Desktop structure: `<header role="banner">` → `<div class="global-nav__inner">` → `<Link to="/" aria-label="Earth Whisper home"><EarthWhisperLogo /></Link>` + `<nav aria-label="Primary">` with `<Link>` to `/`, `/investigate`, `/about` and an `<a>` to NASA Space Apps (external, `target="_blank" rel="noreferrer"`) + `<button aria-label="Open navigation menu" aria-expanded={menuOpen} aria-controls="mobile-menu" className="md:hidden">`
    - Below `md` (768px) the inline `<nav>` is hidden; above `md` the mobile trigger button is hidden
    - Renders `<MobileMenu open={menuOpen} onClose={…} links={NAV_LINKS} />` sourcing links from `NAV_LINKS` constant
    - On `onClose`, return focus to the trigger button via `triggerRef.current?.focus()`
    - Export as named export `GlobalNav`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.8, 7.9, 7.10, 17.2, 17.5_
  - [ ] 4.4 Update `src/components/navigation/MobileMenu.tsx` with focus trap and Escape key handling
    - Add `panelRef = useRef<HTMLDivElement>(null)` and assign to the overlay div
    - Add `useEffect` that activates when `open === true`: queries all focusable elements inside the panel, traps Tab/Shift+Tab between first and last, calls `onClose()` on `Escape` key, and focuses the first element on open
    - Update internal navigation links to use `<Link to={href}>` (react-router-dom) for internal routes and `<a href>` only for external links
    - Add `id="mobile-menu"` to the root dialog div
    - _Requirements: 7.6, 7.7, 17.7_
  - [ ] 4.5 Create `src/components/common/Footer.tsx`
    - Render a `<footer>` element with: `<EarthWhisperLogo variant="inverse" size="sm" />` and AquaByte attribution on the left column; links to `/about` (via `<Link>`) and NASA Space Apps (via `<a target="_blank" rel="noreferrer">`) plus challenge details (NISAR mission, "Dancing with the SARs", "NASA Space Apps Challenge 2026") on the right column; a full-width disclaimer below: "Earth Whisper is a submission for the NASA Space Apps Challenge and is not an official NASA product."
    - Desktop: two-column layout; below `md` (768px): single column stacked
    - All links keyboard-accessible; no icon-only buttons
    - Export as named export `Footer`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 16.5_
  - [ ] 4.6 Update `src/components/common/Button.tsx` with design token alignment
    - Replace hardcoded hex values in `variantClasses` with token references: `primary` uses `var(--color-navy)` background and `var(--color-text-inverse)` text with `hover:bg-[var(--color-primary)]`; `secondary` uses `var(--color-surface)` background, `var(--color-navy)` text, `var(--color-border)` border with hover states using `var(--color-primary)` and `var(--color-surface-subtle)`; `ghost` uses `var(--color-surface-subtle)` hover
    - Update focus ring to reference `var(--color-focus-ring)` instead of `var(--color-primary)` directly
    - Keep `forwardRef` signature, `ButtonProps` interface, and `Button.displayName` unchanged so existing callers (`HeroCTA`, `InvestigationWelcome`) continue to work
    - _Requirements: 2.6, 17.2_

- [ ] 5. Constants and Routing
  - [ ] 5.1 Update `src/lib/constants.ts` with ROUTES.about and NAV_LINKS
    - Add `about: '/about'` to the `ROUTES` constant (change `as const` type to include the new key)
    - Replace `NAV_LINKS_LANDING` with `NAV_LINKS` typed as `readonly NavLink[]` using a `NavLink` interface `{ label: string; to: string; external: boolean }`, containing entries for Home, Investigate, About, and NASA Space Apps (external)
    - Keep all existing string constants (`APP_NAME`, `APP_TAGLINE`, `TEAM_NAME`, `CHALLENGE_NAME`, `CHALLENGE_YEAR`) unchanged
    - _Requirements: 15.3_
  - [ ] 5.2 Update `src/router.tsx` to add the `/about` route and switch to `AppLayout`
    - Import `AppLayout` from `@/components/layout/AppLayout` and `AboutPage` from `@/pages/AboutPage`
    - Change the root route element from `<App />` to `<AppLayout />`; `App.tsx` itself remains a bare `<Outlet />` and is not modified
    - Add `{ path: ROUTES.about, element: <AboutPage /> }` as a sibling of the other top-level routes
    - Preserve the existing `/investigate/map` and `/investigate/case/:candidateId` sub-routes unchanged so Leaflet pages continue to route correctly
    - _Requirements: 15.1, 15.2, 15.4, 15.5_

- [ ] 6. Landing Page
  - [ ] 6.1 Create `src/components/hero/HeroSection.tsx`
    - Layout: CSS Grid with `lg:grid-cols-[1.05fr_1fr]`; below `lg` (1024px) collapses to single column (text above visual)
    - Content: eyebrow `<p>` label ("NASA Space Apps 2026 × NISAR Earth Observation"), `<h1>` rendering the wordmark text in `--font-display` at `--text-5xl` scale, tagline italic `<p>` ("Where Earth's Changes Tell Their Story"), mission description 2–3 sentences in `--font-sans --text-lg`, primary `<Button>` wrapped in `<Link to="/investigate">`, secondary anchor `<a href="#story-section">`
    - Visual: reuse preserved `<HeroEarth />` (already `aria-hidden="true"`) wrapped in a div with `ew-anim-scale` and 0.3s `animationDelay`
    - Entrance animations: apply `ew-anim-rise` with staggered inline `animationDelay` (`0.05s`, `0.15s`, `0.28s`, `0.40s`, `0.55s`) to successive text children
    - Zero imports from `src/features/`
    - Export as named export `HeroSection`
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 9.10, 16.3_
  - [ ] 6.2 Create `src/pages/sections/StorySection.tsx`
    - Section `id="story-section"` with `<h2>` heading: "How an Earth Whisper Investigation Works"
    - Five ordered phase items using lucide-react icons (`Eye`, `GitCompare`, `Archive`, `Search`, `BookOpen`): OBSERVE, COMPARE, COLLECT CLUES, INVESTIGATE, UNDERSTAND — each with a 1–2 sentence description exactly matching the design spec content
    - Desktop: horizontal step connector layout; below `md` (768px): single-column vertical connector
    - All phase content is static inline strings; zero service imports
    - Export as named export `StorySection`
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 16.4_
  - [ ] 6.3 Create `src/pages/sections/ScienceDifferentiationSection.tsx`
    - Section heading (`--font-display` `<h2>`): "Not a Disaster Dashboard"
    - Three principle cards with lucide-react icon + `<h3>` heading + `<p>` body text: "Evidence Independence", "Honest Uncertainty", "Observation Over Prediction" — with exact body text from the design spec
    - Section background: `--color-surface-subtle` with `aria-hidden="true"` decorative SVG topographic pattern
    - No fake percentages, no AI prediction claims
    - Use `--font-display` for section/card headings and `--font-sans` for body text
    - Export as named export `ScienceDifferentiationSection`
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 16.4_
  - [ ] 6.4 Create `src/pages/sections/SciencePreviewSection.tsx`
    - Render a fully static, illustrative investigation card showing: a "Sample investigation structure" badge, a mock event title "Himalayan Terrain Anomaly — Prototype Event", five labeled evidence slots (RADAR / TERRAIN / WEATHER / OPTICAL / WATER) with static placeholder badge states
    - All mock data declared as `const` objects within the component file; zero imports from `src/features/evidence/`, no service calls, no `fetch`
    - Include a `<Link to="/investigate">` CTA button
    - Clearly label all preview content as illustrative (not real data)
    - Export as named export `SciencePreviewSection`
    - _Requirements: 12.1, 12.2, 12.3, 12.4_
  - [ ] 6.5 Update `src/pages/LandingPage.tsx` to compose all four sections
    - Replace the existing content with a bare composition: `<HeroSection />`, `<StorySection />`, `<ScienceDifferentiationSection />`, `<SciencePreviewSection />`
    - Remove imports of `LandingNavbar`, `Hero`, and the inline `<footer>` (GlobalNav and Footer are now provided by `AppLayout`)
    - Import sections from `@/components/hero/HeroSection`, `@/pages/sections/StorySection`, `@/pages/sections/ScienceDifferentiationSection`, `@/pages/sections/SciencePreviewSection`
    - Zero imports from `src/features/`
    - _Requirements: 9.1–9.10, 10.1–10.5, 11.1–11.5, 12.1–12.4, 16.1_

- [ ] 7. Inner Pages
  - [ ] 7.1 Update `src/pages/InvestigationPage.tsx` as a layout shell
    - Replace the existing `AppShell` + `InvestigationWelcome` import with a clean shell implementation
    - Render two `<section>` elements: one with `<h1 id="investigation-heading">Investigation Workspace</h1>`, a brief "being built" description, and a `<Link to="/">← Back to Earth Whisper</Link>`; one with `<h2 id="flow-heading">The Investigation Flow</h2>` presenting the OBSERVE → COMPARE → COLLECT CLUES → INVESTIGATE → UNDERSTAND steps as static text (same content as StorySection, no shared import required)
    - Add three `<div data-slot="…" aria-hidden="true" />` placeholders for future map/observation/evidence panel slots
    - Apply `--page-gutter-mobile/desktop` and `--max-width-content` container for responsive layout
    - Zero imports from `src/features/`, evidence services, fingerprint service, investigation map, or any Leaflet component
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 16.1_
  - [ ] 7.2 Create `src/pages/AboutPage.tsx`
    - Render four `<section>` elements inside a `<div>` (the `<main>` wrapper is provided by `AppLayout`): Purpose, AquaByte Team, NISAR Mission, and NASA Space Apps Challenge 2026
    - Include `<h1>About Earth Whisper</h1>` and the challenge name "Dancing with the SARs" as specified
    - Include an external `<a href="https://www.spaceappschallenge.org/" target="_blank" rel="noreferrer">` link to the Space Apps website
    - All content is static placeholder text; zero evidence service calls
    - Export as named export `AboutPage`
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [ ] 8. Build Verification
  - [ ] 8.1 Run `tsc -b && vite build` and resolve all TypeScript and Vite errors
    - Execute in the `app/` directory; fix any type errors introduced by new or modified files (do not modify preserved files)
    - Common sources to check: missing named exports, incorrect `@/` alias resolution, `any` types introduced in new files, `aria-*` props typed as booleans instead of strings, incorrect `RefObject` typing on `MobileMenu`'s `panelRef`
    - Confirm `AppLayout` does not import from `src/features/`, `InvestigationPage` does not import from `src/features/`, `AboutPage` does not import from `src/features/`, `SciencePreviewSection` does not import from `src/features/`
    - _Requirements: 18.1, 18.2, 18.4, 1.5_
  - [ ] 8.2 Run `oxlint src/` and resolve all lint errors on new and modified files
    - Execute `npx oxlint src/` in the `app/` directory; address any unused imports, missing `key` props, or other lint violations in newly created or modified files only
    - Confirm no new peer-dependency warnings were introduced (no changes to `package.json` or `package-lock.json`)
    - _Requirements: 18.3, 18.5_

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP (none in this plan — all tasks are required for the build gate)
- Tasks 1–2 are foundational; all component tasks (3–7) depend on the design system tokens being in place
- The `AppLayout` pattern (task 4.2) is a prerequisite for the router update (5.2) and all page work (6–7)
- The `ROUTES.about` constant (5.1) must exist before `router.tsx` (5.2) or `GlobalNav` (4.3) reference it
- No existing files under `src/features/`, `src/data/`, or any Leaflet/map component are modified at any point
- `HeroEarth.tsx`, `HeroCTA.tsx`, `AppShell.tsx`, `AppNavbar.tsx`, `LandingNavbar.tsx`, and all `src/features/**` components are preserved and never imported by new shell or page components
- The `src/pages/sections/` directory is a new folder created as part of task 6

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1", "2.2"] },
    { "id": 2, "tasks": ["3.1", "3.2", "3.3"] },
    { "id": 3, "tasks": ["5.1"] },
    { "id": 4, "tasks": ["4.1", "4.6"] },
    { "id": 5, "tasks": ["4.3", "4.4", "4.5"] },
    { "id": 6, "tasks": ["4.2"] },
    { "id": 7, "tasks": ["5.2"] },
    { "id": 8, "tasks": ["6.1", "6.2", "6.3", "6.4", "7.2"] },
    { "id": 9, "tasks": ["6.5", "7.1"] },
    { "id": 10, "tasks": ["8.1"] },
    { "id": 11, "tasks": ["8.2"] }
  ]
}
```
