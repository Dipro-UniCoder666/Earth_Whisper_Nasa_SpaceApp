# Earth Whisper — Scientific Principles

These principles govern every layer of Earth Whisper, from the processing
pipeline to the UI copy to the AI Investigator. They are non-negotiable
design constraints, not aspirational guidelines.

## 1. NISAR detects and characterizes change. It does not, by itself, explain cause.

A coherence-loss signal, a deformation pattern, or any other NISAR-derived
observation tells us *that* something changed and *how strongly*. It does
not tell us *why*. Cause is investigated, not assumed.

## 2. Additional evidence helps investigate — it does not "confirm."

Terrain, precipitation, optical imagery, fire detection, and water extent
are used to see which candidate explanations are *consistent* or
*inconsistent* with what was observed. Evidence narrows the hypothesis
space; it rarely proves a single cause beyond doubt from remote data alone.

## 3. Competing hypotheses, not a single label.

Earth Whisper represents multiple candidate explanations (landslide,
flood, vegetation disturbance, wildfire, human disturbance, subsidence,
seismic deformation, or undetermined) side by side, and states which are
supported, weakened, or not yet assessable — instead of outputting one
confident label.

## 4. Uncertainty is a first-class output, not a footnote.

Every case file must distinguish:
- What is **known** (directly measured).
- What is **uncertain** (plausible but not confirmed).
- What **cannot be concluded** remotely (requires field verification).

## 5. "Undetermined" and "insufficient evidence" are valid, expected answers.

The system must be able to say it doesn't know. A confident-sounding wrong
answer is worse than an honest "insufficient evidence" one.

## 6. The AI layer explains measured evidence. It does not generate evidence.

The language model (e.g. a local Qwen model via Ollama, per the team's
current plan) receives structured, already-computed facts and produces a
human-readable explanation of them. It never invents rainfall values,
terrain values, causes, or confidence scores that were not actually
computed upstream.

## 7. What Earth Whisper must never claim

- "We can predict every disaster."
- "We know the exact cause."
- "Our model guarantees an impending [hazard]."

## 8. What Earth Whisper can claim

- We detect and characterize observed surface changes.
- We compare those observations with relevant environmental evidence.
- We identify explanations that are consistent with the evidence.
- We clearly communicate uncertainty and identify locations for further
  investigation.

## Current prototype status

Candidate #1 (31.1105° N, 77.9373° E) is a **prototype NISAR anomaly**,
not a confirmed event of any kind. Only its measured coherence values
(before ≈0.6648, after ≈0.2188, mean change ≈−0.446, area ≈41.57 km²) are
represented in the app. No cause, rainfall, terrain, or optical evidence
has been fabricated for it — those fields are simply absent until real
evidence collection is implemented.
