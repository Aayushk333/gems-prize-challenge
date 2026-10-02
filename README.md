# GEMS Prize Challenge Project

Collaborative workspace for understanding the GEMS Prize Challenge dataset, reproducing the organizer's reference solution, and developing a geospatially correct fault-probability workflow.

This repository intentionally does **not** redistribute the competition GeoTIFFs. Each teammate should register for the competition, accept the applicable rules, and download the official data through DrivenData.

## Start here

1. Read [`dataset_explanation.md`](dataset_explanation.md) for a ground-up, layperson-friendly explanation of the data.
2. Read [`GEMS_Prize_Challenge_Project_Guide.md`](GEMS_Prize_Challenge_Project_Guide.md) for the broader competition brief, risks, and build plan.
3. Review the generated maps in [`data_overview/`](data_overview/).
4. Inspect the organizer's original benchmark in [`gems-prize-reference-solution/`](gems-prize-reference-solution/).

## Clone with the reference-solution submodule

```bash
git clone --recurse-submodules https://github.com/Aayushk333/gems-prize-challenge.git
cd gems-prize-challenge
```

If the repository was cloned without submodules:

```bash
git submodule update --init --recursive
```

## Download the competition data

After joining the competition, download these files from its data page and place them under:

```text
gems-prize-reference-solution/data/
```

Expected local filenames in this project are:

```text
example_submission.tif
existing_faults.tif
gems-geodawn-numerical-features.tif
tnm_items.json
```

The TIFF files are ignored by Git. `tnm_items.json` is also treated as downloaded competition material and is not required in Git; the dataset handbook records its inspected structure.

The organizer notebook currently expects `numeric_features.tif` and `labels.tif`, which differ from the downloaded filenames above. Do not duplicate the large files solely to satisfy those names; update the notebook's two path variables in a working copy when reproducing it.

## Recreate the read-only data overview

Create an environment containing Rasterio, NumPy, and Matplotlib, then run:

```bash
python inspect_data.py
```

The script reads the local files without modifying them and writes its derived inventory and PNG previews to `data_overview/`.

## Repository layout

```text
.
├── README.md
├── dataset_explanation.md
├── GEMS_Prize_Challenge_Project_Guide.md
├── AI_USAGE_LOG.md
├── inspect_data.py
├── data_overview/
└── gems-prize-reference-solution/   # official DrivenData Git submodule
```

## Reference solution provenance

The benchmark is included as a Git submodule pointing to:

<https://github.com/drivendataorg/gems-prize-reference-solution>

The pinned commit at initial project publication is:

```text
aebe92f7c8a990f0e3443451b7a825d9afd6336b
```

The reference solution remains the work of its original authors and is kept separate from our project code and documentation.

## Collaboration and compliance

- Do not commit downloaded competition data, secrets, credentials, or trained model artifacts.
- Teammates should be formally registered and satisfy the competition's team and eligibility rules.
- Preserve GeoTIFF CRS, transform, resolution, bounds, and no-data masks.
- Record external-data licensing before use.
- Record material generative-AI assistance in `AI_USAGE_LOG.md`.
- Re-check the official competition page, rules, and forum because requirements can change.

Official competition page:

<https://www.drivendata.org/competitions/306/competition-doe-gems/>

