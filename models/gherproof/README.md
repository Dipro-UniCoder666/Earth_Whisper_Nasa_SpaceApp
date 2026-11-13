# GherProof model artifacts

No trained GherProof model or pretrained checkpoint is stored here. The local
PyTorch build is CPU-only and the acquired S1GFloods RAR has no event-level
split mapping. Do not add/export a checkpoint until the event split and
evaluation prerequisites in `docs/GHERPROOF_ML_REPORT.md` are satisfied.

The gated Colab baseline notebook is `notebooks/GherProof_Training.ipynb`.
Any future checkpoint must be accompanied by its source commit, model
configuration, package versions, training manifest, event split manifest,
random seed, benchmark metrics, license and SHA-256.
