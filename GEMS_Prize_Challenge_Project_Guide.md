# GEMS Prize Challenge — Verified Project Brief, Build Plan, and Agent Handoff Guide

**Project:** Geologic Enhanced Mapping System (GEMS) Prize Challenge  
**Verified on:** 13 September 2026  
**Document status:** Working project charter and technical plan  
**Primary purpose:** Give a new agent or collaborator enough context to continue the project without relying on earlier chat history

> **Important:** Competition dates, rules, forum clarifications, and data files can change. Any agent beginning a new session must first re-check the official competition homepage, problem description, rules, and forum. This document records what was verified on 13 September 2026; it is not a substitute for the official rules.

---

## 0. How an agent should use this document

Read this document in order at least once. It starts with a non-technical explanation and gradually introduces the technical details.

Throughout the document, statements are classified as follows:

- **Confirmed fact:** Explicitly stated in an official competition, DOE/NLR, USGS, or official reference-solution source.
- **Derived fact:** Calculated or directly inferred from confirmed metadata, such as the physical size of a 128-pixel tile at 100 m resolution.
- **Working hypothesis:** A proposed solution idea that must be tested experimentally.
- **Open question:** Public documentation does not answer it clearly enough; do not guess.

Every future agent must follow these rules:

1. Separate confirmed facts from hypotheses and assumptions.
2. Prefer primary sources: official competition pages, official rules, official code, USGS data releases, and original research papers.
3. Record the source and access date for any fact that can change.
4. Do not optimize around the public leaderboard before establishing trustworthy local spatial validation.
5. Do not describe an algorithmic lineament as a newly discovered fault unless a qualified geologist has reviewed it.
6. Do not use an external dataset until its license and sponsor-sharing permissions have been recorded.
7. Preserve geospatial metadata exactly when producing submissions.
8. Keep an auditable log of how generative AI is used because the official rules require disclosure.

---

# Part I — Beginner-friendly explanation

## 1. What is this competition about?

In plain language, the competition gives us a very large map of part of Nevada and eastern California. Instead of showing only a normal photograph, the map contains many different measurements of the land and subsurface. Our job is to build a computer system that estimates where geological faults are located, including faults that may not yet appear in the public fault map.

A compact description is:

> **Input:** Several aligned maps describing terrain, magnetism, gravity, deformation, conductivity, and earthquakes.  
> **Output:** One map showing, for every 100 m by 100 m location, how confident we are that a fault is present.

The competition is **not directly asking us to predict a geothermal power plant location, reservoir temperature, commercial viability, or electricity output**. It asks us to map faults because faults are geologically relevant to geothermal and mineral exploration. Faults and fractures may provide pathways for hot fluids, although in real geology some faults can also restrict fluid flow. The machine-learning target is fault presence, not a complete geothermal-resource assessment.

Official task description: [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)

---

## 2. What is a geological fault?

A geological fault is a fracture or discontinuity in the Earth's crust across which rock has moved. The underground surface along which movement occurs is the **fault plane**. Where that plane reaches the ground surface is the **fault trace**. A collection of nearby related fractures is a **fault zone**.

A fault can sometimes be visible through:

- a sharp step in the terrain, called a fault scarp;
- a straight valley or ridge;
- displaced rock layers;
- aligned springs or earthquake activity;
- abrupt changes in rock density, magnetism, or electrical properties.

Many faults are subtle, eroded, covered by sediment, or buried. That is why geologists combine terrain, remote-sensing, seismic, magnetic, gravity, electrical, and deformation information rather than relying on a photograph alone.

The official competition background provides the same high-level explanation: [DrivenData “About” page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)

---

## 3. Why do faults matter for geothermal exploration?

The Earth becomes hotter with depth. A useful geothermal system usually requires a combination of heat, fluids, and pathways through which those fluids can circulate. Fractures and some faults can provide such pathways, so identifying structural geology helps exploration teams decide where further investigation may be worthwhile.

This relationship is not one-to-one:

- A mapped fault does not prove that a commercially useful geothermal resource exists.
- A fault may conduct fluids, seal fluids, or behave differently along different segments.
- Temperature, permeability, fluid availability, depth, chemistry, and economics still matter.

Therefore, our output should be interpreted as an **enhanced fault probability map**, not a geothermal prospect map.

---

## 4. What does the input look like?

Imagine laying several transparent maps on top of one another:

1. a map of elevation;
2. a map of steepness;
3. a map of magnetic measurements;
4. a map of gravity measurements;
5. a map of crustal deformation;
6. a map related to underground electrical conductivity;
7. a map of earthquake-related information;
8. several derived maps showing how quickly those values change from place to place.

All the layers are aligned to the same geography. In machine-learning language, this resembles a multi-channel image. A normal color image has red, green, and blue channels. The competition's main numerical raster has 19 geoscience channels.

The organizer's reference notebook reports a shape of:

```text
3,730 rows × 3,292 columns × 19 feature channels
```

That is **12,279,160 grid cells** in the rectangular raster envelope. Each cell is 100 m by 100 m. Some cells are no-data cells outside the valid survey footprint, so the rectangular envelope should not be confused with the true surveyed area.

Source for dimensions and band metadata: [official reference notebook](https://raw.githubusercontent.com/drivendataorg/gems-prize-reference-solution/main/unet-mc-cv-reference-solution.ipynb)

---

## 5. What does the output look like?

We submit a single georeferenced image, called a **GeoTIFF**. Each valid 100 m pixel must contain a 32-bit floating-point number from 0 to 1:

```text
0.00  = essentially no confidence that a fault is present
0.25  = weak evidence
0.60  = plausible evidence
0.90  = strong evidence
1.00  = maximum confidence
```

The result is a probability or confidence heatmap, not merely a list of coordinates and not necessarily a hard yes/no mask.

Official submission requirements:

- one raster layer;
- `float32` values between 0 and 1;
- EPSG:32611, which is UTM Zone 11N;
- 100 m resolution;
- the same bounds as the training raster;
- null/NaN outside the valid bounds;
- predictions for all faults across the region.

Source: [DrivenData problem description — submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)

---

## 6. Why is this not a normal supervised-learning problem?

The public fault map is known to be incomplete and may contain inaccuracies. Therefore:

```text
Mapped fault pixel     → reasonably strong positive evidence
Unmapped pixel         → may be ordinary ground OR an undiscovered/unmapped fault
```

A naive model treats every unlabelled pixel as a confirmed negative. That can teach it to suppress exactly the hidden faults the challenge wants us to find.

This is related to:

- **positive-unlabelled learning:** positives are known, negatives are not fully known;
- **weak supervision:** labels are imperfect approximations of reality;
- **noisy-label learning:** some labels can be wrong or spatially misaligned;
- **semi-supervised learning:** unlabelled areas may contain useful structure.

These terms are useful later, but the main idea is simple: **absence from the current map does not prove absence in the ground.**

---

# Part II — Verified competition brief

## 7. Current competition snapshot

The following was verified on 13 September 2026.

| Item | Verified information |
|---|---|
| Competition | The Geologic Enhanced Mapping System (GEMS) Prize Challenge |
| Platform | DrivenData |
| Sponsor | U.S. Department of Energy Office of Geothermal |
| Additional support / administrator | National Lab of the Rockies (NLR) |
| Current website deadline | **3 December 2026, 11:59 p.m. UTC** |
| Total prize pool | **$300,000** |
| Initial Prize Round | $50,000; top five receive $10,000 each |
| Final Prize Round | $250,000; $100k, $70k, $40k, $25k, and $15k |
| Submission frequency | Up to three scored submissions per week |
| Final selection | One submission must be selected for both prize rounds |
| Main output | One full-region, one-band, 100 m, float32 GeoTIFF of fault probabilities |
| Main metric | Distance-weighted Tversky index |
| Generative AI | Allowed, but its use must be disclosed |
| Finalist obligation | Complete code, documentation, resource requirements, and reproducibility on new data |

Primary sources:

- [Competition homepage](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

### 7.1 A deadline discrepancy that requires clarification

The current DrivenData homepage says **3 December 2026 at 11:59 p.m. UTC**. However, Appendix A of the official rules says final content must be uploaded by **5:00 p.m. ET on the deadline date**. Those are not the same cutoff.

The rules also say that the competition website should be consulted for the most current timeline. Nevertheless, because missing the legal deadline would be catastrophic, we should:

1. ask the organizers which cutoff controls;
2. plan against the earlier cutoff until they answer;
3. set an internal submission freeze no later than **1 December 2026**.

This is an **open question**, not something an agent should silently resolve by assumption.

---

## 8. Eligibility is a Phase 0 gate

The official rules state:

- An individual competitor must be a U.S. citizen or permanent resident.
- A team may win if its designated captain is a U.S. citizen or permanent resident.
- Other individual team members must be legally authorized to work in the United States.
- Private entities must be incorporated in the United States and maintain their primary place of business there.
- Academic institutions must be U.S.-based and appropriately accredited.
- Federal entities and federal employees are generally ineligible, with additional detailed restrictions in the rules.

Do not infer eligibility from a person's current country, nationality, employer, visa, or work location. If any part is uncertain, obtain a written clarification from the organizers before treating the project as prize-eligible.

The competition homepage directs rule questions to the forum or to `gemsprize@nlr.gov`.

This document is not legal advice. The [official rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf) control.

---

## 9. The unusual two-round evaluation structure

The challenge was designed around incomplete ground truth.

### 9.1 Initial Prize Round

Experts identified new faults that are not in the current public USGS fault database. These expert-labelled new faults are divided into public and private evaluation data. During the competition, public performance is shown on the leaderboard. At the deadline, the selected final submission is evaluated on the private set.

### 9.2 Expert review

After the Initial Prize Round, experts review the submitted predictions to identify plausible faults that were missing even from their initial expert labels.

### 9.3 Final Prize Round

Experts update the label set with verified additions. The **same already-selected submission** is then scored again against the expanded labels.

This structure rewards a solution that maps geologically credible faults rather than merely reproducing known public labels. It also means the final ground truth partly evolves after seeing competitors' predictions.

Source: [competition structure](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)

---

## 10. A critical scoring ambiguity

The documentation says all of the following:

- the public known-fault labels may be used for training;
- initial evaluation labels are newly identified faults absent from the public USGS database;
- the submission should predict **all faults** across the region.

What is not yet explicit in the public documentation is how predictions over supplied known-fault locations are treated during initial scoring. Possibilities include:

1. known faults are also positive in the scoring target;
2. known-fault areas are masked or ignored;
3. the scoring target contains only new faults, in which case known-fault predictions could otherwise look like false positives unless special masking is applied.

This distinction can radically change the optimal output. We must ask the organizers and must not mask, erase, or boost known faults based on an unverified assumption.

At the time of verification, the public competition forum contained no substantive clarification threads beyond the category introduction: [GEMS Prize forum](https://community.drivendata.org/c/gems-prize-challenge/111)

---

# Part III — Data and geospatial contract

## 11. Study region and GeoDAWN background

GeoDAWN means **Geoscience Data Acquisition for Western Nevada**. The source USGS survey covers northern and western Nevada and adjacent eastern California, including parts of the Walker Lane and western Great Basin.

The USGS reports that the combined source survey consists of approximately:

- **51,857 square kilometres**;
- **149,030 line-kilometres** of airborne acquisition;
- four acquisition blocks: Winnemucca, Fallon, Hawthorne, and Tonopah.

The raw GeoDAWN program acquired high-resolution airborne magnetic and radiometric data, coordinated with lidar/topographic collection. The challenge feature stack also incorporates other public geospatial variables.

Source: [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)

### Important distinction

The raw GeoDAWN source includes magnetic and radiometric products. The 19 bands printed by the official reference notebook do **not** obviously include a radiometric band by name. Do not assume that every raw GeoDAWN variable is contained in the provided 19-band competition raster. Inspect the downloaded GeoTIFF metadata.

---

## 12. Main 100 m numerical feature raster

The official problem page calls the file `training_features.tif`. The official reference notebook currently reads `data/numeric_features.tif`. This naming discrepancy must be reconciled after downloading the actual data; code should not hardcode a filename until the inventory step is complete.

The reference notebook reports:

- width: 3,292 pixels;
- height: 3,730 pixels;
- resolution: 100 m × 100 m;
- CRS: EPSG:32611;
- data type: float32;
- 19 bands;
- shape after loading: `(3730, 3292, 19)`.

At four bytes per float, 19 uncompressed channels contain roughly **0.93 GB of numerical values** before masks, tensors, duplicated arrays, or training patches are created. Actual memory use during modelling will be much higher.

Source: [official reference notebook](https://raw.githubusercontent.com/drivendataorg/gems-prize-reference-solution/main/unet-mc-cv-reference-solution.ipynb)

---

## 13. The 19 bands in the official reference notebook

The table below reproduces the notebook's band metadata in simpler language. The exact downloaded raster metadata remains the source of truth.

| Band | Notebook description | Beginner interpretation | Why it might help with faults |
|---:|---|---|---|
| 1 | Magnetic anomaly | Difference from an expected regional magnetic field | Faults and displaced rock bodies can create magnetic boundaries |
| 2 | Reduced-to-pole magnetic data | Magnetic anomaly transformed to make sources easier to locate | Can align magnetic responses more closely with their geological source |
| 3 | Total magnetic intensity horizontal gradient | How quickly magnetic intensity changes sideways | Strong horizontal changes can mark edges or contacts |
| 4 | Geodetic second invariant | Overall magnitude of the strain-rate tensor | Highlights areas of stronger crustal deformation |
| 5 | Isostatic gravity anomaly slope | Spatial change in topography-corrected gravity | May show density boundaries related to structures |
| 6 | Tilt angle or total curvature | Magnetic derivative used for edge detection | Designed to emphasize linear or boundary-like magnetic features |
| 7 | Geodetic shear rate | Rate of angular deformation | Active structures may influence shear patterns |
| 8 | Geodetic dilatation rate | Rate of expansion or contraction | Can reveal regional tectonic deformation |
| 9 | Total magnetic intensity vertical gradient | Vertical-rate derivative of magnetic intensity | Often emphasizes shallower magnetic sources and edges |
| 10 | Distance to earthquake, with stated neighbourhood/orientation parameters | Engineered seismic-proximity feature | Fault activity can be associated with earthquake patterns |
| 11 | Isostatic gravity anomaly vertical gradient | Vertical derivative of corrected gravity | Can sharpen density contrasts and structural edges |
| 12 | Detrended elevation | Terrain after large regional trend is removed | Makes local landform breaks easier to see |
| 13 | Isostatic gravity anomaly | Gravity after accounting for topographic/isostatic effects | Reflects subsurface density variation |
| 14 | Total magnetic intensity | Strength of the measured magnetic field | Different rocks and structural offsets produce magnetic patterns |
| 15 | Depth to basement surface | Estimated thickness of overlying sediment to deeper basement | Fault-bounded basins and structural relief can alter basement depth |
| 16 | Earthquake intensity or density | Engineered concentration of seismic activity | Active or recently active structures may concentrate earthquakes |
| 17 | Conductivity surface | Estimated subsurface electrical conductivity | Fluids, clay, alteration, and lithology affect conductivity |
| 18 | Isostatic gravity anomaly horizontal gradient | Sideways change in corrected gravity | Can delineate density boundaries |
| 19 | Detrended elevation slope | Local steepness after regional topographic trend removal | Fault scarps and linear breaks may appear as slope anomalies |

### Metadata discrepancy to resolve

The official problem page describes “surface conductivity and depth to conductive base surface” and a “top-of-crustal magnetic source depth estimate.” The notebook prints “depth to basement surface” for Band 15 and does not name a separate top-of-crust magnetic-depth band. This could be a wording difference, metadata change, or file-version issue.

**Required action after download:** export the actual per-band tags from the supplied GeoTIFF and create a versioned `data_dictionary.md`. Do not rely solely on the table above.

---

## 14. High-resolution 1 m DEM data

The competition provides `1m_DEM_links.csv`, containing links or instructions for 1 m digital elevation model data.

A 1 m DEM has 10,000 one-metre cells inside one 100 m × 100 m competition pixel. Feeding the whole 1 m region directly into one model would be computationally expensive. More practical approaches include:

1. derive terrain statistics within each 100 m cell;
2. create multi-scale features from 1 m, 5 m, 10 m, 25 m, and 100 m terrain;
3. train a separate high-resolution terrain model on selected patches;
4. aggregate its predictions or embeddings onto the 100 m output grid;
5. fuse terrain evidence with the 100 m geophysical model.

Potential derived terrain features include:

- slope and aspect;
- profile and plan curvature;
- local relief;
- topographic position index;
- roughness and openness;
- multi-directional hillshade;
- edge and lineament density;
- dominant edge orientation;
- drainage/canyon indicators;
- elevation percentiles within a 100 m cell;
- difference-of-Gaussians or multi-scale residual relief.

These are **working hypotheses**, not guaranteed improvements. Fine terrain also contains streams, roads, shorelines, and canyon walls that can look fault-like.

---

## 15. Labels

The official sources say the training labels come from USGS Quaternary fault mapping and the INGENIOUS Great Basin regional compilation. Labels are available in vector and raster form, with the raster aligned to the 100 m feature grid.

We should preserve both representations:

- **Raster labels** are convenient for segmentation training.
- **Vector fault traces** are valuable for grouping faults, orientation analysis, distance calculations, spatial splitting, and topology-aware evaluation.

The label audit must inspect:

- source field and source date, if present;
- fault age or confidence attributes, if present;
- duplicate or overlapping traces;
- rasterization rules and line width;
- invalid geometries;
- traces crossing the data boundary;
- differences between the vector and raster versions;
- disconnected components and very short fragments;
- spatial offsets from visible terrain or geophysical breaks.

---

## 16. No-data and valid-area handling

No-data is not the same as “no fault.” The official reference feature raster reports a very negative float sentinel, while the label raster reports `-1`. The sample submission and exact downloaded files should determine the authoritative valid mask.

Non-negotiable rules:

1. Create one explicit `valid_data_mask` from the official sample submission and/or supplied raster metadata.
2. Never convert no-data pixels into ordinary negative training examples.
3. Preserve the exact transform, CRS, width, height, bounds, and no-data behaviour in every submitted file.
4. Validate the final file with a dedicated script before upload.

---

# Part IV — Evaluation metric

## 17. Distance-weighted Tversky index

The competition uses a distance-weighted version of the Tversky index. It combines:

- true-positive credit;
- false-positive penalty;
- false-negative penalty;
- graded spatial tolerance around the true fault trace.

The final score is:

```math
DTI = TP_w / (TP_w + α·FP_w + β·FN_w + ε)
```

with:

```text
α = 0.2  (false-positive coefficient)
β = 0.8  (false-negative coefficient)
R = 300 m (three 100 m pixels)
```

The distance kernel is triangular:

```math
k(d) = max(1 - d/R, 0)
```

This means a prediction exactly on the labelled fault gets full spatial weight. A nearby prediction gets partial weight. At or beyond 300 m, proximity credit becomes zero.

Source and exact formula: [performance metric section](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)

---

## 18. What the metric implies—and what it does not imply

### Confirmed implication

A unit of false-negative error has four times the coefficient of a unit of false-positive error in the denominator, because `0.8 / 0.2 = 4`.

### Incorrect interpretation to avoid

This does **not** mean “predict faults everywhere.” The region contains vastly more background pixels than fault pixels, so diffuse low-quality probability can still create an enormous false-positive contribution.

### Practical implications to test

- Recall matters strongly.
- A slightly wider or spatially uncertain fault response may be better than a brittle one-pixel trace, but excessive width creates false-positive mass.
- Probabilities should be calibrated rather than automatically thresholded.
- Post-processing must be evaluated with the exact metric, not merely with IoU or F1.
- The 300 m tolerance is graded, not full credit anywhere inside a 300 m buffer.

---

## 19. Metric implementation requirements

Before serious modelling, implement the official distance-weighted Tversky metric locally and unit-test it.

Required tests:

1. Reproduce the official worked example score of approximately **0.60**.
2. Confirm behaviour for all-zero prediction.
3. Confirm behaviour for perfect prediction.
4. Confirm behaviour for one-pixel offsets at 100, 200, and 300 m.
5. Confirm behaviour for probabilistic predictions.
6. Confirm no-data handling.
7. Compare a thin line, a buffered line, and a diffuse map.
8. Test whether any thresholding or calibration improves out-of-fold score.

The exact competition metric, rather than an ordinary Tversky loss, must be used for model selection.

---

# Part V — Audit of the official reference solution

## 20. What the reference notebook does

The official repository is a useful starting point:

- [Repository](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Raw notebook](https://raw.githubusercontent.com/drivendataorg/gems-prize-reference-solution/main/unet-mc-cv-reference-solution.ipynb)

It currently:

1. loads the 19-band feature raster and fault label raster;
2. globally min-max normalizes every feature channel to `[0, 1]`;
3. creates 128 × 128 patches;
4. uses all 19 channels;
5. keeps only non-overlapping patches containing at least one labelled fault for the initial patch set;
6. creates overlapping training patches with a step of 32 pixels;
7. performs five random Monte Carlo train/test splits;
8. uses 50% of eligible patches as test patches in each split;
9. trains for five epochs per split with batch size 32 and learning rate `1e-4`;
10. uses a U-Net with a ResNet-18 encoder initialized with ImageNet weights;
11. uses AdamW and an ordinary binary Tversky loss with `α=0.2`, `β=0.8`;
12. applies random resized crop, horizontal and vertical flips, and rotations up to 30 degrees;
13. stores predictions for held-out test patches and writes a GeoTIFF.

A 128-pixel patch corresponds to **12.8 km × 12.8 km** at 100 m resolution. A training stride of 32 pixels corresponds to **3.2 km**.

---

## 21. What is good about the reference solution

It gives us a working example of:

- reading geospatial raster metadata;
- handling 19-channel neural-network input;
- building a segmentation model;
- using an asymmetric Tversky loss;
- performing augmentation;
- mapping patch predictions back into a raster;
- writing a georeferenced submission-like GeoTIFF;
- setting up CPU, Apple MPS, or NVIDIA GPU environments.

It is valuable as an instructional baseline and environment smoke test.

---

## 22. Important limitations and audit findings

The reference notebook should not be treated as a competition-ready final pipeline without modification.

### 22.1 It only selects patches that already contain mapped faults

The eligible patch list requires at least one positive label. Pure background and fully unlabelled patches are excluded from the initial patch set.

Consequences:

- the model does not learn a representative distribution of ordinary background;
- it cannot learn enough hard negative examples such as canyons or streams;
- it may generate excessive false positives when applied to the full region;
- the example output is not a proper full-region discovery pipeline.

### 22.2 The final map is made from held-out test-patch predictions, not standard full-extent inference

In each Monte Carlo split, the notebook predicts only the randomly held-out positive-containing patches. It accumulates those predictions into the output and divides each contribution by the total number of Monte Carlo iterations.

Consequences to audit:

- pure-unlabelled tiles remain zero;
- some positive tiles may not be selected as test in every iteration;
- dividing by total iterations rather than the number of predictions received can attenuate probability values;
- it is out-of-fold visualization rather than a conventional ensemble in which every trained model predicts every valid tile.

Our pipeline must train models and run sliding-window inference over **every valid pixel**, with overlap blending and explicit coverage checks.

### 22.3 Random positive-tile splitting is not sufficient spatial validation

Nearby patches share geology, acquisition artefacts, and potentially segments of the same fault system. A random tile split can overestimate performance on geographically unseen structures. This is a reasoned inference from the code, not a claim that the notebook contains direct label leakage.

We need geographic block and fault-object splits.

### 22.4 The training loss is not the exact competition metric

The notebook uses ordinary Tversky loss. The official score is distance-weighted and gives partial spatial credit. Training loss can remain Tversky-based, but model selection must use the exact official metric.

### 22.5 Normalization is simplistic

Global min-max normalization is highly sensitive to extreme values and data-release changes. NaN is later replaced with zero, which can make no-data numerically indistinguishable from a legitimate channel minimum unless a validity mask is added.

We should compare:

- robust percentile scaling;
- z-score or median/IQR scaling within valid cells;
- clipping per feature;
- explicit missingness/coverage channels;
- fold-safe normalization computed only from training regions.

### 22.6 A code comment and channel index appear inconsistent

The patch function says it checks valid elevation in “channel 4,” but the zero-based index used is `4`, which corresponds to Band 5 in the notebook's own printed list: isostatic gravity anomaly slope. The actual data coverage may be identical, but the comment or index is inconsistent and must be audited.

### 22.7 The 1 m DEM is unused

The baseline uses the 19 numerical channels only. It does not exploit the fine-scale terrain data.

### 22.8 Label incompleteness is not explicitly modelled

Excluding negative-only patches partially avoids treating the whole region as negative, but it is not a complete positive-unlabelled strategy. There is no confidence weighting, ignore mask, pseudo-labelling policy, or explicit treatment of uncertain negatives.

### 22.9 Augmentation may need to be modality-aware

Arbitrary image rotation and resampling can be helpful, but geophysical acquisition artefacts and directional features may not behave like natural RGB photographs. We should compare safe transforms such as flips and 90-degree rotations against arbitrary-angle rotations rather than assuming all image augmentation is valid.

---

## 23. Verified corrections and refinements to the initial project understanding

The re-verification produced several important refinements:

1. **The reference notebook is an instructional baseline, not yet a full-map competitive inference system.** Its held-out-positive-tile output must be replaced.
2. **There is a deadline wording conflict** between the current competition site and the official rules appendix.
3. **There is an unresolved scoring ambiguity** about how supplied known-fault pixels are treated when the initial test labels are newly identified faults.
4. **The filename and band descriptions differ across official sources.** Actual downloaded GeoTIFF metadata must be authoritative.
5. **The 1 m DEM is promising but not automatically a winning feature.** It also introduces strong false-positive structures and major compute costs.
6. **Predicting faults is not the same as predicting geothermal resources.** We should not overstate the interpretation of the model.
7. **Eligibility can be a hard stop for prize participation** and must be resolved before major investment.

---

# Part VI — Why the challenge is technically difficult

## 24. Main scientific and machine-learning challenges

### 24.1 Incomplete and noisy labels

Some real faults are absent, some mapped faults may be inaccurate, and mapped locations may be offset from the physical surface expression.

### 24.2 Extreme class imbalance

Fault traces occupy a tiny fraction of the full raster. A model can appear accurate by predicting background almost everywhere while completely failing the purpose of the challenge.

### 24.3 Spatial autocorrelation

Nearby pixels and patches are not independent. Random cross-validation can give misleadingly good scores because neighbouring terrain and survey artefacts appear in both training and validation.

### 24.4 Faults are elongated structures

A fault is usually a line or network, not an isolated blob. Continuity, orientation, junctions, and structural context matter.

### 24.5 Multi-modal inputs have different physical meanings

Magnetic, gravity, strain, seismic, conductivity, and terrain layers have different noise, scales, spatial support, and acquisition artefacts. Treating them as interchangeable colors may waste information.

### 24.6 Resolution mismatch

The main target is 100 m, while terrain is available at 1 m. A 10,000-to-1 pixel relationship must be handled efficiently.

### 24.7 Geological lookalikes

Streams, canyon edges, roads, shorelines, ridges, survey seams, lithological contacts, and processing artefacts can all look linear.

### 24.8 Dynamic final labels

The second-round ground truth is expanded after expert review. A model that overfits the fixed public leaderboard may fail to produce scientifically plausible candidates for the expanded evaluation.

---

## 25. Evidence from related fault-mapping research

The 2025 Hermant, Kiersnowski, and Bellanger study, linked by the organizers, trained convolutional models on elevation, slope, and satellite imagery for Quaternary fault detection. The study reported that models could detect known faults and propose new candidates that experts later confirmed using lidar. It also described false responses on canyon and stream boundaries and discussed paleo-shorelines and other geomorphic lookalikes. The authors emphasized imbalance, imperfect fault maps, and the possibility that unlabelled areas contain real faults.

These findings support our planned emphasis on:

- high-resolution terrain;
- hard-negative mining;
- incomplete-label methods;
- spatial/generalization testing;
- expert or geology-informed review;
- iterative learning rather than one-shot pixel classification.

Source: [Hermant et al. (2025), “Using deep learning to map Quaternary faults in Western USA”](https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2025/Hermant.pdf)

The organizers also link a 2021 study on automatic fault mapping from optical and topographic data as further reading:

- [Mattéo et al. (2021), Journal of Geophysical Research: Solid Earth](https://doi.org/10.1029/2020JB021269)

---

# Part VII — What we plan to build

## 26. Product definition

We plan to build a reproducible geospatial machine-learning system that:

1. ingests the official 100 m multi-band feature raster, known-fault labels, and permitted high-resolution terrain data;
2. validates and documents all coordinate systems, masks, bands, and licenses;
3. trains models using spatially honest validation;
4. accounts for incomplete labels and severe imbalance;
5. predicts fault probability for every valid 100 m cell;
6. combines coarse geophysical and fine terrain evidence;
7. preserves uncertainty rather than forcing every location into a hard binary decision;
8. produces a valid GeoTIFF and all documentation needed to reproduce it;
9. generates interpretable candidate maps for human geological review;
10. records experiments, data provenance, AI use, and final-selection decisions.

---

## 27. Proposed system architecture

The system should be developed in layers rather than beginning with the largest possible neural network.

### 27.1 Branch A — 100 m multi-modal model

Purpose: learn broad geophysical and tectonic patterns from the 19 aligned channels.

Initial implementation:

- robust per-channel normalization;
- explicit valid/no-data mask;
- spatial patches with overlap;
- a modest U-Net or comparable segmentation architecture;
- full-region sliding-window inference;
- overlap blending to reduce tile seams;
- out-of-fold probability maps.

Later experiments:

- U-Net++, DeepLabV3+, SegFormer, or other architectures;
- multi-scale context;
- separate encoders for feature families;
- learned feature gating or channel attention;
- larger-context low-resolution branch;
- self-supervised pretraining on the unlabeled feature raster.

### 27.2 Branch B — high-resolution terrain model

Purpose: identify subtle topographic fault expressions that are lost at 100 m.

Two implementation paths should be compared:

**Path B1: aggregated terrain features**

- derive multi-scale terrain measures from the 1 m DEM;
- summarize them to the 100 m grid;
- add them as channels to Branch A or to a tabular/segmentation auxiliary model.

**Path B2: dedicated high-resolution patch model**

- process selected 1 m or downsampled terrain patches;
- predict fine fault-lineament evidence;
- aggregate probability, orientation, and uncertainty to the 100 m grid;
- fuse with Branch A.

B1 is cheaper and should be attempted before B2.

### 27.3 Branch C — geometry, uncertainty, and fusion

Purpose: combine evidence while respecting fault-like geometry.

Candidate components:

- calibrated weighted ensemble of multiple spatial folds and architectures;
- test-time augmentation where physically justified;
- uncertainty from fold/model disagreement;
- multi-scale ridge/line filters;
- connected-component diagnostics;
- orientation consistency;
- optional skeleton or topology-aware losses;
- conservative gap bridging only when supported by surrounding evidence;
- probability calibration against out-of-fold predictions.

Geometry should refine evidence, not invent long lines unsupported by the data.

### 27.4 Optional Branch D — external data

Potential external sources may include raw GeoDAWN products, additional public terrain derivatives, optical imagery, geological maps, heat-flow or alteration datasets, and broader fault datasets. Every source must pass a licensing and sponsor-sharing review before use.

External data are a later-stage option. We should first understand what the official data already contain.

---

## 28. Central modelling hypothesis

Our strongest early hypothesis is:

> A geographically validated ensemble that combines 100 m geophysical evidence, fine-scale terrain evidence, explicit handling of incomplete labels, and fault-geometry diagnostics will outperform a larger generic image model trained with random patches.

This is a hypothesis, not a fact. Every component must earn its place through controlled experiments.

---

# Part VIII — Validation strategy

## 29. Validation is the highest-priority design decision

A competition model is only as good as the evidence used to choose it. A public leaderboard based on a limited public set can be noisy and exploitable. We need validation schemes that test the behaviours the final competition requires.

No single split answers every question. We should maintain several complementary validation views.

---

## 30. Geographic block cross-validation

Divide the valid region into large contiguous geographic blocks rather than random patches.

Requirements:

- keep neighbouring pixels together;
- add an exclusion buffer around validation boundaries when practical;
- ensure the same connected fault trace does not cross train and validation without explicit handling;
- map fold boundaries and fault density;
- compare latitudinal/longitudinal grids with geology-informed or acquisition-block splits;
- include at least one severe “leave-region-out” test.

A possible high-level holdout is by GeoDAWN acquisition block, but four blocks may be too coarse for all experiments. Nested sub-blocks can provide more folds while retaining geographic separation.

---

## 31. Fault-object grouped validation

Use the vector labels to define fault objects or connected trace groups. Assign complete fault objects to folds so that different portions of the same mapped structure are not casually split across train and validation.

This measures whether the model learns transferable fault signatures rather than memorizing one structure's neighbourhood.

---

## 32. Simulated hidden-fault validation

The actual challenge asks us to find faults missing from the public map. We can simulate this:

1. choose complete known fault objects as hidden faults;
2. remove them from the training target or place them in a held-out geographic block;
3. train without their positive labels;
4. evaluate whether the model recovers them;
5. ensure surrounding pixels are not incorrectly used as hard negatives in a way that reveals the experiment;
6. repeat across many faults and geological settings.

This is one of the most important validation ideas because it resembles the competition's missing-label structure more closely than ordinary random segmentation splits.

Maintain two variants:

- **Geographic discovery test:** all data in the hidden-fault geography are held out.
- **Label-missing robustness test:** the geography remains available but selected fault labels are removed, testing resistance to incomplete supervision.

---

## 33. Metrics to track locally

The official distance-weighted Tversky score is primary, but diagnostics should include:

- distance-weighted true positive, false positive, and false negative terms separately;
- recall of held-out fault objects;
- score by fault length, orientation, and terrain type;
- prediction probability by distance from a true fault;
- false-positive probability per square kilometre;
- connected-component length and fragmentation;
- calibration curves for out-of-fold probabilities;
- performance by feature availability and survey block;
- performance on manually curated hard negatives;
- performance on candidate previously hidden faults;
- inference coverage and seam artefacts.

Do not select a model solely by ordinary pixel accuracy, which is nearly meaningless under extreme imbalance.

---

## 34. Relationship to the public leaderboard

Use the public leaderboard as secondary evidence only.

A disciplined submission policy:

1. submit only models with a recorded local hypothesis;
2. compare leaderboard movement with spatial-validation movement;
3. do not tune dozens of thresholds directly to the public score;
4. reserve some submission capacity for format and sanity checks;
5. record every upload, model hash, local metrics, and exact post-processing;
6. select the final model using a pre-agreed combination of local evidence, robustness, and leaderboard evidence.

---

# Part IX — Handling incomplete labels and class imbalance

## 35. Training-mask design

Pixels should not be limited to only “positive” and “negative.” A more useful target system may contain:

- **positive:** mapped fault pixels or a narrow distance-weighted band;
- **confident background:** sampled far from mapped faults and curated candidates;
- **uncertain/unlabelled:** not mapped, but not trusted as negative;
- **no-data:** excluded entirely;
- **hard negative:** known fault lookalike, such as a stream or canyon edge, if curated.

The exact masks must be tested and documented.

---

## 36. Candidate strategies

Start simple and add complexity only when validation supports it.

### 36.1 Balanced and stratified sampling

Use a mixture of:

- positive-centred tiles;
- near-fault tiles;
- random valid background tiles;
- hard-negative tiles;
- candidate lineament tiles.

### 36.2 Soft distance targets

Instead of a one-pixel binary line, assign decreasing target confidence with distance from the mapped trace. This can reflect positional uncertainty and align better with the distance-tolerant metric.

### 36.3 Ignore zones

Do not penalize some uncertain pixels as strongly, especially near mapped traces or around high-confidence cross-model candidates.

### 36.4 Positive-unlabelled objectives

Compare methods that estimate the background distribution without declaring every unlabelled location negative. Possibilities include non-negative PU risk, asymmetric negative weighting, bootstrapping, or confidence-based pseudo-labelling.

### 36.5 Iterative pseudo-labelling

Only high-confidence candidates supported by multiple models/modalities should be considered, and they should remain separate from official truth. Use conservative weights and inspect for feedback loops.

### 36.6 Hard-negative mining

After each strong model, collect high-confidence false responses around:

- drainage channels;
- canyon walls;
- shorelines and beach ridges;
- roads and other human-made linear features;
- survey seams or flight-line artefacts;
- lithological contacts that are not target faults;
- raster boundaries and no-data edges.

Retrain with these examples while avoiding the assumption that every disagreement with the map is a true false positive.

---

# Part X — Data exploration plan

## 37. Required initial data audit

Create an automated inventory report containing:

- filenames and checksums;
- byte size;
- CRS, affine transform, bounds, width, height, resolution;
- number of bands and exact tags;
- data type and no-data value;
- valid-pixel count per band;
- min, max, robust percentiles, mean, standard deviation;
- NaN/no-data maps;
- pairwise channel correlations on a spatial sample;
- label pixel count and percentage;
- vector feature count and geometry types;
- 1 m DEM link count, tile extents, coverage, size, and license;
- sample submission metadata;
- differences between official page wording and actual files.

Save the report as both machine-readable JSON and human-readable Markdown.

---

## 38. Visual exploration deliverables

Build a geospatial EDA report with:

1. full-region thumbnails for all 19 bands;
2. robustly scaled and raw-value views;
3. known-fault overlays;
4. zoomed examples of strong and weak fault expressions;
5. profiles across fault traces for selected bands;
6. maps of feature missingness and survey boundaries;
7. label density and fault orientation rose plots;
8. differences between vector and raster labels;
9. examples of streams, canyons, ridges, roads, shorelines, and survey artefacts;
10. 1 m DEM hillshades at multiple sun angles;
11. spatial-fold maps;
12. acquisition-block and regional geology context.

Every image should include scale, north direction where appropriate, CRS, and location identifiers.

---

# Part XI — Phased execution roadmap

## 39. Phase 0 — Governance and eligibility

**Objective:** Ensure the project can legally and operationally participate.

Tasks:

- verify the intended individual/team/entity eligibility route;
- save a dated copy of official rules;
- establish team captain and primary submitter if applicable;
- agree in writing how any prize would be allocated;
- ask organizers about the deadline discrepancy;
- ask organizers about known-fault treatment in scoring;
- create AI-use and data-license logs;
- register/join on DrivenData if eligible.

**Exit criteria:** Eligibility route is documented, critical rule questions are sent, and compliance logs exist.

---

## 40. Phase 1 — Reproducible environment and data contract

**Objective:** Load all official data without ambiguity.

Tasks:

- clone and pin the official reference repository;
- create a Python 3.12 environment using the official lock/config where practical;
- download official data;
- calculate checksums;
- extract actual raster and vector metadata;
- compare filenames and bands with documentation;
- define the valid-area mask;
- implement a submission-format validator;
- write `data_dictionary.md` and `data_inventory.json`.

**Exit criteria:** One command can validate the data package, and a known-valid sample GeoTIFF passes our validator.

---

## 41. Phase 2 — Exact metric and baseline reproduction

**Objective:** Establish a trustworthy end-to-end benchmark.

Tasks:

- implement the exact distance-weighted Tversky metric;
- reproduce the official 0.60 worked example;
- run the reference notebook;
- document its outputs and limitations;
- modify it to include valid background sampling;
- add full-region sliding-window inference;
- blend overlaps and verify complete coverage;
- produce Baseline v0 submission and local report.

**Exit criteria:** We can generate a valid full-region GeoTIFF and reproduce the exact metric on tests.

---

## 42. Phase 3 — Spatial validation and strong 100 m baseline

**Objective:** Create local evidence that predicts real generalization.

Tasks:

- design geographic block folds;
- design grouped fault-object folds;
- build simulated hidden-fault tests;
- implement robust normalization and missingness masks;
- compare sampling strategies;
- train a modest U-Net baseline across folds;
- save out-of-fold maps;
- conduct channel-family ablations;
- build an error-analysis dashboard.

**Exit criteria:** Baseline v1 is stable across multiple spatial views and outperforms trivial/reference baselines for credible reasons.

---

## 43. Phase 4 — Incomplete-label methods and hard negatives

**Objective:** Improve discovery without flooding the map with false positives.

Tasks:

- test soft distance labels;
- test ignore masks and asymmetric negative weights;
- compare positive-unlabelled strategies;
- mine and curate hard negatives;
- model uncertainty from fold disagreement;
- inspect high-confidence map disagreements;
- consult geological expertise where available.

**Exit criteria:** At least one method improves hidden-fault validation and does not degrade geographic generalization or calibration.

---

## 44. Phase 5 — 1 m DEM integration

**Objective:** Add fine terrain evidence efficiently.

Tasks:

- audit coverage and storage needs;
- generate multi-scale terrain derivatives;
- aggregate initial features to 100 m;
- compare with the 100 m-only baseline;
- inspect false responses on geomorphic lookalikes;
- decide whether a high-resolution patch model is justified;
- if justified, train and fuse a dedicated terrain model.

**Exit criteria:** The terrain branch provides repeatable gains on fault-object and spatial validation, not only on random pixels.

---

## 45. Phase 6 — Ensemble, geometry, and calibration

**Objective:** Combine complementary evidence into a robust final candidate.

Tasks:

- ensemble folds, architectures, and data branches;
- calibrate probabilities with out-of-fold predictions;
- test line/topology diagnostics;
- compare thin, soft-buffered, and geometry-refined outputs;
- quantify uncertainty;
- produce candidate maps for manual review;
- stress-test acquisition seams, nodata edges, and confounders.

**Exit criteria:** Final candidates show consistent gains across validation schemes and pass all geospatial integrity checks.

---

## 46. Phase 7 — Submission freeze and reproducibility package

**Objective:** Select one defensible final submission before the official deadline.

Tasks:

- freeze model code and dependencies;
- rerun from clean environment where possible;
- regenerate the exact final GeoTIFF;
- verify SHA-256 checksum;
- run submission validator;
- document compute, seeds, folds, data versions, and post-processing;
- prepare generative-AI disclosure;
- prepare external-data license dossier;
- select the final submission in DrivenData;
- archive all final assets.

**Internal target:** freeze by 1 December 2026 or earlier, pending organizer clarification of the conflicting time cutoffs.

**Exit criteria:** One reproducible, validated, selected final submission and a complete handoff package exist.

---

# Part XII — Prioritized experiment backlog

## 47. Priority 0: foundation experiments

| Experiment | Hypothesis | Required evidence |
|---|---|---|
| Exact metric implementation | Local metric can reproduce organizer behaviour | Unit tests including official 0.60 example |
| Full-coverage inference | Reference output misses valid areas | Pixel coverage map equals valid mask |
| Spatial vs random CV | Random patches overestimate generalization | Compare fold scores and error maps |
| Valid background sampling | Positive-only training undercontrols false positives | Better DTI and hard-negative behaviour |
| Robust normalization | Percentile/median scaling is more stable than global min-max | Consistent fold gain and fewer artefacts |
| Overlap blending | Sliding-window seams harm predictions | Seam diagnostics and metric comparison |

---

## 48. Priority 1: strong modelling experiments

| Experiment | Hypothesis | Required evidence |
|---|---|---|
| Channel-family ablation | Some modalities provide unique value | Fold-wise delta with confidence intervals |
| Larger/multi-scale context | Fault systems need context beyond one patch scale | Fault-object recall and continuity improve |
| Soft distance labels | Spatial uncertainty is better represented than hard one-pixel labels | Exact DTI improves without excessive width |
| Ignore/uncertain masks | Not all unlabelled cells should be hard negatives | Hidden-fault recovery improves |
| Hard-negative mining | Confounders can be learned explicitly | Lower FP mass on curated zones |
| Modality-aware augmentation | Generic rotations may not always be physically helpful | Controlled ablation |
| Model ensemble | Different folds/models capture complementary structures | OOF and geographic holdout gains |

---

## 49. Priority 2: terrain and incomplete-label experiments

| Experiment | Hypothesis | Required evidence |
|---|---|---|
| Aggregated 1 m terrain derivatives | Fine scarps survive as informative 100 m summaries | Spatial/fault-object gain |
| High-resolution terrain model | Local morphology adds evidence beyond aggregates | Gain justifies compute and false-positive risk |
| PU-learning objective | Reduces suppression of unmapped faults | Better simulated-hidden-fault score |
| Conservative pseudo-labels | Cross-model agreement can expand training signal | Independent fold gain, no collapse |
| Uncertainty-aware fusion | Model disagreement identifies ambiguous regions | Better calibration and candidate prioritization |

---

## 50. Priority 3: advanced research ideas

Only pursue these after the foundation is stable:

- topology-aware or skeleton losses;
- steerable filters and orientation-aware networks;
- graph representations of candidate fault networks;
- self-supervised pretraining on the full feature cube;
- grouped modality encoders;
- transformer or hybrid segmentation architectures;
- external optical/radiometric/geological datasets;
- active-learning loop with a geologist;
- model distillation for reproducible inference.

A complex architecture without honest validation is lower priority than a simple model with correct data, metric, and inference.

---

# Part XIII — Engineering and experiment management

## 51. Suggested repository structure

```text
gems-prize/
├── README.md
├── pyproject.toml
├── uv.lock
├── configs/
│   ├── data/
│   ├── folds/
│   ├── models/
│   └── experiments/
├── data/
│   ├── raw/                 # never modify; usually not committed
│   ├── external/
│   ├── interim/
│   ├── processed/
│   └── checksums/
├── docs/
│   ├── GEMS_Prize_Challenge_Project_Guide.md
│   ├── data_dictionary.md
│   ├── rules_and_open_questions.md
│   ├── geology_learning_notes.md
│   └── decisions/
├── registries/
│   ├── data_sources.csv
│   ├── licenses.csv
│   ├── experiments.csv
│   ├── submissions.csv
│   └── ai_usage_log.md
├── notebooks/
│   ├── 00_data_audit.ipynb
│   ├── 01_geospatial_eda.ipynb
│   ├── 02_metric_validation.ipynb
│   └── 03_error_analysis.ipynb
├── src/gems/
│   ├── data/
│   ├── features/
│   ├── folds/
│   ├── metrics/
│   ├── models/
│   ├── training/
│   ├── inference/
│   ├── postprocessing/
│   ├── validation/
│   └── submission/
├── tests/
│   ├── test_metric.py
│   ├── test_geospatial_contract.py
│   ├── test_inference_coverage.py
│   └── test_submission.py
├── artifacts/
│   ├── folds/
│   ├── oof/
│   ├── models/
│   └── reports/
├── reports/
│   ├── figures/
│   └── experiments/
└── submissions/
```

Do not commit large raw data or secret credentials. Store data-download instructions and checksums instead.

---

## 52. Minimum experiment record

Every experiment must store:

- unique experiment ID;
- date and agent/person responsible;
- hypothesis;
- Git commit;
- configuration file;
- data checksum/version;
- fold definition version;
- random seeds;
- model architecture and parameter count;
- input channels and preprocessing;
- sampling method;
- training loss;
- exact validation metrics by fold;
- compute hardware and runtime;
- out-of-fold prediction path;
- maps of representative errors;
- decision: keep, reject, or investigate;
- next experiment;
- use of generative AI, if any.

No result should be trusted if its data version, fold, and post-processing cannot be reconstructed.

---

## 53. Submission validator requirements

A dedicated validator should reject a file unless all conditions pass:

- file opens with Rasterio/GDAL;
- exactly one band;
- dtype is float32;
- CRS equals EPSG:32611;
- affine transform exactly matches sample submission;
- width, height, and bounds exactly match;
- valid-area mask is correct;
- outside-mask cells have required null/NaN behaviour;
- all valid predictions are finite and within `[0, 1]`;
- no accidental all-zero/all-one map unless intentional;
- file size is plausible;
- a checksum and summary statistics are written;
- a thumbnail is generated for visual sanity checking.

---

# Part XIV — Agent organization

## 54. Recommended agent roles

### 54.1 Project lead / orchestrator

Responsibilities:

- maintain roadmap and priorities;
- resolve conflicts between agents;
- approve experiments before large compute runs;
- ensure results use comparable folds and metrics;
- maintain the decision log and final model shortlist.

Deliverables:

- weekly project status;
- prioritized backlog;
- decision records;
- final-selection rationale.

### 54.2 Rules and compliance agent

Responsibilities:

- monitor homepage, rules, forum, and announcements;
- track eligibility, deadlines, submission limits, AI disclosure, and external-data rights;
- draft organizer questions;
- maintain dated source snapshots.

Deliverables:

- `rules_and_open_questions.md`;
- compliance checklist;
- change alerts.

### 54.3 Geospatial data steward

Responsibilities:

- inventory rasters/vectors;
- validate CRS, transforms, masks, and band metadata;
- create data loaders and windowed IO;
- manage checksums and derived-data lineage.

Deliverables:

- data dictionary;
- valid mask;
- raster/vector audit;
- submission validator.

### 54.4 Geology research agent

Responsibilities:

- explain feature physics in plain language;
- summarize relevant fault-mapping literature;
- identify plausible confounders;
- help interpret spatial errors without claiming certainty.

Deliverables:

- geology primer;
- band interpretation notes;
- confounder catalogue;
- candidate-review checklist.

### 54.5 Metric and validation agent

Responsibilities:

- implement exact DTI;
- define spatial and fault-group folds;
- build simulated hidden-fault tests;
- audit leakage and produce fold maps.

Deliverables:

- unit-tested metric;
- fold files;
- validation protocol;
- OOF evaluation reports.

### 54.6 Baseline engineering agent

Responsibilities:

- reproduce the official notebook;
- identify code assumptions;
- implement full-extent inference;
- produce Baseline v0 and v1.

Deliverables:

- reproducible training/inference commands;
- baseline report;
- valid GeoTIFF.

### 54.7 Terrain/DEM agent

Responsibilities:

- audit 1 m DEM coverage;
- derive multi-scale topographic features;
- build aggregated and optional high-resolution branches;
- analyse terrain-specific false positives.

Deliverables:

- DEM feature pipeline;
- storage/compute estimate;
- terrain ablation report.

### 54.8 Modelling agent

Responsibilities:

- run controlled architecture, loss, sampling, and fusion experiments;
- use only approved validation;
- save checkpoints and OOF outputs;
- report negative as well as positive results.

Deliverables:

- experiment records;
- model cards;
- candidate ensembles.

### 54.9 Error-analysis agent

Responsibilities:

- map false positives and false negatives;
- cluster failure modes;
- maintain hard-negative and uncertain-candidate libraries;
- compare model disagreement.

Deliverables:

- interactive/static error report;
- curated case sets;
- next-experiment recommendations.

### 54.10 Reproducibility and submission agent

Responsibilities:

- rerun final pipeline from clean state;
- validate output metadata;
- archive code, configs, hashes, logs, and documentation;
- prepare AI-use and external-data disclosures.

Deliverables:

- final reproducibility bundle;
- final submission checksum;
- finalist documentation draft.

---

## 55. Standard handoff template for every agent session

```markdown
# GEMS Session Handoff

## Session metadata
- Date/time:
- Agent/role:
- Git commit:
- Environment lock hash:
- Data version/checksums:

## Objective
What specific question was this session trying to answer?

## Sources consulted
List official pages, papers, code, and access dates.

## Work completed
Describe code, analysis, experiments, and files produced.

## Results
Include fold-wise metrics, exact configuration, and relevant maps.

## Interpretation
Separate observations from hypotheses. State uncertainty.

## Decisions made
What was accepted, rejected, or deferred, and why?

## Problems / risks
List bugs, ambiguity, leakage risk, compute constraints, or rule questions.

## Open questions
What remains unresolved?

## Recommended next actions
Prioritized, concrete tasks for the next session.
```

---

## 56. Reusable prompt for a new agent

```text
You are contributing to the GEMS Prize Challenge project.

First read GEMS_Prize_Challenge_Project_Guide.md in full. Treat it as a
working project charter, not as an authority that overrides current official
competition sources.

Before acting:
1. Re-check the DrivenData homepage, problem description, official rules,
   and competition forum for changes.
2. Identify whether each statement you make is a confirmed fact, derived
   fact, working hypothesis, or open question.
3. Use the existing data, fold, metric, experiment, license, and AI-use
   registries. Do not create an incompatible parallel workflow.
4. Do not use the public leaderboard as the primary validation set.
5. Do not treat all unlabelled pixels as confirmed negatives without an
   explicit experiment and rationale.
6. Do not call an algorithmic lineament a discovered fault without expert
   geological confirmation.
7. Preserve the official geospatial contract exactly.

Your assigned role is: [ROLE]
Your task is: [TASK]
Required deliverables are: [DELIVERABLES]
The decision this work must support is: [DECISION]
```

---

# Part XV — Rules, compliance, and operational safeguards

## 57. Generative-AI disclosure

The official rules allow generative AI but require disclosure of the extent and manner of use. Since AI agents are part of this project, maintain `registries/ai_usage_log.md` from day one.

For each use, record:

- date;
- tool/model, if known;
- purpose;
- whether generated code, text, analysis, or research guidance was used;
- files affected;
- human review performed;
- known limitations or corrections.

Do not wait until the deadline to reconstruct this history.

---

## 58. External-data license registry

For every external source, record:

- dataset title and provider;
- source URL and access date;
- version/date;
- license text and URL;
- whether competition use is permitted;
- whether sharing with the sponsor for evaluation is permitted;
- whether redistribution is permitted;
- citation requirement;
- files and derived features used;
- approver and decision.

A publicly viewable dataset is not automatically licensed for every competition use.

---

## 59. Team and prize administration

The official rules state that a team award is paid as one amount to the designated primary submitter, who is responsible for distributing it. The administrator will not arbitrate team disputes.

Before serious collaboration, document:

- captain and primary submitter;
- eligibility representations;
- ownership and permitted use of code/data;
- prize-sharing agreement;
- publication and publicity expectations;
- confidentiality markings where needed;
- what happens if a member leaves.

---

## 60. Reproducibility and disclosure to DOE/NLR

Finalists may be required to submit complete code assets, documentation, and resource requirements sufficient to reproduce results and generate predictions on new data.

Therefore:

- avoid unrecoverable notebook-only workflows;
- pin dependencies;
- record random seeds;
- make preprocessing deterministic;
- document hardware assumptions;
- archive model weights and exact configs;
- ensure any external assets can legally be provided or re-obtained;
- clearly mark confidential material according to official rules.

---

# Part XVI — Open questions to send to organizers

## 61. Highest-priority questions

### Question 1 — Treatment of supplied known faults during scoring

The submission instructions request predictions for all faults, while initial test labels are newly identified faults absent from the supplied public mapping. Are supplied known-fault pixels included as positives, ignored/masked, or otherwise excluded from false-positive accounting in public/private scoring?

### Question 2 — Exact deadline cutoff

The DrivenData page lists 3 December 2026 at 11:59 p.m. UTC, while Appendix A of the official rules refers to 5:00 p.m. ET on the deadline date. Which exact timestamp controls?

### Question 3 — Authoritative filenames and band metadata

The problem page names `training_features.tif`; the official reference notebook uses `numeric_features.tif`. The problem page and notebook also describe some depth-related bands differently. Which file/version and band dictionary are authoritative?

### Question 4 — No-data scoring mask

Are pixels outside the valid survey footprint ignored entirely? Must they be NaN, or is the sample submission mask the sole authoritative template?

### Question 5 — Metric reference implementation

Will the organizers publish exact metric code, including handling of NaN, positive probabilities, ties, borders, and no-data pixels?

---

## 62. Additional useful questions

- Does the 19-band feature raster include any radiometric channel, or is radiometric data only available through external/raw GeoDAWN products?
- Is deterministic algorithmic post-processing, such as thinning or line linking, fully permitted as part of the model pipeline?
- For external data, what exactly must be shareable with the sponsor: raw data, derived features, code to reacquire data, or all of these?
- At what stage and in what format is the generative-AI narrative required?
- Are human-reviewed adjustments to model predictions allowed, or must the final GeoTIFF be produced entirely by a reproducible algorithm?
- What are the exact team-member eligibility expectations for people who are not U.S. citizens/permanent residents but may or may not have U.S. work authorization?

Do not send duplicates if the forum or organizers answer them publicly first.

---

# Part XVII — What success looks like

## 63. Minimum viable competition entry

A valid minimum entry requires:

- eligibility/compliance resolved;
- official data loaded correctly;
- exact metric implemented;
- a modest segmentation model;
- full-valid-area inference;
- geospatially valid GeoTIFF;
- reproducible code and experiment record;
- one selected final submission.

This is achievable even without advanced geology expertise.

---

## 64. Competitive entry

A serious competitive entry should additionally have:

- spatial and fault-object cross-validation;
- simulated hidden-fault tests;
- robust background/hard-negative sampling;
- explicit incomplete-label treatment;
- multi-scale geophysical context;
- useful 1 m terrain integration;
- calibrated ensemble and uncertainty;
- careful confounder analysis;
- geology-informed candidate review;
- clean reproducibility and license documentation.

---

## 65. Difficulty assessment

The problem statement is learnable. The main concepts can be understood without prior geology training, especially when introduced through maps and examples.

The competition is difficult to win because it combines:

- geospatial engineering;
- computer vision;
- incomplete labels;
- unusual evaluation;
- multi-scale data;
- geological interpretation;
- reproducibility and federal-prize rules.

It is still a good project for a technically strong beginner in geology because the organizers provide a reference solution, the task has a clear output contract, and domain knowledge can be acquired incrementally. The hardest part is unlikely to be memorizing geology vocabulary; it will be designing honest validation and learning from incomplete spatial labels.

---

# Part XVIII — Immediate next actions

## 66. First ten actions for the next session

1. Resolve or formally investigate eligibility.
2. Save local copies of the current homepage, problem page, official rules, and reference repository commit.
3. Send the two critical organizer questions: known-fault scoring treatment and deadline cutoff.
4. Join the competition and download data if eligible and permitted.
5. Create checksums and run the data inventory.
6. Export the actual 19-band metadata and reconcile documentation discrepancies.
7. Build the exact metric and reproduce the official example.
8. Run the official notebook unchanged as a smoke test.
9. replace its output logic with full-region inference and a valid-background sampling baseline.
10. Design and visualize geographic and fault-object folds before architecture experimentation.

---

## 67. Decisions we should deliberately postpone

Do not yet commit to:

- a very large transformer;
- raw full-resolution DEM training over the whole region;
- external satellite datasets;
- aggressive line linking or skeletonization;
- pseudo-labeling thousands of candidate faults;
- a final probability threshold;
- a single validation split;
- treating all unlabelled pixels as negative;
- masking known faults from the submission.

These decisions require evidence or organizer clarification.

---

# Part XIX — Glossary

| Term | Plain-language meaning |
|---|---|
| Fault | A fracture/discontinuity in Earth's crust across which rock has moved |
| Fault plane | The underground surface along which displacement occurs |
| Fault trace | The line where the fault plane intersects the ground surface |
| Fault zone | A group of related nearby fractures |
| Fault scarp | A step or steep break in terrain created or preserved by fault movement |
| Quaternary fault | A fault with movement during the Quaternary period; exact age categories vary by mapping source |
| DEM | Digital Elevation Model: a grid of ground elevation |
| Lidar | Laser-based remote sensing that can produce detailed terrain models |
| Geophysics | Studying Earth using physical measurements such as magnetism, gravity, seismic waves, or electricity |
| Magnetic anomaly | Difference between observed and expected magnetic field, often linked to rock properties |
| Gravity anomaly | Small variation in gravity related to differences in subsurface density |
| Conductivity | How easily electrical current passes through material |
| Strain | Deformation of the crust; shear changes shape, dilatation changes area/volume |
| Raster | A geographic grid of cells/pixels |
| Vector | Points, lines, or polygons with coordinates |
| GeoTIFF | A TIFF image that stores geographic coordinate information |
| CRS | Coordinate Reference System: rules that map grid coordinates to locations on Earth |
| UTM | A projected coordinate system dividing Earth into zones; the challenge uses Zone 11N |
| EPSG:32611 | Identifier for WGS 84 / UTM Zone 11N |
| Segmentation | Predicting a class or probability for every pixel |
| U-Net | A neural-network architecture commonly used for image segmentation |
| Encoder | Model portion that compresses input into higher-level features |
| Decoder | Model portion that restores spatial detail to make a pixel-level output |
| Tversky index | Overlap metric with adjustable penalties for false positives and false negatives |
| False positive | Predicting fault where the evaluation says there is none |
| False negative | Failing to predict a labelled fault |
| Class imbalance | One class, here background, is far more common than the other |
| Spatial autocorrelation | Nearby locations tend to be similar, violating ordinary independence assumptions |
| Positive-unlabelled learning | Learning when positive examples are known but the remaining data are not confirmed negatives |
| Hard negative | A non-target example that looks confusingly similar to the target |
| Out-of-fold prediction | Prediction for an example made by a model that did not train on that example/fold |
| Calibration | Making probability values reflect reliable levels of confidence |
| Ensemble | Combining multiple models or folds |
| Lineament | A visible linear feature; it may or may not be a geological fault |
| Topology | Connectivity and structural relationships among predicted lines or regions |
| No-data | A cell without a valid measurement; not the same as a zero value or no fault |

---

# Part XX — Source register

All sources below were checked on 13 September 2026 unless otherwise stated.

## Official competition sources

1. DrivenData. **GEMS Prize Challenge homepage.**  
   https://www.drivendata.org/competitions/306/competition-doe-gems/

2. DrivenData. **GEMS Prize Challenge problem description, data, metric, and submission format.**  
   https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/

3. DrivenData. **GEMS Prize Challenge background/about page.**  
   https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/

4. National Lab of the Rockies / U.S. Department of Energy. **Geologic Enhanced Mapping System (GEMS) Prize Official Rules.**  
   https://docs.nlr.gov/docs/fy26osti/96647.pdf

5. DrivenData Community. **GEMS Prize Challenge forum.**  
   https://community.drivendata.org/c/gems-prize-challenge/111

## Official reference solution

6. DrivenData. **GEMS Prize reference-solution repository.**  
   https://github.com/drivendataorg/gems-prize-reference-solution

7. DrivenData / John Lipor. **Fault Detection Using U-Net with Monte Carlo Cross-Validation notebook.**  
   https://raw.githubusercontent.com/drivendataorg/gems-prize-reference-solution/main/unet-mc-cv-reference-solution.ipynb

## Data provenance

8. U.S. Geological Survey. **GeoDAWN: Airborne magnetic and radiometric surveys of the northwestern Great Basin, Nevada and California.**  
   https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and

## Research referenced by the organizers

9. Hermant, B., Kiersnowski, L., and Bellanger, M. (2025). **Using deep learning to map Quaternary faults in Western USA.** Proceedings of the 50th Workshop on Geothermal Reservoir Engineering.  
   https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2025/Hermant.pdf

10. Mattéo, L., Manighetti, I., Tarabalka, Y., Gaucel, J.-M., van den Ende, M., Mercier, A., et al. (2021). **Automatic fault mapping in remote optical images and topographic data with deep learning.** Journal of Geophysical Research: Solid Earth, 126, e2020JB021269.  
    https://doi.org/10.1029/2020JB021269

---

# Final project statement

We are building a scientifically cautious, geospatially correct, reproducible fault-probability mapping system for the GeoDAWN region. The solution will begin with the official 19-channel 100 m data, establish exact metric and spatial validation, improve the reference baseline into a true full-region inference pipeline, explicitly address incomplete labels, add high-resolution terrain evidence only after controlled tests, and combine models through calibrated, geometry-aware fusion. Compliance, eligibility, licenses, AI disclosure, and reproducibility are first-class parts of the solution rather than end-of-project paperwork.

