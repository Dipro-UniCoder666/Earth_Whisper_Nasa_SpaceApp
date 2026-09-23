# Design Document — Earth Whisper Frontend Rebuild (Prompt 1)

## Overview

This document specifies the technical design for **Prompt 1: Foundation** of the Earth Whisper visual rebuild. The objective is a complete CSS and component reset that delivers a cohesive, scientifically elegant interface on top of the existing React + TypeScript + Vite stack, while leaving every piece of scientific backend code untouched.

The work falls into four broad categories:

1. **Design system** — a single CSS file (`globals.css`) plus an animation file (`animations.css`) that encode every visual decision as named tokens.
2. **Shell components** — `EarthWhisperLogo`, `GlobalNav`, `MobileMenu`, `AppLayout`, `Footer`, and a `SkipLink` accessibility primitive.
3. **Page implementations** — `LandingPage` (Hero, Story, ScienceDifferentiation, SciencePreview sections), `InvestigationPage` (layout shell only), and `AboutPage` (placeholder).
4. **Routing** — an updated `App.tsx`, a `ROUTES` constant, and a clean `router.tsx` that preserves all existing sub-routes.

### Key Constraints

- **Zero changes** to any file under `src/features/`, `src/data/`, or any Leaflet map component.
- **Zero new dependencies** — all work uses what is already installed: React 19, react-router-dom 7, Tailwind CSS 4, lucide-react, TypeScript 6.
- **Build gate** — `tsc -b && vite build` and `npx oxlint src/` must exit zero after all files are written.

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│  main.tsx  →  RouterProvider  →  router.tsx       │
│               ↓                                    │
│            App.tsx (bare Outlet)                  │
│               ↓                                    │
│        AppLayout.tsx (GlobalNav + Outlet + Footer)│
│         /              │              \            │
│  LandingPage    InvestigationPage    AboutPage    │
│  (Hero+Story    (shell/layout       (placeholder) │
│   +ScienceDiff  only, no evidence                 │
│   +SciencePrev) services)                         │
│                                                    │
│  Preserved: InvestigationMapPage, Case…Page       │
│             (still wrapped by AppShell legacy)    │
└──────────────────────────────────────────────────┘
```

`AppLayout` is the new unified layout wrapper used by the three top-level pages. The existing `AppShell` (used by `InvestigationMapPage` and `CaseInvestigationPage`) is preserved unchanged to avoid touching any Leaflet-dependent pages.

---

## Components and Interfaces

This section covers the full component hierarchy, each component's props interface, behavior contract, and accessibility specification.

## Component Hierarchy

```
App.tsx
└── AppLayout.tsx
    ├── SkipLink.tsx              (first focusable element, a11y)
    ├── GlobalNav.tsx
    │   ├── EarthWhisperLogo.tsx  (updated)
    │   └── MobileMenu.tsx        (updated)
    ├── <main id="main-content">
    │   └── <Outlet>              (routed page)
    │       ├── LandingPage.tsx
    │       │   ├── HeroSection.tsx
    │       │   │   ├── HeroEarth.tsx     (reused SVG illustration)
    │       │   │   └── HeroCTA.tsx       (reused)
    │       │   ├── StorySection.tsx
    │       │   ├── ScienceDifferentiationSection.tsx
    │       │   └── SciencePreviewSection.tsx
    │       ├── InvestigationPage.tsx     (shell)
    │       └── AboutPage.tsx             (placeholder)
    └── Footer.tsx
```

Components that sit outside this tree (preserved, not modified):
- `AppShell.tsx` → wraps `InvestigationMapPage` and `CaseInvestigationPage`
- All `src/features/**` components and services
- `InvestigationWelcome.tsx`, `InvestigationHeader.tsx`

---

## File Structure

Only new or modified files are listed. Every path marked `[PRESERVE]` is not touched.

```
app/
├── index.html                          [MODIFIED] — add Google Fonts preconnect
├── public/
│   └── favicon.svg                     [MODIFIED] — updated Earth Whisper mark SVG
└── src/
    ├── App.tsx                         [MODIFIED] — bare Outlet, no change in logic
    ├── router.tsx                      [MODIFIED] — add /about route; preserve others
    ├── main.tsx                        [UNCHANGED]
    │
    ├── lib/
    │   └── constants.ts                [MODIFIED] — add ROUTES.about + NAV_LINKS
    │
    ├── styles/
    │   ├── globals.css                 [MODIFIED] — full design token rewrite
    │   └── animations.css              [MOSTLY PRESERVED, minor additions]
    │
    ├── components/
    │   ├── branding/
    │   │   ├── EarthWhisperLogo.tsx    [MODIFIED] — size/variant props, DOM wordmark
    │   │   └── AquaByteMark.tsx        [PRESERVE]
    │   │
    │   ├── navigation/
    │   │   ├── GlobalNav.tsx           [NEW] — replaces AppNavbar + LandingNavbar
    │   │   ├── MobileMenu.tsx          [MODIFIED] — add focus trap, Escape key
    │   │   ├── AppNavbar.tsx           [PRESERVE — still used by AppShell]
    │   │   └── LandingNavbar.tsx       [PRESERVE — no longer used; safe to keep]
    │   │
    │   ├── layout/
    │   │   └── AppLayout.tsx           [NEW] — GlobalNav + Outlet + Footer wrapper
    │   │
    │   ├── common/
    │   │   ├── SkipLink.tsx            [NEW] — accessibility skip link
    │   │   ├── Button.tsx              [MODIFIED] — token-aligned styles
    │   │   ├── Footer.tsx              [NEW]
    │   │   ├── GlassCard.tsx           [PRESERVE]
    │   │   ├── IconButton.tsx          [PRESERVE]
    │   │   └── LoadingScreen.tsx       [PRESERVE]
    │   │
    │   ├── hero/
    │   │   ├── HeroSection.tsx         [NEW] — landing hero section (was Hero.tsx)
    │   │   ├── HeroCTA.tsx             [PRESERVE]
    │   │   └── HeroEarth.tsx           [PRESERVE — already matches design spec]
    │   │
    │   └── app/                        [PRESERVE all three files]
    │
    ├── pages/
    │   ├── LandingPage.tsx             [MODIFIED] — full rebuild with AppLayout
    │   ├── InvestigationPage.tsx       [MODIFIED] — shell only, uses AppLayout
    │   ├── AboutPage.tsx               [NEW]
    │   ├── InvestigationMapPage.tsx    [PRESERVE]
    │   └── CaseInvestigationPage.tsx   [PRESERVE]
    │
    └── features/                       [PRESERVE all]
```

---

## Design System Specification

### CSS Architecture

All design tokens live in a single `:root` block at the top of `src/styles/globals.css`. The file uses the **Tailwind CSS v4 `@theme` block** pattern that is already present, but the tokens below are added both as Tailwind theme tokens (for utility class generation) and as standard CSS custom properties accessible anywhere.

Because the project uses `@tailwindcss/vite` (v4), tokens can be defined once in `@theme` and used as both `var(--token)` and via generated Tailwind utilities.

### Color Tokens

```css
@theme {
  /* ── Backgrounds ──────────────────────────────── */
  --color-bg:             #F7FBFF;   /* page background, very pale blue-white     */
  --color-surface:        #FFFFFF;   /* card / panel elevated surface              */
  --color-surface-subtle: #F0F6FF;   /* alternate panel, form backgrounds          */

  /* ── Brand ────────────────────────────────────── */
  --color-navy:           #073B66;   /* primary dark, headings, logo               */
  --color-primary:        #0B5EA8;   /* interactive primary, links, CTA            */
  --color-aqua:           #18B7C9;   /* accent, highlight, anomaly indicators      */
  --color-aqua-soft:      #DDF7FA;   /* tinted background for aqua-context areas   */

  /* ── Scientific semantic ──────────────────────── */
  --color-scientific-positive: #4FAF83;  /* confirmed / positive signal            */
  --color-scientific-warning:  #D97706;  /* uncertain / caution                    */
  --color-scientific-anomaly:  #DC2626;  /* anomaly / alert                        */

  /* ── Text ─────────────────────────────────────── */
  --color-text:           #0D1B2A;   /* primary body text (contrast ≥ 4.5:1 on bg) */
  --color-text-muted:     #4A6280;   /* secondary / supporting text                */
  --color-text-inverse:   #F7FBFF;   /* text on dark navy/primary surfaces         */

  /* ── Borders ──────────────────────────────────── */
  --color-border:         #C8D8E8;   /* default component border                   */
  --color-border-subtle:  #E4EEF8;   /* hairline separator, divider                */

  /* ── Utility ──────────────────────────────────── */
  --color-focus-ring:     #0B5EA8;   /* keyboard focus outline                     */
}
```

**Contrast verification:**
- `--color-text` (`#0D1B2A`) on `--color-bg` (`#F7FBFF`): relative luminance ratio ≈ **14.5:1** ✓
- `--color-text-inverse` (`#F7FBFF`) on `--color-navy` (`#073B66`): ratio ≈ **12.4:1** ✓
- `--color-text-muted` (`#4A6280`) on `--color-bg` (`#F7FBFF`): ratio ≈ **4.7:1** ✓ (passes AA for body)

### Typography Tokens

```css
@theme {
  --font-display: 'Fraunces', ui-serif, Georgia, serif;
  --font-sans:    'Inter', ui-sans-serif, system-ui, sans-serif;

  /* ── Type scale ───────────────────────────────── */
  --text-xs:   0.75rem;    /* 12px — captions, labels            */
  --text-sm:   0.875rem;   /* 14px — secondary body, UI labels   */
  --text-base: 1rem;       /* 16px — body copy                   */
  --text-lg:   1.125rem;   /* 18px — lead paragraph              */
  --text-xl:   1.25rem;    /* 20px — card heading                */
  --text-2xl:  1.5rem;     /* 24px — section sub-heading         */
  --text-3xl:  1.875rem;   /* 30px — section heading             */
  --text-4xl:  2.25rem;    /* 36px — page sub-title              */
  --text-5xl:  3rem;       /* 48px — hero / page title           */
}
```

**Heading assignments:**
| Element | Font | Size (desktop) | Line height | Letter spacing |
|---------|------|----------------|-------------|----------------|
| `h1` | `--font-display` | `--text-5xl` (responsive up to 4.4rem) | `0.95` | `-0.03em` |
| `h2` | `--font-display` | `--text-3xl` | `1.1` | `-0.02em` |
| `h3` | `--font-display` | `--text-2xl` | `1.2` | `-0.01em` |
| Body | `--font-sans` | `--text-base` | `1.6` | `0` |
| Label | `--font-sans` | `--text-sm` | `1.4` | `0.05em` uppercase |

Google Fonts import (placed in `index.html` `<head>` for optimal LCP):

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400&family=Inter:wght@400;500;600;700&display=swap"
  rel="stylesheet"
/>
```

### Spacing Tokens

```css
@theme {
  --space-1:  0.25rem;   /*  4px */
  --space-2:  0.5rem;    /*  8px */
  --space-3:  0.75rem;   /* 12px */
  --space-4:  1rem;      /* 16px */
  --space-5:  1.25rem;   /* 20px */
  --space-6:  1.5rem;    /* 24px */
  --space-8:  2rem;      /* 32px */
  --space-10: 2.5rem;    /* 40px */
  --space-12: 3rem;      /* 48px */
  --space-14: 3.5rem;    /* 56px */
  --space-16: 4rem;      /* 64px */
  --space-20: 5rem;      /* 80px */
  --space-24: 6rem;      /* 96px */

  --max-width-content: 80rem;   /* 1280px */
  --max-width-narrow:  45rem;   /* 720px  */

  --page-gutter-mobile:  1.5rem;   /* 24px, < 768px */
  --page-gutter-desktop: 2.5rem;   /* 40px, ≥ 768px */
}
```

### Breakpoints

Defined as Tailwind screen values (v4 `@theme`):

```css
@theme {
  --breakpoint-sm:  40rem;    /* 640px  */
  --breakpoint-md:  48rem;    /* 768px  */
  --breakpoint-lg:  64rem;    /* 1024px */
  --breakpoint-xl:  80rem;    /* 1280px */
  --breakpoint-2xl: 90rem;    /* 1440px */
}
```

---

## Animation Specification

All animation definitions live in `src/styles/animations.css`, which is already imported in `main.tsx`. The file is extended with the missing `ew-anim-fade` class and the `--ew-dash` property usage, but the existing keyframes are preserved.

### Entrance Animations (one-shot, applied on mount)

| Class | Keyframe | Duration | Easing | Effect |
|-------|----------|----------|--------|--------|
| `ew-anim-rise` | `ew-rise-in` | 0.8s | `cubic-bezier(0.16, 1, 0.3, 1)` | `opacity 0→1`, `translateY 14px→0` |
| `ew-anim-scale` | `ew-scale-in` | 1.1s | `cubic-bezier(0.16, 1, 0.3, 1)` | `opacity 0→1`, `scale 0.94→1` |
| `ew-anim-fade` | `ew-fade` | 1.0s | `ease-out` | `opacity 0→1` |

Stagger pattern in Hero: `0.05s`, `0.15s`, `0.28s`, `0.40s`, `0.55s` on successive children via inline `style={{ animationDelay }}`.

### Ambient Loop Animations (CSS `infinite`, applied to SVG elements)

| Class | Keyframe | Duration | Notes |
|-------|----------|----------|-------|
| `ew-orbit-slow` | `ew-rotate-slow` | 90s linear | Clockwise rotation; `transform-origin: center` |
| `ew-orbit-slow-reverse` | `ew-rotate-slow` | 130s linear reverse | Counter-clockwise |
| `ew-drift` | `ew-drift` | 7s ease-in-out | `translateY 0 → -6px → 0` |
| `ew-pulse-ring` | `ew-pulse-ring` | 3.2s | `scale 0.85→2.1`, `opacity 0.9→0` |

### SVG Path Draw

```css
.ew-draw {
  stroke-dasharray: var(--ew-dash, 600);
  animation: ew-draw 1.8s cubic-bezier(0.65, 0, 0.35, 1) both;
}
```

`--ew-dash` is set inline on each `<path>` to match its approximate total length.

### Reduced Motion Override

The `prefers-reduced-motion: reduce` rule in `globals.css` sets `animation-duration: 0.01ms !important` and `transition-duration: 0.01ms !important` on `*`. A secondary block in `animations.css` explicitly sets `animation: none !important` on the four ambient classes to ensure they are fully stopped (not just sped up to 0.01ms, which would still tick).

```css
@media (prefers-reduced-motion: reduce) {
  .ew-orbit-slow,
  .ew-orbit-slow-reverse,
  .ew-drift,
  .ew-pulse-ring {
    animation: none !important;
  }
  /* entrance classes — duration already 0.01ms via globals.css wildcard */
}
```

---

## Component Specifications

### SkipLink

**File:** `src/components/common/SkipLink.tsx`

**Purpose:** WCAG 2.1 SC 2.4.1 — provides keyboard users a way to bypass navigation and jump to `#main-content`.

**Props:** none

**Behavior:**
- Rendered as the very first child of `AppLayout`, before `GlobalNav`.
- Visually hidden until focused: `position: absolute; transform: translateY(-100%)` → on `:focus-visible`: `transform: translateY(0)`.
- On activation (`Enter`/`Space`), scrolls focus to `<main id="main-content">`.
- Stays in DOM at all times (not conditionally rendered).

**HTML:** `<a href="#main-content" className="skip-link">Skip to main content</a>`

**CSS class `.skip-link`** (in `globals.css`):
```css
.skip-link {
  position: absolute;
  top: var(--space-4);
  left: var(--space-4);
  z-index: 9999;
  padding: var(--space-2) var(--space-4);
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  font-weight: 600;
  border-radius: 4px;
  transform: translateY(-150%);
  transition: transform 0.2s ease-out;
}
.skip-link:focus-visible {
  transform: translateY(0);
}
```

---

### EarthWhisperLogo (updated)

**File:** `src/components/branding/EarthWhisperLogo.tsx`

**Props:**
```ts
interface EarthWhisperLogoProps {
  className?: string;
  markOnly?: boolean;      // default false — show mark + wordmark
  size?: 'sm' | 'md' | 'lg';  // default 'md'
  variant?: 'default' | 'inverse';  // default 'default'
}
```

**Size mapping:**
| size | mark px | wordmark rem |
|------|---------|-------------|
| `sm` | 22px | 1.1rem |
| `md` | 28px | 1.35rem |
| `lg` | 36px | 1.75rem |

**Variant mapping:**
- `default`: navy text, standard mark colors
- `inverse`: `--color-text-inverse` text, white/aqua mark colors (for dark footers)

**Wordmark structure:**
```tsx
<div aria-label="Earth Whisper" role="img">
  <span aria-hidden="true">EARTH</span>
  {/* line break via block/flex layout */}
  <span aria-hidden="true">WHISPER</span>
</div>
```

When used as a nav link, the parent `<Link>` supplies the `aria-label="Earth Whisper home"`. The inner `role="img"` div is then `aria-hidden="true"`.

---

### GlobalNav

**File:** `src/components/navigation/GlobalNav.tsx`

**Props:** none (reads route from `useLocation`)

**State:**
```ts
const [menuOpen, setMenuOpen] = useState(false);
const [scrolled, setScrolled] = useState(false);
```

**Scroll behavior:** `useEffect` attaches a `scroll` listener. When `window.scrollY > 80`, sets `scrolled = true`. This adds class `global-nav--scrolled` to the `<header>`, which applies:
```css
.global-nav--scrolled {
  background-color: rgba(247, 251, 255, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border-subtle);
  box-shadow: 0 1px 0 rgba(7, 59, 102, 0.06);
}
```

This only activates on `LandingPage` (which starts with a transparent nav); on other pages the nav has a background from the start.

**Desktop structure:**
```html
<header class="global-nav [global-nav--scrolled]" role="banner">
  <div class="global-nav__inner">
    <Link to="/" aria-label="Earth Whisper home">
      <EarthWhisperLogo />
    </Link>
    <nav aria-label="Primary">
      <Link to="/">Home</Link>
      <Link to="/investigate">Investigate</Link>
      <Link to="/about">About</Link>
      <a href="https://www.spaceappschallenge.org/" target="_blank" rel="noreferrer">
        NASA Space Apps ↗
      </a>
    </nav>
    <button aria-label="Open navigation menu" class="global-nav__menu-trigger md:hidden" />
  </div>
  <MobileMenu open={menuOpen} onClose={…} />
</header>
```

**Active link detection:** `useLocation()` from react-router-dom. Compare `location.pathname` to each link's `to` prop. Active link receives an additional visual marker:
- Non-color indicator: `font-weight: 600` and an underline `border-bottom: 2px solid var(--color-primary)`.
- Color indicator (supplementary): `color: var(--color-primary)`.

**Keyboard:** All `<Link>` and `<a>` elements are naturally keyboard-focusable. The menu trigger `<button>` uses `aria-expanded={menuOpen}` and `aria-controls="mobile-menu"`.

**Responsiveness:**
- `< md (768px)`: inline `<nav>` is `display: none`; menu trigger button is shown.
- `≥ md`: trigger is `display: none`; nav is shown.

---

### MobileMenu (updated)

**File:** `src/components/navigation/MobileMenu.tsx`

**Props:** (unchanged interface, but now uses `Link` for internal routes)
```ts
interface MobileMenuLink {
  label: string;
  href: string;
  external?: boolean;
}
interface MobileMenuProps {
  open: boolean;
  onClose: () => void;
  links: readonly MobileMenuLink[];
}
```

**Focus trap implementation:**
```ts
useEffect(() => {
  if (!open) return;
  const panel = panelRef.current;
  if (!panel) return;
  const focusable = panel.querySelectorAll<HTMLElement>(
    'a[href], button, [tabindex]:not([tabindex="-1"])'
  );
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Escape') { onClose(); return; }
    if (e.key !== 'Tab') return;
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault(); last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault(); first.focus();
    }
  }
  document.addEventListener('keydown', handleKeyDown);
  first?.focus();
  return () => document.removeEventListener('keydown', handleKeyDown);
}, [open, onClose]);
```

When closed, `onClose()` is called and the caller (`GlobalNav`) returns focus to the trigger button via `triggerRef.current?.focus()`.

**ARIA:** `role="dialog"`, `aria-modal="true"`, `aria-label="Navigation menu"`, `id="mobile-menu"`.

Internal links rendered as `<Link to={href}>` (react-router-dom) for SPA navigation. External links remain `<a>`.

---

### AppLayout

**File:** `src/components/layout/AppLayout.tsx`

**Props:** none (uses `<Outlet>`)

```tsx
export function AppLayout() {
  return (
    <>
      <SkipLink />
      <GlobalNav />
      <main id="main-content" tabIndex={-1}>
        <Outlet />
      </main>
      <Footer />
    </>
  );
}
```

`tabIndex={-1}` on `<main>` allows the SkipLink's `href="#main-content"` to programmatically focus it on older browsers.

---

### Footer

**File:** `src/components/common/Footer.tsx`

**Props:** none

**Structure:**
```
<footer>
  ┌─────────────────────────────────────────────┐
  │ [EarthWhisperLogo inverse] [AquaByte team]  │
  │                                             │
  │ Links: About · NASA Space Apps ↗            │
  │                                             │
  │ NASA Space Apps Challenge 2026              │
  │ "Dancing with the SARs"                     │
  │ NISAR Earth Observation Mission             │
  │                                             │
  │ ─────────────────────────────────────────   │
  │ Earth Whisper is a submission for the NASA  │
  │ Space Apps Challenge and is not an official │
  │ NASA product.                               │
  └─────────────────────────────────────────────┘
```

**Desktop layout:** Two columns — brand on left, links/mission info on right.
**Mobile (< 768px):** Single column, stacked.

**Accessibility:** `<footer>` element, all links keyboard-accessible, external NASA link has `target="_blank" rel="noreferrer"`, no icon-only buttons.

---

### Button (updated)

**File:** `src/components/common/Button.tsx`

Token-aligned update: replaces all hardcoded hex values with `var(--color-*)` tokens. Interface and forwardRef signature unchanged to avoid breaking `InvestigationWelcome`, `HeroCTA`, and other callers.

**Variant styles (token-aligned):**
```ts
const variantClasses = {
  primary:   'bg-[var(--color-navy)] text-[var(--color-text-inverse)] hover:bg-[var(--color-primary)]',
  secondary: 'bg-[var(--color-surface)] text-[var(--color-navy)] border border-[var(--color-border)] hover:border-[var(--color-primary)] hover:bg-[var(--color-surface-subtle)]',
  ghost:     'bg-transparent text-[var(--color-navy)] hover:bg-[var(--color-surface-subtle)]',
}
```

**Focus ring:** `focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--color-focus-ring)]`

**Touch target:** `lg` size uses `py-4` (16px padding each side + ~24px text ≈ 56px height). `md` uses `py-2.5` ≈ 44px minimum.

---

### LandingPage

**File:** `src/pages/LandingPage.tsx`

```tsx
export function LandingPage() {
  return (
    <>
      <HeroSection />
      <StorySection />
      <ScienceDifferentiationSection />
      <SciencePreviewSection />
    </>
  );
}
```

No imports from evidence services. All data is static strings defined within the component files or in `constants.ts`.

#### HeroSection

**File:** `src/components/hero/HeroSection.tsx` (new file; `Hero.tsx` preserved for AppShell compatibility if needed)

**Layout:** CSS Grid, `lg:grid-cols-[1.05fr_1fr]`. Below `lg` (1024px): single column, text above visual.

**Content:**
- Eyebrow label: `"NASA Space Apps 2026 × NISAR Earth Observation"` — `<p>` with `--text-xs` uppercase tracking
- `<h1>` with EarthWhisperLogo in display mode (stacked "EARTH / WHISPER") or the raw text at large scale
- Tagline italic: `"Where Earth's Changes Tell Their Story"` — `<p>` using `--font-display` italic
- Body: 2–3 sentence mission description, `--font-sans --text-lg`
- CTAs: Primary `<Button>` linking to `/investigate` via react-router-dom `<Link>`; secondary anchor scrolling to `#story-section`

**Visual:** Reuses `<HeroEarth />` (existing, preserved, already `aria-hidden="true"`). Wrapped in `ew-anim-scale` with 0.3s delay.

**Entrance animations:** All text children have `ew-anim-rise` with staggered `animationDelay` inline style.

#### StorySection

**File:** `src/components/hero/StorySection.tsx` → actually placed at `src/pages/sections/StorySection.tsx`

> Note: To keep the `src/components/hero/` folder untouched (it's effectively used by old pages too), landing-page-specific sections go in `src/pages/sections/`.

**New folder:** `src/pages/sections/` containing:
- `StorySection.tsx`
- `ScienceDifferentiationSection.tsx`
- `SciencePreviewSection.tsx`

**StorySection content:**
```
Section heading: "How an Earth Whisper Investigation Works"
id="story-section"

Five phases, ordered, each with icon glyph (lucide-react) + name + 1–2 sentence description:
1. OBSERVE — "NISAR radar scans the same patch of ground repeatedly, building a precise record of how it looks from space."
2. COMPARE — "We compare the before and after: how much did the surface change? In which direction? How quickly?"
3. COLLECT CLUES — "Independent data streams — terrain shape, weather history, water levels, optical imagery, fire records — are each assessed separately."
4. INVESTIGATE — "The evidence is laid out without a predetermined conclusion. We ask: what could plausibly explain what we see?"
5. UNDERSTAND — "A scientific assessment, with explicit uncertainty. Not a label — an inquiry."
```

**Layout:** Horizontal step connector on desktop; single column with vertical connector on mobile.

**Lucide icons:** `Eye`, `GitCompare`, `Archive`, `Search`, `BookOpen` — one per phase.

#### ScienceDifferentiationSection

**File:** `src/pages/sections/ScienceDifferentiationSection.tsx`

**Section heading** (`--font-display`): `"Not a Disaster Dashboard"`

**Three principles (cards with icon + heading + body):**
1. **Evidence Independence** — "Each data source is assessed separately. Radar, terrain, weather, optical imagery, fire, and water clues are never blended into a single score before their individual signals are understood."
2. **Honest Uncertainty** — "We state explicitly what we know, what we are uncertain about, and what the current data cannot tell us. A conclusion without stated confidence is not a scientific finding."
3. **Observation Over Prediction** — "Earth Whisper does not predict events. It documents changes that have already been observed by NISAR and asks what the evidence supports — not what an algorithm guesses."

No fake percentages, no fabricated AI claims.

**Section background:** `--color-surface-subtle` with subtle topographic contour SVG pattern (`aria-hidden="true"`).

#### SciencePreviewSection

**File:** `src/pages/sections/SciencePreviewSection.tsx`

**Content:** An illustrative, static schematic of an investigation card showing:
- A labeled `"Sample investigation structure"` badge
- A mock event title: `"Himalayan Terrain Anomaly — Prototype Event"`
- Five evidence slots labeled RADAR / TERRAIN / WEATHER / OPTICAL / WATER with static placeholder badge states (no live data, no service calls)
- A call-to-action `<Link to="/investigate">` Button

**Implementation note:** This component renders only static JSX. There are zero imports from `src/features/evidence/` or any service. The mock data is declared as `const` objects within the component file.

---

### InvestigationPage (shell)

**File:** `src/pages/InvestigationPage.tsx`

**Design:**
```tsx
export function InvestigationPage() {
  return (
    <div className="investigation-shell">
      <section aria-labelledby="investigation-heading">
        <h1 id="investigation-heading">Investigation Workspace</h1>
        <p>The investigation workspace is being built. The architecture is in place.</p>
        <Link to="/">← Back to Earth Whisper</Link>
      </section>

      <section aria-labelledby="flow-heading" id="observe-flow">
        <h2 id="flow-heading">The Investigation Flow</h2>
        {/* OBSERVE → COMPARE → COLLECT CLUES → INVESTIGATE → UNDERSTAND */}
        {/* Same static text as StorySection, no live data */}
      </section>

      {/* Named section slots for future Prompt 2 integration */}
      <div data-slot="map-workspace" aria-hidden="true" />
      <div data-slot="observation-panel" aria-hidden="true" />
      <div data-slot="evidence-panel" aria-hidden="true" />
    </div>
  );
}
```

**Zero imports from:** evidence services, fingerprint service, investigation map, nisarService, locationService, or any `src/features/**` component.

**Fully responsive:** uses `--page-gutter-mobile/desktop` and max-width container.

---

### AboutPage

**File:** `src/pages/AboutPage.tsx`

**Structure:**
```
<main id="main-content">
  <h1>About Earth Whisper</h1>

  <section> Purpose
    What Earth Whisper is, why it exists, what problem it addresses.
  </section>

  <section> AquaByte Team
    Brief team introduction.
  </section>

  <section> NISAR Mission
    What NISAR is, why it matters, its observational capabilities.
  </section>

  <section> NASA Space Apps Challenge 2026
    Challenge name: "Dancing with the SARs"
    External link to https://www.spaceappschallenge.org/ (new tab, rel="noreferrer")
  </section>
</main>
```

No evidence service calls, no live data.

---

## Data Models

Prompt 1 introduces no new runtime data models. All content is static. The following type shapes are defined in `src/lib/constants.ts` for navigation configuration:

```ts
// Navigation link shape used by GlobalNav and MobileMenu
interface NavLink {
  label: string;
  to: string;
  external: boolean;
}

// Route keys — exported as ROUTES constant
type RouteKey = 'landing' | 'investigate' | 'about';
const ROUTES: Record<RouteKey, string>;
```

The preserved scientific data models remain unchanged in `src/features/` and are not referenced by any Prompt 1 component.

## Routing Configuration

### `src/lib/constants.ts` (updated)

```ts
export const APP_NAME = 'Earth Whisper';
export const APP_TAGLINE = "Where Earth's Changes Tell Their Story";
export const TEAM_NAME = 'AquaByte';
export const CHALLENGE_NAME = 'Dancing with the SARs';
export const CHALLENGE_YEAR = 'NASA Space Apps Challenge 2026';

export const ROUTES = {
  landing:    '/',
  investigate: '/investigate',
  about:      '/about',
} as const;

export const NAV_LINKS = [
  { label: 'Home',            to: ROUTES.landing,    external: false },
  { label: 'Investigate',     to: ROUTES.investigate, external: false },
  { label: 'About',           to: ROUTES.about,       external: false },
  { label: 'NASA Space Apps', to: 'https://www.spaceappschallenge.org/', external: true },
] as const;
```

### `src/router.tsx` (updated)

```tsx
import { createBrowserRouter } from 'react-router-dom';
import { AppLayout }              from '@/components/layout/AppLayout';
import { LandingPage }            from '@/pages/LandingPage';
import { InvestigationPage }      from '@/pages/InvestigationPage';
import { AboutPage }              from '@/pages/AboutPage';
import { InvestigationMapPage }   from '@/pages/InvestigationMapPage';   // preserved
import { CaseInvestigationPage }  from '@/pages/CaseInvestigationPage';  // preserved
import { ROUTES }                 from '@/lib/constants';

export const router = createBrowserRouter([
  {
    element: <AppLayout />,          // GlobalNav + main + Footer
    children: [
      { path: ROUTES.landing,                                  element: <LandingPage /> },
      { path: ROUTES.investigate,                              element: <InvestigationPage /> },
      { path: `${ROUTES.investigate}/map`,                     element: <InvestigationMapPage /> },
      { path: `${ROUTES.investigate}/case/:candidateId`,       element: <CaseInvestigationPage /> },
      { path: ROUTES.about,                                    element: <AboutPage /> },
    ],
  },
]);
```

**Key routing decisions:**

1. `AppLayout` (not `App.tsx`) is the route element for all top-level routes. `App.tsx` becomes a bare pass-through that simply re-exports or renders `<Outlet />` — the existing pattern is preserved.
2. `InvestigationMapPage` and `CaseInvestigationPage` are kept in the router unchanged and still use `AppShell` internally (which uses `AppNavbar`, not `GlobalNav`). This avoids touching those pages. In a future prompt, their shell can be migrated.
3. `AppLayout` is used only for the three new/rebuilt pages. The legacy pages continue to work through `AppShell`.

> **Alternative considered:** wrapping everything in `AppLayout` and removing `AppShell`. Rejected because `AppShell` contains the subtle grid backdrop and `AppNavbar` styling that the map and case pages rely on; touching them risks breaking Leaflet integration outside of Prompt 1 scope.

---

## Data Flow

Prompt 1 has **no live data flow**. All content is static.

```
Static strings (constants.ts, inline JSX)
    ↓
Page components (LandingPage, InvestigationPage, AboutPage)
    ↓
Rendered HTML
```

The preserved pages (`InvestigationMapPage`, `CaseInvestigationPage`) retain their existing data flow through evidence/investigation services — but those are untouched.

---

## CSS Architecture

### File organization

```
src/styles/
├── globals.css       — @theme tokens, base HTML resets, focus styles, leaflet overrides,
│                       skip-link utility, prefers-reduced-motion universal rule
└── animations.css    — keyframe definitions, animation utility classes,
                        reduced-motion overrides for ambient classes
```

Both files are imported in `main.tsx` (already the case). No CSS modules, no additional CSS files.

### Token usage rule

Components use `var(--color-*)` references inside Tailwind's arbitrary value syntax:
```tsx
className="text-[var(--color-navy)] bg-[var(--color-surface)]"
```

Or via Tailwind theme utility classes where the token has a matching generated utility (e.g., `text-navy` if Tailwind v4 generates it from `@theme`).

The project already uses `@tailwindcss/vite` v4, which reads `@theme` tokens and generates utilities. Both usage patterns are valid.

### No hardcoded hex values in TSX

The sole exception is inline SVG `fill`/`stroke` attributes, where Tailwind classes and CSS `var()` don't apply. In those cases, hardcoded values matching the design tokens are acceptable (e.g., `fill="#073B66"` for `--color-navy`). The `HeroEarth.tsx` SVG already follows this pattern.

### Mobile-first CSS

All layout uses `min-width` breakpoints. Base styles target 390px; breakpoint prefixes (`md:`, `lg:`) add desktop enhancements.

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Reduced-Motion Compliance

*For any* element rendered by the application that carries one of the Earth Whisper animation classes (`ew-anim-rise`, `ew-anim-scale`, `ew-anim-fade`, `ew-orbit-slow`, `ew-orbit-slow-reverse`, `ew-drift`, `ew-pulse-ring`), when the `prefers-reduced-motion: reduce` media query is active, that element's computed `animation-duration` SHALL be effectively zero (≤ 1ms), and any element that would otherwise have `opacity: 0` at rest SHALL instead have `opacity: 1`.

**Validates: Requirements 5.3, 9.9**

### Property 2: Science Preview Has No Side Effects

*For any* render of the `SciencePreviewSection` component, regardless of the surrounding application state, the global `fetch` function SHALL NOT be called, no evidence service function SHALL be invoked, and no module from `src/features/evidence/` SHALL be imported at the time of rendering.

**Validates: Requirements 12.4, 13.6**

### Property 3: No Horizontal Overflow Across Viewport Widths

*For any* viewport width `w` in the range `[390px, 1440px]`, when any of the three primary pages (`/`, `/investigate`, `/about`) is rendered at that width, no element in the document tree SHALL have a `scrollWidth` greater than `clientWidth` on the document body (i.e., no horizontal scrollbar SHALL appear).

**Validates: Requirements 16.1**

### Property 4: Skip Link Is the First Focusable Element on Every Page

*For any* route in `{/, /investigate, /about}`, after the page renders, the first element in the natural Tab order SHALL be a link pointing to `#main-content`, with accessible text "Skip to main content".

**Validates: Requirements 17.3**

### Property 5: Decorative SVGs Are Aria-Hidden on Every Page

*For any* route in `{/, /investigate, /about}`, every SVG element in the rendered DOM that is decorative (not conveying unique information to sighted users) SHALL have `aria-hidden="true"`. No decorative SVG SHALL have a role or accessible name that would cause a screen reader to announce it.

**Validates: Requirements 17.4**

---

## Error Handling

No live data calls occur in Prompt 1, so there are no async error states to handle for the new pages. The following error considerations apply:

**Route not found:** react-router-dom v7 will render a blank page for unknown routes. A future prompt should add a 404 boundary; it is out of scope for Prompt 1.

**Font load failure:** Google Fonts failing to load will fall back to `ui-serif, Georgia, serif` and `ui-sans-serif, system-ui, sans-serif` respectively. These are specified in the font tokens and provide acceptable visual degradation.

**Preserved pages:** `InvestigationMapPage` and `CaseInvestigationPage` retain their own error handling from the existing codebase.

---

## Testing Strategy

### Unit Tests (example-based)

Prompt 1 does not create test files — build verification is the acceptance gate. However, the following unit test targets are specified for subsequent prompt iterations:

- `EarthWhisperLogo` renders wordmark with display font class
- `GlobalNav` renders all three route links
- `GlobalNav` marks active link with `font-weight: 600` + border indicator
- `MobileMenu` opens on trigger, closes on Escape, returns focus to trigger
- `Footer` contains NASA attribution text
- `SkipLink` renders as first DOM child of `AppLayout`
- `AboutPage` contains "Dancing with the SARs" text
- `InvestigationPage` contains no evidence service imports (static analysis)

### Property-Based Tests

If Vitest is added in a future prompt, the five correctness properties above are the targets for property-based test implementation using [fast-check](https://github.com/dubzzz/fast-check).

**Configuration:** Minimum 100 runs per property. Tag format: `Feature: earth-whisper-frontend-rebuild, Property N: <property text>`.

**Example test structure (Property 1):**
```ts
// Feature: earth-whisper-frontend-rebuild, Property 1: Reduced-motion compliance
import * as fc from 'fast-check';
const ANIMATION_CLASSES = ['ew-anim-rise','ew-anim-scale','ew-anim-fade','ew-orbit-slow','ew-orbit-slow-reverse','ew-drift','ew-pulse-ring'];
test('all animation classes respect prefers-reduced-motion', () => {
  fc.assert(
    fc.property(fc.constantFrom(...ANIMATION_CLASSES), (cls) => {
      // mock matchMedia reduced-motion, render an element with cls,
      // assert computed animation-duration <= 1ms
    })
  );
});
```

**Why PBT applies here:** Animation classes and their behavior under `prefers-reduced-motion` constitute a universal property: it must hold for *every* element bearing *any* animation class. A property test with generated class selections and simulated media query state will find gaps that example tests might miss. Similarly, the no-horizontal-overflow property benefits from testing across a generated range of viewport widths rather than just two or three spot-checks.

### Build Verification

```bash
# TypeScript + Vite build (zero errors expected)
cd app && tsc -b && vite build

# Lint (zero errors expected)
cd app && npx oxlint src/
```

**What the build verifies:**
- All TypeScript types resolve correctly (including `@/` alias paths)
- No unused imports that would fail oxlint
- No missing module references
- Vite tree-shakes successfully with no circular dependency errors

**Pre-build checklist:**
1. All `import` paths in new files use `@/` alias (not relative `../../`)
2. Every new component exports a named export (no default exports except `App.tsx` per convention)
3. No `any` types introduced in new files
4. All `aria-*` attributes are strings (not booleans) in JSX
5. `MobileMenu` `panelRef` is typed as `RefObject<HTMLDivElement>`
6. `AppLayout` does not import from `src/features/`
7. `InvestigationPage` does not import from `src/features/`
8. `AboutPage` does not import from `src/features/`
9. `SciencePreviewSection` does not import from `src/features/`

---

## Hero SVG Illustration (HeroEarth) — Reference

The existing `HeroEarth.tsx` already matches the design specification fully:

- ✅ Inline SVG composition, no raster images
- ✅ Abstract Earth circle with terrain-form landmass paths
- ✅ Two subtle orbital arc paths using `ew-orbit-slow` / `ew-orbit-slow-reverse`
- ✅ Pulsing dots for change-detection points using `ew-pulse-ring`
- ✅ Scientific annotation labels (NISAR OBSERVATION, CHANGE DETECTED)
- ✅ `aria-hidden="true"` on the outer `<div>`
- ✅ Scientific illustration aesthetic using the design system color palette

This component is **preserved as-is**.

---

## Favicon

**File:** `public/favicon.svg`

The existing file is replaced with a cleaner 32×32 version of the Earth Whisper mark: the radar-arc-over-sphere glyph, using `--color-navy` (`#073B66`) and `--color-aqua` (`#18B7C9`). It is a stand-alone SVG with `xmlns` attribute, appropriate `viewBox`, and no external dependencies.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none">
  <circle cx="16" cy="16" r="9" fill="#073B66"/>
  <path d="M16 4c-3.2 3.4-4.8 7.6-4.8 12s1.6 8.6 4.8 12" stroke="#18B7C9" stroke-width="1.5" fill="none" opacity="0.9"/>
  <path d="M4.5 11.5c5-2.3 18-2.3 23 0" stroke="#0B5EA8" stroke-width="1.5" fill="none" opacity="0.8"/>
</svg>
```

---

## Appendix: Token Alias Mapping (Old → New)

To help with migration, the following table maps old token names (used in preserved components) to their new equivalents:

| Old token | New token | Notes |
|-----------|-----------|-------|
| `--color-sky` | `--color-border-subtle` | `#EAF6FF` ≈ `#E4EEF8` — preserved in globals as alias |
| `--color-white` | `--color-surface` | Same value `#FFFFFF` |
| `--color-muted` | `--color-text-muted` | Value changed: `#6D8294` → `#4A6280` (higher contrast) |
| `--color-earth-green` | `--color-scientific-positive` | Same value `#4FAF83` |
| `--color-text` | `--color-text` | Value updated: `#12304A` → `#0D1B2A` (higher contrast) |

To avoid breaking existing components in `AppShell`, `AppNavbar`, `InvestigationMapPage`, etc., the old token names are **kept as aliases** in `globals.css`:

```css
:root {
  --color-sky:         var(--color-border-subtle);
  --color-white:       var(--color-surface);
  --color-muted:       var(--color-text-muted);
  --color-earth-green: var(--color-scientific-positive);
}
```

This ensures zero regressions in preserved components without any file modifications.
