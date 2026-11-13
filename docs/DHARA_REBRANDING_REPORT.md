# DHARA Rebranding Report

## Brand

- **Product:** DHARA
- **Tagline:** Seeing Water Changes. Supporting Better Decisions.
- **Description:** Satellite-powered environmental monitoring and decision support.
- **Parent application:** Earth Whisper

DHARA remains a broad environmental monitoring and decision-support product.
Its current demonstration continues to support fisheries and aquaculture
incident screening without limiting the product identity to one profession.

## Application changes

- Updated the shared navigation, mobile navigation, footer navigation and
  route labels to show **DHARA**.
- Added `/dhara` as the canonical feature route. The former `/gherproof` URL
  remains registered as a compatibility alias and displays the DHARA brand.
- Updated the page title and description metadata for both routes. The parent
  Earth Whisper title and metadata remain intact on the home page and other
  routes.
- Replaced the feature landing, investigation results, breadcrumbs,
  accessibility label, loading/service errors and report-dialog branding with
  DHARA.
- Updated the generated Markdown report heading and fisheries case-study title
  to use DHARA. The evidence JSON download now uses `dhara-event-evidence.json`.
- Updated FastAPI documentation tags to DHARA while retaining the existing
  `/api/gherproof` service prefix.
- Updated active root, frontend and backend READMEs to describe DHARA and its
  compatibility paths.

## Compatibility and preserved records

The `/api/gherproof` routes, `/gherproof` alias, source module names, service
identifiers, fisheries environment-variable names, database fields, evidence
IDs, data directories, raster paths, manifests and checksums remain unchanged.
Historical reports and provenance records that identify the original project
name were not rewritten. Sandhya and Monda files/data were not edited, and no
DELTAQ files or outputs were added or restored.

The active frontend source still contains legacy implementation identifiers
such as `GherProofPage`, `GHERPROOF_API` and the `features/gherproof/` directory.
These are internal compatibility names; the active interface and current
generated report use DHARA. Remaining `/gherproof` strings are compatibility
routes/API prefixes or preserved storage and historical provenance paths.

## Verification

| Check | Result | Details |
|---|---|---|
| Frontend production build | **PASS** | `npm run build`; TypeScript and Vite completed, transforming 1,985 modules. Vite retains its existing warning that the minified JavaScript chunk exceeds 500 kB. |
| Fisheries regression tests | **PASS** | All 13 tests in `backend/tests/test_gherproof_fisheries.py` completed successfully, including the updated DHARA report title and evidence error wording. |
| Combined fisheries and raster-preview run | **INCOMPLETE** | The 13 fisheries tests passed; execution then stalled in `tests/test_gherproof_phase9_preview.py` before the preview tests completed. The run was interrupted. A subsequent Python invocation could not start (`MXC launcher: native MXC is unavailable on this Windows build`). No preview-test pass is claimed. |
| User-visible branding scan | **PASS** | Active feature UI, navigation labels, route titles, report heading and API tags no longer display GherProof branding. Remaining source hits are internal compatibility identifiers, route/API paths, historic report names and provenance/storage references. |

No scientific outputs, model results, observations, or provenance were changed
for this rebrand.
