# Requirements Document

## Introduction

Earth Whisper is a scientific investigation platform created by AquaByte for the NASA Space Apps Challenge 2026 ("Dancing with the SARs"), built on the NASA-ISRO NISAR mission. It transforms NISAR satellite radar observations of Earth's changing surface into structured scientific investigations — presenting surface-change events not as labelled disasters, but as evidence-driven inquiries: What changed? What evidence do we have? What could explain it? What are we still uncertain about?

This requirements document covers **Prompt 1: Foundation** — a full visual/UX reset of the existing React + TypeScript + Vite application. The scope is limited to: repository preservation, design system, visual identity, landing page, investigation shell, about route placeholder, global navigation, footer, responsive design, routing, and build verification. Scientific backend code (evidence services, fingerprint service, terrain/water/fire/radar/optical/weather services, investigation types, demo data) is explicitly preserved and must not be altered.

---

## Glossary

- **Earth_Whisper**: The application platform built by AquaByte, presented to end users as "EARTH WHISPER."
- **AquaByte**: The team that created Earth Whisper.
- **NISAR**: NASA-ISRO Synthetic Aperture Radar satellite mission; the core scientific data source.
- **Design_System**: The collection of CSS custom properties (tokens), typography definitions, spacing scale, and color palette that govern all visual styling.
- **Landing_Page**: The public-facing page at route `/`, comprising Hero, Story, Science_Differentiation, and Science_Preview sections.
- **Investigation_Shell**: The placeholder workspace at route `/investigate`, presenting structural layout without live scientific data.
- **About_Page**: The placeholder page at route `/about` describing Earth Whisper, its science, and its data sources.
- **Global_Nav**: The persistent navigation component rendered across all routes, providing access to `/`, `/investigate`, and `/about`.
- **Mobile_Nav**: The slide-in or overlay navigation menu rendered on viewports below the desktop breakpoint.
- **Footer**: The persistent bottom-of-page component rendered across all routes.
- **Hero_Section**: The first visible section of the Landing_Page, containing the wordmark, tagline, mission context, and primary call-to-action.
- **Story_Section**: The section of the Landing_Page that explains the scientific investigation philosophy (OBSERVE → COMPARE → COLLECT CLUES → INVESTIGATE → UNDERSTAND).
- **Science_Differentiation_Section**: The section of the Landing_Page that distinguishes Earth Whisper from disaster dashboards.
- **Science_Preview_Section**: The section of the Landing_Page that illustrates what an investigation looks like, without live data.
- **Design_Token**: A named CSS custom property that encodes a single design decision (e.g., a color, font size, or spacing unit).
- **Wordmark**: The typographic logotype rendering of "EARTH WHISPER" using the defined brand typeface.
- **Viewport_Desktop**: Screen widths of 1440px and above.
- **Viewport_Mobile**: Screen widths down to 390px.
- **prefers-reduced-motion**: A CSS media feature indicating the user has requested minimal animation.
- **WCAG_AA**: Web Content Accessibility Guidelines 2.1 Level AA contrast and keyboard navigation standards.

---

## Requirements

### Requirement 1: Repository Audit and Scientific Backend Preservation

**User Story:** As a developer, I want all existing scientific backend code preserved unchanged through the visual rebuild, so that no investigation logic, evidence services, or data structures are lost.

#### Acceptance Criteria

1. THE Earth_Whisper application SHALL preserve without modification all files under `src/features/evidence/services/` (fingerprintService, radarService, terrainService, weatherService, opticalService, fireService, waterService).
2. THE Earth_Whisper application SHALL preserve without modification all files under `src/features/investigation/` (types, hooks, services, components).
3. THE Earth_Whisper application SHALL preserve without modification `src/features/casefile/types.ts`, `src/features/investigator/types.ts`, `src/data/demoEvent.ts`, and `src/data/eventTypes.ts`.
4. THE Earth_Whisper application SHALL preserve without modification the Leaflet map infrastructure in `src/features/investigation/components/InvestigationMap.tsx` and all related map components.
5. WHEN the build step runs after the visual rebuild, THE Earth_Whisper application SHALL produce zero TypeScript errors in the preserved scientific backend files.

---

### Requirement 2: Design System — Color Tokens

**User Story:** As a designer, I want a complete, named color token system defined in CSS custom properties, so that every component references tokens rather than hardcoded values.

#### Acceptance Criteria

1. THE Design_System SHALL define the following background tokens: `--color-bg` (soft off-white/very pale blue, e.g. `#F7FBFF`), `--color-surface` (slightly elevated surface, e.g. `#FFFFFF`), and `--color-surface-subtle` (subtle card/panel background).
2. THE Design_System SHALL define the following brand tokens: `--color-navy` (deep navy, e.g. `#073B66`), `--color-primary` (NASA-like blue, e.g. `#0B5EA8`), `--color-aqua` (aqua accent, e.g. `#18B7C9`), and `--color-aqua-soft` (aqua tint for backgrounds, e.g. `#DDF7FA`).
3. THE Design_System SHALL define the following semantic tokens: `--color-scientific-positive` (restrained green, e.g. `#4FAF83`), `--color-scientific-warning` (amber, e.g. `#D97706`), `--color-scientific-anomaly` (red/coral, e.g. `#DC2626`).
4. THE Design_System SHALL define the following text tokens: `--color-text` (primary text, high contrast on `--color-bg`), `--color-text-muted` (secondary/subdued text), `--color-text-inverse` (text on dark surfaces).
5. THE Design_System SHALL define the following border and utility tokens: `--color-border` (default border), `--color-border-subtle` (hairline border), `--color-focus-ring` (keyboard focus indicator color).
6. WHEN a component uses a color, THE Design_System SHALL require that component to reference a Design_Token rather than a hardcoded hex value, with the sole exception of inline SVG fill/stroke values where token reference is not possible.
7. THE Design_System SHALL maintain a minimum contrast ratio of 4.5:1 between `--color-text` and `--color-bg`, and between `--color-text-inverse` and any dark surface it is used on, per WCAG_AA.

---

### Requirement 3: Design System — Typography

**User Story:** As a designer, I want a restrained, scientifically elegant typographic system, so that the reading experience feels premium and purposeful rather than generic.

#### Acceptance Criteria

1. THE Design_System SHALL define a display typeface token `--font-display` mapped to "Fraunces" (variable optical-size, serif) with system fallbacks `ui-serif, Georgia, serif`.
2. THE Design_System SHALL define a body typeface token `--font-sans` mapped to "Inter" (variable, sans-serif) with system fallbacks `ui-sans-serif, system-ui, sans-serif`.
3. THE Design_System SHALL load both typefaces from Google Fonts with `display=swap` to prevent layout shift.
4. THE Design_System SHALL define a modular type scale with named tokens for sizes from `--text-xs` (0.75rem) through `--text-5xl` (3rem+), with explicit `line-height` and `letter-spacing` values for each heading level.
5. THE Design_System SHALL assign `--font-display` exclusively to heading elements (h1, h2, h3) and the Wordmark; all body copy, labels, and UI text SHALL use `--font-sans`.
6. WHEN a heading uses `--font-display`, THE Design_System SHALL apply `-webkit-font-smoothing: antialiased` and `text-rendering: optimizeLegibility` to the html element.

---

### Requirement 4: Design System — Spacing and Layout

**User Story:** As a developer, I want a consistent spacing and layout system, so that all components align to a shared grid and padding rhythm.

#### Acceptance Criteria

1. THE Design_System SHALL define a base spacing unit of 4px and provide a scale of named tokens from `--space-1` (4px) through `--space-24` (96px).
2. THE Design_System SHALL define a maximum content width of 1280px (`--max-width-content`) and a narrow content width of 720px (`--max-width-narrow`) for reading-focused layouts.
3. THE Design_System SHALL define horizontal page padding tokens: `--page-gutter-mobile` (24px) for viewports below 768px, and `--page-gutter-desktop` (40px) for viewports 768px and above.
4. THE Design_System SHALL define breakpoints: `sm` (640px), `md` (768px), `lg` (1024px), `xl` (1280px), `2xl` (1440px).

---

### Requirement 5: Design System — Motion and Animation

**User Story:** As a designer, I want a small, purposeful animation library, so that the interface feels alive without being distracting or inaccessible.

#### Acceptance Criteria

1. THE Design_System SHALL define entrance animation classes: `ew-anim-rise` (opacity 0→1, translateY 14px→0, 0.8s ease-out), `ew-anim-scale` (opacity 0→1, scale 0.94→1, 1.1s ease-out), and `ew-anim-fade` (opacity 0→1, 1s ease-out).
2. THE Design_System SHALL define ambient loop classes: `ew-orbit-slow` (360° rotation, 90s linear infinite), `ew-orbit-slow-reverse` (counter-rotation, 130s), `ew-drift` (vertical 0→-6px→0, 7s infinite), and `ew-pulse-ring` (scale + opacity pulse, 3.2s infinite).
3. WHILE the `prefers-reduced-motion: reduce` media query is active, THE Design_System SHALL set all animation durations to 0.01ms and all transition durations to 0.01ms for every element, including ambient loops.
4. THE Design_System SHALL define a CSS custom property `--ew-dash` used by the `ew-draw` path animation class for SVG stroke-dashoffset animation.

---

### Requirement 6: Visual Identity — Wordmark and Branding

**User Story:** As a brand owner, I want a clean Earth Whisper wordmark and AquaByte attribution rendered consistently, so that the product identity is clear on every page.

#### Acceptance Criteria

1. THE Earth_Whisper application SHALL render the "EARTH WHISPER" Wordmark using `--font-display` at the appropriate weight and size, with "EARTH" and "WHISPER" on separate lines or as two distinct typographic elements per the design specification.
2. THE Earth_Whisper application SHALL render the AquaByte team attribution adjacent to the Wordmark in the Global_Nav and Footer, using `--font-sans` at a subdued scale.
3. THE Earth_Whisper application SHALL use a single `EarthWhisperLogo` component that accepts size/variant props and renders the Wordmark using DOM elements (no raster image) to remain crisp at all resolutions.
4. WHEN the Wordmark is used as a navigation link, THE Earth_Whisper application SHALL wrap it in an `<a>` element pointing to `/` with an accessible `aria-label` of "Earth Whisper home".
5. THE Earth_Whisper application SHALL serve a valid `favicon.svg` at the document root representing the Earth Whisper mark.

---

### Requirement 7: Global Navigation

**User Story:** As a visitor, I want clear, accessible navigation to all primary routes, so that I can move between the landing page, investigation workspace, and about page from anywhere in the application.

#### Acceptance Criteria

1. THE Global_Nav SHALL render a persistent header on every route (`/`, `/investigate`, `/about`) containing the Wordmark and navigation links.
2. THE Global_Nav SHALL include links to: `/` (labelled "Home" or the Wordmark), `/investigate` (labelled "Investigate"), and `/about` (labelled "About").
3. THE Global_Nav SHALL include an external link to the NASA Space Apps Challenge website, opening in a new tab with `rel="noreferrer"`.
4. WHILE the current route matches a navigation link's `href`, THE Global_Nav SHALL apply an active visual state to that link that is distinguishable from non-active links.
5. WHEN the viewport is below the `md` breakpoint (768px), THE Global_Nav SHALL hide the inline link list and display a Mobile_Nav trigger button.
6. WHEN the Mobile_Nav trigger is activated, THE Mobile_Nav SHALL open and display all navigation links in a full-width overlay or slide-in panel.
7. WHEN the Mobile_Nav is open and the user activates the close control or presses the Escape key, THE Mobile_Nav SHALL close and return focus to the trigger button.
8. THE Global_Nav SHALL use a `<header>` element containing a `<nav aria-label="Primary">` for the link list.
9. THE Global_Nav SHALL be keyboard-navigable such that all links are reachable via Tab key and activatable via Enter key.
10. WHEN the page is scrolled more than 80px from the top on the Landing_Page, THE Global_Nav SHALL apply a subtle background and border-bottom to remain legible over content.

---

### Requirement 8: Footer

**User Story:** As a visitor, I want a consistent footer on every page, so that team attribution, challenge context, and secondary links are always available.

#### Acceptance Criteria

1. THE Footer SHALL render on every route and display: the Earth Whisper Wordmark or abbreviated brand mark, AquaByte team attribution, the NASA Space Apps Challenge 2026 name, the challenge title "Dancing with the SARs", and the NISAR mission name.
2. THE Footer SHALL include secondary navigation links to `/about` and to the external NASA Space Apps Challenge website.
3. THE Footer SHALL include a brief statement that Earth Whisper is a submission for the NASA Space Apps Challenge and is not an official NASA product.
4. THE Footer SHALL use a `<footer>` element and all links within it SHALL be keyboard-navigable.
5. THE Footer SHALL be fully visible and legible at all viewport widths from 390px to 1440px.

---

### Requirement 9: Landing Page — Hero Section

**User Story:** As a first-time visitor, I want an immediate, confident introduction to Earth Whisper's purpose, so that I understand what the platform does and feel compelled to explore it.

#### Acceptance Criteria

1. THE Hero_Section SHALL render the "EARTH WHISPER" Wordmark as the primary `<h1>` element on the Landing_Page.
2. THE Hero_Section SHALL render the tagline "Where Earth's Changes Tell Their Story" as a styled subtitle below the `<h1>`.
3. THE Hero_Section SHALL render a concise mission description (2–3 sentences maximum) explaining NISAR's role and Earth Whisper's investigation approach, using `--font-sans` body text.
4. THE Hero_Section SHALL render a mission context label identifying "NASA Space Apps 2026 × NISAR Earth Observation" above the `<h1>`.
5. THE Hero_Section SHALL include a primary call-to-action button linking to `/investigate` and a secondary call-to-action linking to the Story_Section or Science_Differentiation_Section.
6. THE Hero_Section SHALL render a visual element (SVG illustration, abstract Earth/radar visualization, or animated composition) to the right of the text content on Viewport_Desktop.
7. WHEN the viewport is below the `lg` breakpoint (1024px), THE Hero_Section SHALL stack the text content above the visual element in a single column.
8. THE Hero_Section SHALL apply entrance animations from the Design_System to its text and visual elements, with staggered delays.
9. WHEN `prefers-reduced-motion: reduce` is active, THE Hero_Section SHALL display all elements at full opacity without animation.
10. THE Hero_Section primary call-to-action button SHALL have a visible focus ring and be activatable via keyboard.

---

### Requirement 10: Landing Page — Story Section

**User Story:** As a curious visitor, I want to understand Earth Whisper's scientific investigation philosophy, so that I appreciate how it differs from simply reading a disaster feed.

#### Acceptance Criteria

1. THE Story_Section SHALL render a section heading explaining the investigation approach in plain language.
2. THE Story_Section SHALL present the five investigation phases as named, ordered steps: OBSERVE, COMPARE, COLLECT CLUES, INVESTIGATE, UNDERSTAND.
3. THE Story_Section SHALL provide a one-to-two sentence description for each phase explaining what happens at that step, without using fabricated data or false accuracy claims.
4. THE Story_Section SHALL visually differentiate each phase (e.g., numbered sequence, iconography, or progressive connector) while maintaining the restrained scientific aesthetic of the Design_System.
5. WHEN the viewport is below the `md` breakpoint (768px), THE Story_Section SHALL stack the phase items in a single column.

---

### Requirement 11: Landing Page — Science Differentiation Section

**User Story:** As a scientifically literate visitor, I want to understand what makes Earth Whisper's approach rigorous and honest, so that I trust its evidence-driven methodology.

#### Acceptance Criteria

1. THE Science_Differentiation_Section SHALL present at least three named scientific principles that distinguish Earth Whisper from conventional disaster dashboards.
2. THE Science_Differentiation_Section SHALL include the principle of honest uncertainty: explicitly stating what is known, what is uncertain, and what cannot be concluded.
3. THE Science_Differentiation_Section SHALL include the principle of evidence independence: each source (radar, terrain, weather, optical, fire, water) is assessed separately before any cause is attributed.
4. THE Science_Differentiation_Section SHALL not include fake accuracy percentages, fabricated AI prediction claims, or unverifiable statistical claims.
5. THE Science_Differentiation_Section SHALL use `--font-display` for section headings and `--font-sans` for body text.

---

### Requirement 12: Landing Page — Science Preview Section

**User Story:** As a prospective user, I want a preview of what an Earth Whisper investigation looks like, so that I can understand the product before entering the investigation workspace.

#### Acceptance Criteria

1. THE Science_Preview_Section SHALL render a representative visual showing the structure of an Earth Event investigation (e.g., a schematic Earth Event Fingerprint card, evidence clue labels, or the investigation flow diagram).
2. THE Science_Preview_Section SHALL clearly label any preview content as illustrative (e.g., "Sample investigation structure") rather than presenting it as real data.
3. THE Science_Preview_Section SHALL include a call-to-action directing users to `/investigate`.
4. THE Science_Preview_Section SHALL not render live data from the evidence services or fetch any external APIs.

---

### Requirement 13: Investigation Shell

**User Story:** As a developer, I want a structured placeholder at `/investigate`, so that the routing and layout architecture are in place for future investigation feature integration.

#### Acceptance Criteria

1. THE Investigation_Shell SHALL render at the route `/investigate` using the existing React Router setup.
2. THE Investigation_Shell SHALL display the Global_Nav and Footer.
3. THE Investigation_Shell SHALL render a clearly labelled placeholder heading and brief description indicating the investigation workspace is being built, without implying the product is broken.
4. THE Investigation_Shell SHALL include a visible section that describes the OBSERVE → COMPARE → COLLECT CLUES → INVESTIGATE → UNDERSTAND flow at a high level.
5. THE Investigation_Shell SHALL include a navigation pathway back to `/` (landing page).
6. THE Investigation_Shell SHALL not import or invoke any evidence service, fingerprint service, or map component.
7. THE Investigation_Shell SHALL be fully responsive from 390px to 1440px.

---

### Requirement 14: About Page Placeholder

**User Story:** As a curious visitor, I want a placeholder at `/about` that communicates what the about page will contain, so that the route works and the navigation link resolves correctly.

#### Acceptance Criteria

1. THE About_Page SHALL render at the route `/about` using the existing React Router setup.
2. THE About_Page SHALL display the Global_Nav and Footer.
3. THE About_Page SHALL render a heading "About Earth Whisper" and placeholder descriptive text covering: the project's purpose, the AquaByte team, the NISAR mission, and the NASA Space Apps Challenge 2026.
4. THE About_Page SHALL include the challenge name "Dancing with the SARs" and a link to the official NASA Space Apps Challenge website.
5. THE About_Page SHALL not render any live scientific data or call any evidence services.

---

### Requirement 15: Routing and Navigation Structure

**User Story:** As a developer, I want a clean, complete routing configuration for all three routes, so that navigation links resolve correctly and the application renders without 404s.

#### Acceptance Criteria

1. THE Earth_Whisper application SHALL define routes for `/`, `/investigate`, and `/about` in the React Router configuration.
2. THE Earth_Whisper application SHALL preserve the existing sub-routes under `/investigate` (`/investigate/map`, `/investigate/case/:candidateId`) in the router configuration so that future prompts can activate them.
3. THE Earth_Whisper application SHALL export a `ROUTES` constant from `src/lib/constants.ts` that includes keys for `landing` (`/`), `investigate` (`/investigate`), and `about` (`/about`).
4. WHEN a user navigates to `/about`, THE Earth_Whisper application SHALL render the About_Page without a 404 or blank screen.
5. THE Earth_Whisper application SHALL use `react-router-dom` `Link` components for all internal navigation links rather than `<a href>` elements.

---

### Requirement 16: Responsive Design

**User Story:** As a user on any device, I want the application to be fully usable and visually correct from a 390px mobile screen to a 1440px desktop screen, so that the experience is not degraded on smaller viewports.

#### Acceptance Criteria

1. THE Earth_Whisper application SHALL render all page sections without horizontal scrolling at viewport widths between 390px and 1440px.
2. WHEN the viewport is below the `md` breakpoint (768px), THE Global_Nav SHALL hide the inline link list and show the Mobile_Nav trigger exclusively.
3. WHEN the viewport is below the `lg` breakpoint (1024px), THE Hero_Section SHALL collapse to a single-column layout with text above the visual element.
4. WHEN the viewport is below the `md` breakpoint (768px), THE Story_Section and Science_Differentiation_Section SHALL collapse to single-column layouts.
5. THE Footer SHALL reflow its content columns to a stacked single-column layout below the `md` breakpoint (768px).
6. THE Earth_Whisper application SHALL use relative units (rem, em, %) for all typography sizes and a fluid or step-based approach to heading scale between mobile and desktop breakpoints.
7. THE Earth_Whisper application SHALL ensure all interactive elements (buttons, links, nav items) have a minimum touch target size of 44×44px on mobile viewports.

---

### Requirement 17: Accessibility

**User Story:** As a user relying on keyboard navigation or screen reader assistance, I want the application to be navigable and comprehensible without a mouse, so that the experience is inclusive.

#### Acceptance Criteria

1. THE Earth_Whisper application SHALL use semantic HTML elements (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`, `<h1>`–`<h3>`, `<button>`, `<a>`) throughout all pages.
2. THE Earth_Whisper application SHALL provide a visible focus ring on all interactive elements when navigated via keyboard, using `--color-focus-ring` as the outline color.
3. THE Earth_Whisper application SHALL include a skip-to-main-content link as the first focusable element on every page.
4. THE Earth_Whisper application SHALL mark all decorative images and SVG illustrations as `aria-hidden="true"`.
5. THE Earth_Whisper application SHALL provide descriptive `aria-label` attributes on icon-only buttons and navigation triggers.
6. THE Earth_Whisper application SHALL ensure all visible text meets WCAG_AA minimum contrast requirements (4.5:1 for normal text, 3:1 for large text).
7. WHEN the Mobile_Nav is open, THE Earth_Whisper application SHALL trap focus within the Mobile_Nav panel until it is closed.
8. THE Earth_Whisper application SHALL not rely solely on color to convey state information (e.g., active nav state SHALL include a non-color indicator such as a border or font weight change).

---

### Requirement 18: Build Verification

**User Story:** As a developer, I want the application to build without errors after the visual rebuild, so that the codebase is in a deployable state at the end of Prompt 1.

#### Acceptance Criteria

1. WHEN `tsc -b && vite build` is run in the `app/` directory, THE Earth_Whisper application SHALL produce zero TypeScript compiler errors.
2. WHEN `tsc -b && vite build` is run in the `app/` directory, THE Earth_Whisper application SHALL produce zero Vite build errors.
3. WHEN `oxlint` is run in the `app/` directory, THE Earth_Whisper application SHALL produce zero lint errors on all newly created or modified files.
4. THE Earth_Whisper application SHALL successfully resolve all path aliases (e.g., `@/`) in the TypeScript and Vite configurations after the rebuild.
5. THE Earth_Whisper application SHALL not introduce any new peer-dependency warnings or version conflicts in `package.json`.
