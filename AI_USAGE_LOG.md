# Generative AI Usage Log

This log supports the GEMS Prize Challenge requirement to disclose the extent and manner of generative-AI use. Add an entry whenever AI materially contributes code, documentation, research synthesis, analysis, or experimental decisions.

## 2026-09-13 to 2026-10-02 — Initial project orientation and repository setup

- **Tool/model:** OpenAI Codex assistant; exact deployed model version not exposed in the workspace.
- **Purpose:** Read the project guide, clone and audit the official reference solution, inspect the supplied GeoTIFFs, explain the dataset in beginner-friendly language, generate read-only visual summaries, and prepare the collaborative Git repository.
- **Generated or materially assisted content:**
  - `dataset_explanation.md`
  - `inspect_data.py`
  - `data_overview/data_inventory.json`
  - `data_overview/numerical_features_overview.png`
  - `data_overview/fault_rasters_overview.png`
  - `data_overview/fault_rich_closeup.png`
  - `README.md`
  - `.gitignore`
  - this usage log
- **Human review:** The project owner requested the work and reviewed the explanations iteratively. Exact raster metadata, alignment, cell counts, hashes, and example values were checked programmatically against the local files.
- **Known limitations:** Several feature-band units and source derivations remain undocumented in the GeoTIFF tags and are explicitly recorded as open questions. The AI-generated explanations are not geological validation of any predicted structure.
- **Data handling:** Inspection was read-only. Downloaded competition TIFFs were not modified and are excluded from Git publication.

