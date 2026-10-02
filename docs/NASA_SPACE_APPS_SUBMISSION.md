# EARTH WHISPER – NASA SPACE APPS CHALLENGE 2026

Submission documentation for the Earth Whisper repository.

---

## 1. Project Overview

**Project:** Earth Whisper
**Tagline:** Where Earth's Changes Tell Their Story
**Team:** Aquabyte
**Challenge:** Dancing with the SARs
**Location:** Barishal, Bangladesh
**License:** Apache License 2.0
**Live demo:** https://earth-whisper.vercel.app/

Earth Whisper is an interactive Earth-observation investigation experience
designed to help users explore where Earth's surface changes, examine
supporting observations, understand uncertainty, and follow evidence rather
than simply receiving a single unexplained satellite signal.

The core idea is simple: instead of only showing a satellite image, Earth
Whisper helps turn Earth-observation signals into an understandable
investigation. A radar signal is presented together with the evidence around
it, the limitations that apply to it, and the provenance that explains where
it came from.

The project is designed around:

- **Observation** - measured Earth-observation signals, primarily NASA-ISRO
  NISAR radar coherence.
- **Investigation** - a structured workflow that examines those signals in
  context rather than in isolation.
- **Supporting evidence** - independent and contextual information that helps
  narrow the space of possible explanations.
- **Uncertainty** - what is known, what is uncertain, and what cannot be
  concluded remotely.
- **Provenance** - which dataset, method, and processing step produced each
  recorded value.
- **Communication** - presenting all of the above in a form non-specialists
  can follow.

The repository does not claim a confirmed physical cause for any observed
change. Detailed scientific methodology and dataset documentation are in
`docs/SCIENTIFIC_DATA_AND_METHODOLOGY.md`.

---

## 2. The Why, The What, The How

### The Why

Surface changes can be difficult to understand from ground observation alone.
Earth-observation data provides another perspective on the same places, but
raw satellite imagery and radar measurements are not self-explanatory: a
single radar signal does not automatically explain the physical cause of a
change. Users need a way to explore the change and the surrounding evidence
together, and to see what remains unknown.

### The What

Earth Whisper provides:

- an interactive investigation experience rather than a static image viewer;
- location-based investigation entry points;
- radar-based Earth observation as the primary signal;
- supporting and independent evidence alongside the primary observation;
- exploration of anomaly/candidate regions and their statistics;
- explicit uncertainty for every recorded value;
- provenance for the data behind each result;
- an **Event Case File** that packages observations, evidence, uncertainty,
  sources, and limitations together.

### The How (concept level)

```
User selects a location
  -> Earth Whisper investigates
  -> Earth-observation observations are examined
  -> changes are identified
  -> supporting / contextual evidence is considered
  -> anomaly / candidate analysis helps prioritize investigation
  -> uncertainty and provenance are retained
  -> results are presented
  -> an Event Case File can be generated
```

This section is deliberately conceptual. The detailed scientific workflow,
processing steps, dataset roles, and statistical methods are documented once,
in `docs/SCIENTIFIC_DATA_AND_METHODOLOGY.md`, and are not duplicated here.

---

## 3. Project Development Journey

Earth Whisper was developed iteratively by Team Aquabyte during the NASA Space
Apps Challenge 2026. The work progressed in roughly this order:

1. **Challenge selection and problem framing** - choosing *Dancing with the
   SARs* and framing the problem around understanding Earth-observation
   change rather than merely displaying satellite imagery.
2. **Earth Whisper concept development** - defining the investigation
   experience: observation, evidence, uncertainty, provenance, and
   communication as first-class parts of the product.
3. **Designing the scientific investigation workflow** - specifying the
   pipeline from NISAR radar observations through coherence change, candidate
   regions, cross-checks, context, and uncertainty.
4. **Exploring and processing Earth-observation data** - working with NISAR
   GUNW products, Sentinel-1 backscatter, NASADEM terrain data, GPM IMERG
   rainfall, and an optical verification attempt.
5. **Building candidate/change detection and evidence workflows** - candidate
   region extraction, region statistics, temporal fingerprints, feature
   tables, and anomaly prioritization.
6. **Developing the frontend investigation experience** - the landing
   experience, investigation flow, map-based context, and evidence
   presentation.
7. **Developing the backend/API layer** - a read-only service that serves the
   verified candidate contract and case-file artifacts.
8. **Building the Event Case File workflow** - structured, traceable
   case-file outputs (machine-readable and PDF).
9. **Testing and debugging** - iterative verification of builds, data
   contracts, and backend behaviour, including unit tests for the live
   metadata service.
10. **Integrating scientific results into the application** - delivering the
    verified artifacts into the investigation interface.
11. **Preparing the final presentation and video** - narration, visual assets,
    and the submission materials.

**Direction and authorship.** The project concept was developed by Team
Aquabyte. The overall system architecture was planned by the team. The
frontend/backend structure and feature requirements were planned by the team.
The scientific workflow and implementation direction were determined by the
team. AI tools were used as implementation/development assistants rather than
as the source of the project's core architectural decisions.

**Working environment.** Development took place in an Ubuntu/Linux terminal
environment with QGIS and GDAL for geospatial work, Python for scientific
processing, a frontend/backend development environment for the application,
iterative testing and debugging throughout, and a Git/GitHub workflow for
version control and publishing.

---

## 4. Team & Responsibilities

| Member | Role |
|---|---|
| **Dipro Das** | Team Leader & Full-Stack Developer |
| **Shakil Ahmed** | QA Lead & Data Coordinator |
| **Devjyoti Dey Mugdho** | Earth Science & Geospatial Research Contributor |
| **Jerin Tasnim** | Media & Communications Lead |

Responsibilities are stated at project level: Dipro Das led the team and the
full-stack development work; Shakil Ahmed led quality assurance and data
coordination; Devjyoti Dey Mugdho contributed Earth science and geospatial
research; Jerin Tasnim led media and communications.

---

## 5. Community Relevance & Potential Impact

Earth Whisper is intended to make Earth-observation information more
understandable and more inspectable:

- **Public understanding of remote sensing** - presenting radar observations
  together with plain-language context, provenance, and uncertainty.
- **Learning and exploration** - supporting students, educators, and
  interested users in exploring evidence-based investigation workflows.
- **Environmental and geospatial investigation** - demonstrating how
  multi-source evidence and explicit uncertainty can be organized into a
  traceable case file.
- **Extension beyond the initial study areas** - the workflow is structured
  around locations and datasets rather than hard-coded conclusions, so it can
  be extended as new verified investigations are added.
- **Educational / exploratory decision support** - a possible interface for
  exploring where change was observed and where further investigation may be
  warranted.

Earth Whisper is **not** an operational emergency response system, is **not**
a disaster confirmation system, is **not** a guaranteed event detector, is
**not** a medical or health system, and is **not** a replacement for
professional field verification. No measured real-world outcomes or impact
statistics are claimed.

---

## 6. Media & Demo Links

### 240-Second Prescreening Video

https://www.youtube.com/watch?v=mgyILV_3OjE

### 30-Second Final Demo Video

TO BE ADDED – 30-second final demo YouTube URL

### Application

Live demo: https://earth-whisper.vercel.app/

---

## 7. Visual Assets & Presentation

Visual material used by the project, based on assets present in the
repository:

| Category | Assets |
|---|---|
| Brand and identity | Earth Whisper logo marks (`Logo.svg`, `LOGO_EW.svg`) |
| Landing and hero artwork | `Hero.svg` (desktop), `Hero_Mobile.svg` (portrait/mobile), `Other_Page.svg` (secondary pages), `sattelite.png` |
| Team imagery | Team member photographs used on the About/team presentation |
| Application interface visuals | The running interface itself: the investigation flow, the Leaflet/OpenStreetMap map views, and the evidence presentation screens |
| Scientific visualizations | The NISAR coherence-change maps listed in the Step 11 figure manifest (`HH_023_to_029_coherence_change.png`, `VV_025_to_026_coherence_change.png`) |
| Case-file figures | Figures embedded in the generated event case-file PDF, indexed by `data/step11_event_case_file/figure_manifest.json` |
| Presentation / video visuals | Narration script, scene plan, and the assembled presentation video (see sections 8-13) |
| Keyframe video asset | `Video.mp4` used in the Earth-signal section of the landing experience |

No design-platform claim is made: there is no repository evidence that Figma
or another design tool was used, so none is asserted here.

---

## 8. AI USE & TRANSPARENCY

### 8.1 Project Design & Technical Direction

The core Earth Whisper project concept, overall system architecture,
frontend/backend planning, feature requirements, scientific workflow,
investigation structure, and implementation direction were designed and
decided by Team Aquabyte. AI tools were used primarily as development
assistants during implementation.

### 8.2 AI-Assisted Software Development

| Tool | Use |
|---|---|
| **Autoclaw** | Used as a coding/development assistant for implementation-level coding tasks, syntax assistance, debugging, and structured technical work. |
| **ChatGPT Codex** | Used as a coding/development assistant for writing and refining code, syntax checking, debugging, and implementation support based on team-defined requirements. |
| **Kiro** | Used as a coding/development assistant for implementation support, syntax/error checking, and structuring technical development work. |

These tools assisted with code implementation, syntax/error checking,
debugging, and structured technical documentation based on requirements
defined and reviewed by our team. They are not described here as having
designed the scientific idea or independently created the project
architecture.

### 8.3 ChatGPT for Research / Documentation / Prompt Structuring

ChatGPT was also used for:

- structuring and refining technical and scientific documentation;
- helping interpret technical documentation;
- troubleshooting and reasoning support;
- structuring detailed visual-generation prompts;
- organizing project explanations and reports.

ChatGPT was not the source of the project's satellite measurements.

### 8.4 Google Gemini - AI-Generated Video Clips

Google Gemini was used to generate selected cinematic 2D animated visual clips
using structured prompts. The final video was **not** generated automatically
as one complete AI-generated video. The team manually:

- selected clips
- reviewed outputs
- trimmed clips
- arranged scenes
- timed scenes with narration
- added transitions
- composited visuals
- added subtitles
- synchronized audio
- placed background music
- completed the final presentation/edit

> The final video was manually assembled and edited by Team Aquabyte.

---

## 9. Example AI Video Prompt

**Representative example of a structured AI video-generation prompt used
during production.**

> "Create a 10-second cinematic 2D animated movie scene set in rural
> Bangladesh beside the Sandhya River near Babuganj, Barishal. Use a
> hand-drawn 2D animated feature-film style with lush vegetation, a broad
> natural river, painterly backgrounds, cinematic camera movement, layered
> depth, natural character motion, and a calm Barishal atmosphere.
>
> Main character: an 11-12-year-old Bangladeshi boy named Rafi, with
> consistent appearance, clothing, hairstyle, and proportions across scenes.
>
> Begin with a high overhead cinematic view of the river and surrounding
> landscape, transition to a wide shot of Rafi walking beside the river, and
> finish with a medium-wide tracking shot showing the familiar riverbank and
> environment.
>
> The scene should feel like a continuous animated film sequence rather than a
> presentation, slideshow, game, or advertisement.
>
> Strictly no text, subtitles, captions, labels, logos, watermarks, UI, or
> graphic overlays."

This is one representative example of the structured prompts used during
production; it does not represent every generated clip.

---

## 10. Manual Creative Contribution

After AI-assisted generation, the following work was carried out manually by
the team:

- creative concept development
- visual direction
- prompt decisions
- clip selection
- clip review
- timing
- scene arrangement
- transitions
- visual compositing
- subtitles
- narration synchronization
- background music integration
- audio mixing
- final pacing
- final editing
- final presentation

AI-generated clips were individual assets. The final video was manually
constructed by the team.

---

## 11. Voice & Narration Credits

**Voice Recording Tools**

- Audacity
- MOTIV Audio

**Voices**

- Jerin Tasnim
- Dipro Das

No additional voice contributors are documented.

---

## 12. Background Music Credits

Background music sources used for the final video:

### Music for Video Library

https://youtu.be/HhXJ4Nabki8?si=OPdkv3dpjR4MscQr

### Pro Tunes - Copyright Safe Music

https://youtu.be/I34bTKW8ud0?si=q13kuGN34mtDmfuQ

These were used as background music sources and were manually incorporated
into the final video. No additional legal or copyright claims are made beyond
what is documented here.

---

## 13. Video Production

**Video editing:** KineMaster

Production work included:

- manual clip assembly
- timing
- transitions
- subtitles
- visual compositing
- background music placement
- narration synchronization
- final audio/visual editing

---

## 14. Third-Party / External Assets & Credits

The following third-party technologies and assets are present in the
repository and are credited to their respective owners. No ownership is
claimed over third-party material.

| Category | Item | Role |
|---|---|---|
| Maps | OpenStreetMap contributors (https://www.openstreetmap.org/copyright) | Map tiles and geocoding source for the application map |
| Mapping library | Leaflet / React-Leaflet | Interactive map rendering in the application |
| Frontend libraries | React, React Router, Lucide icons, Tailwind CSS, Vite, TypeScript | User interface, routing, iconography, styling, build tooling |
| Backend | FastAPI, Uvicorn | Read-only data and case-file API |
| Scientific software | QGIS, GDAL (Python `osgeo`) | Geospatial workspace and raster I/O for the scientific workflow |
| Scientific libraries | Python, NumPy, pandas | Processing, statistics, feature tables, anomaly analysis |
| Optical attempt libraries | earthaccess, rasterio, pyproj | Optical verification attempt and coordinate handling |
| NASA / space-agency sources | NASA-ISRO NISAR (GUNW), NASA Earthdata / ASF, NASA GPM IMERG, NASA HLS | Earth-observation datasets used by the documented workflow |
| Third-party music | Music for Video Library; Pro Tunes | Background music sources for the final video (see section 12) |
| AI-generated visual assets | Google Gemini-generated cinematic clips | Selected communication assets for the final video (see sections 8.4 and 10) |

Detailed dataset roles, processing steps, and citations are documented in
`docs/SCIENTIFIC_DATA_AND_METHODOLOGY.md`.

---

## 15. Scientific & AI Transparency Boundary

Earth Whisper keeps three distinct things separate:

**Scientific evidence** - generated and processed from the project's
documented Earth-observation and geospatial workflow. The application serves
these as verified, precomputed artifacts (with a static fallback), and the
repository's live NASA Earthdata CMR usage is metadata discovery only.

**AI-assisted development** - AI tools were used to assist coding,
syntax/error checking, debugging, and structured documentation, based on
requirements defined and reviewed by the team.

**AI-generated presentation visuals** - selected cinematic clips generated for
communication purposes and manually assembled into the final video.

AI-generated presentation visuals are **not** the source of the scientific
measurements. The project does **not** use a runtime LLM to generate the
scientific measurements or to replace the documented scientific processing.

---

## 16. Submission Checklist

- [x] Public GitHub repository - `Dipro-UniCoder666/Earth_Whisper_Nasa_SpaceApp`
- [x] Open-source license - Apache License 2.0 (`LICENSE`)
- [x] Source code included - frontend, backend, scientific scripts, and generated artifacts
- [x] Setup / installation instructions - `README.md` ("Running the Application")
- [x] Project description - `README.md`
- [x] Team Journey - section 3 of this document
- [x] Community / Impact - section 5 of this document
- [x] 240-second prescreening video - https://www.youtube.com/watch?v=mgyILV_3OjE
- [x] Visual assets - brand, hero, team imagery, and scientific figures committed; interface visuals are captured from the running application
- [x] Architecture documentation - `README.md` and `docs/architecture/overview.md`
- [x] NASA dataset documentation - `docs/SCIENTIFIC_DATA_AND_METHODOLOGY.md` (section 3)
- [x] References / citations - `data/step11_event_case_file/sources.txt` and `docs/SCIENTIFIC_DATA_AND_METHODOLOGY.md` (section 10)
- [x] AI disclosure - section 8 of this document
- [x] AI tools listed - section 8.2 of this document
- [x] Example AI prompt - section 9 of this document
- [x] Manual creative contribution documented - section 10 of this document
- [x] Third-party / media credits - sections 11, 12, 13, and 14 of this document

---

## 17. Final Submission Summary

Earth Whisper combines Earth observation, scientific processing, evidence
exploration, explicit uncertainty, and provenance inside an interactive
investigation experience. The project was developed through human-directed
technical work by Team Aquabyte, with transparent AI-assisted implementation
and media production: AI tools assisted with coding, debugging, documentation,
and selected presentation visuals, while the project concept, architecture,
scientific workflow, investigation structure, and final video editing
decisions remained with the team. Earth Whisper reports what was observed,
what supports or complicates it, what remains unknown, and where further
investigation should focus - and it does not claim a confirmed physical cause
that the underlying evidence does not establish.
