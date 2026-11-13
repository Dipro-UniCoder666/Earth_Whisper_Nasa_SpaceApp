# GherProof scripts

- `recover_event_imagery.py` authenticates to CDSE locally, resumes and verifies
  the four same-orbit January COGs; see `docs/GHERPROOF_CDSE_SETUP.md`.
- `verify_event_imagery.py` reads real local rasters and reports actual scene
  metadata/coverage. Missing assets remain explicitly unverified.
- `train_pretrained_sen1floods11.py` runs the distinct pretrained-encoder
  fine-tuning experiment on the frozen event split;
  `evaluate_pretrained_model.py` reports comparison metrics and hashes.
- `train_sen1floods11.py` and `evaluate_sen1floods11_checkpoint.py` reproduce
  the scratch benchmark baseline and independent evaluation.

- `query_event_scenes.py` queries the Copernicus STAC API for the January
  2026 provisional locality window and saves catalogue metadata. It does not
  download/process scene pixels or infer flooding.
- `download_public_data.py` downloads the S1GFloods archive with resume support
  and exact size/SHA-256 checks.
- `download_clark_bangladesh.py` downloads the Clark Bangladesh archive with
  resume support and exact size/SHA-256 checks.

The Clark Bangladesh archive includes official source legend metadata and is
documented in `data/gherproof/manifests/public_dataset_audit.json`. It is not
redistributed from the app.
