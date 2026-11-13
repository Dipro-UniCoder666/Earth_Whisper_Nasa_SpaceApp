# GherProof Frontend Correction Report

## Result

GherProof is now integrated into Earth Whisper's existing application shell at `/gherproof`. The route is nested under `AppLayout`, so it uses the shared `WhisperNav`, Earth Whisper background atmosphere, standard content layout and footer. The root landing page and existing investigation/science/about routes were not intentionally changed. The separate GherProof home shell was removed.

## User flow and evidence display

The page follows the requested compact flow: short introduction with a real Sentinel-2 context image, one selectable January 2026 regional screening card, then an Analyze Now action that loads prepared evidence. The results view has three distinct modes (satellite imagery, optical comparison and AI screening), a registered layer selector, opacity control, raster metadata/limitations, an eight-line summary, expandable methodology and an evidence-preview strip. Query-string stages preserve browser back/refresh behavior.

The result loader requests existing GherProof API products and displays partial-load failures. It does not perform model inference or training. The map uses the registered provisional regional extent and explicitly labels it as non-authoritative. Satellite/optical layers, scratch/pretrained predictions and disagreement products remain separate. Optical weak-reference candidate counts appear only in expandable details, with pixel resolution and a clear note that these are not verified water or area.

The Sentinel-2 previews use registered Jan 10/20 B08 evidence IDs to render the saved Phase 7C B08/B04/B03 false-colour composites with their documented 0–0.4 reflectance display stretch. The rendering endpoint validates the date/evidence ID pair. The preview is imagery, not a water classification.

## Files changed

- `app/src/router.tsx`: nested GherProof under the existing `AppLayout`.
- `app/src/features/gherproof/GherProofPage.tsx`: compact intro, single investigation selection, prepared-evidence loading and result routing.
- `app/src/features/gherproof/GherProofWorkspace.tsx`: evidence-aware map, summary, layer controls, previews and methodology details.
- `app/src/features/gherproof/GherProofMap.tsx`: bounded map overlays and support for registered RGB previews.
- `app/src/features/gherproof/gherproof.css`: integrated responsive styling using Earth Whisper's darker/teal visual language.
- `backend/app/api/gherproof.py`: RGB preview support for the two registered Sentinel-2 composites; ASCII-safe response header.
- `backend/tests/test_gherproof_phase9_preview.py`: added the Sentinel-2 RGB preview regression test.
- `docs/GHERPROOF_FRONTEND_INTEGRATION_CONTRACT.md`: replaced the prior standalone-shell description with the integrated route and actual evidence semantics.

## Verification

- `npm run build` in `app/`: passed (TypeScript and Vite production build). Vite reports the existing bundle-size advisory for a JS chunk over 500 kB.
- Python `py_compile` for the preview API and focused test module: passed.
- Direct backend invocation for the Jan 10 registered RGB preview: produced a `StreamingResponse` with `image/png`, evidence ID `s2-2026-01-10-B08`, and ASCII-safe display metadata. It selected the actual Phase 7C composite file.
- Focused pytest run `python -m pytest tests/test_gherproof_phase9_preview.py -q`: did not complete or emit test output after 30 seconds; interrupted. A direct `TestClient` request also stalled during application startup in this environment. Therefore the new regression test is added but not reported as passed.
- Browser screenshot QA could not be completed: the CUA browser surface reports local browser access unavailable, even though the Vite server started. No screenshot artifact is claimed.

## Limits

The UI reflects current registry and manifest contents. It does not establish that the reported incident occurred at a particular enclosure, produce verified flood extent, calculate impacts, or establish local model accuracy. The only geographic outline in this flow is a provisional regional search extent. Human reference labels and an exact Pallimangal boundary remain unavailable, as stated by the existing evidence records.
