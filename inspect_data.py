"""Read-only inventory and visualization of the downloaded GEMS data."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "gems-prize-reference-solution" / "data"
OUTPUT_DIR = PROJECT_ROOT / "data_overview"
FEATURE_PATH = DATA_DIR / "gems-geodawn-numerical-features.tif"
LABEL_PATH = DATA_DIR / "existing_faults.tif"
SUBMISSION_PATH = DATA_DIR / "example_submission.tif"
DEM_LINKS_PATH = DATA_DIR / "tnm_items.json"


def raster_summary(path: Path) -> dict:
    with rasterio.open(path) as src:
        return {
            "path": path.relative_to(PROJECT_ROOT).as_posix(),
            "driver": src.driver,
            "width": src.width,
            "height": src.height,
            "bands": src.count,
            "dtypes": list(src.dtypes),
            "crs": str(src.crs),
            "resolution": list(src.res),
            "bounds": [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top],
            "transform": list(src.transform)[:6],
            "nodata": src.nodata,
            "compression": src.compression.name if src.compression else None,
            "block_shapes": [list(shape) for shape in src.block_shapes],
            "descriptions": list(src.descriptions),
            "dataset_tags": src.tags(),
            "band_tags": [src.tags(i) for i in range(1, src.count + 1)],
        }


def read_preview(src: rasterio.DatasetReader, max_height: int = 900) -> np.ma.MaskedArray:
    out_height = min(max_height, src.height)
    out_width = round(src.width * out_height / src.height)
    return src.read(
        out_shape=(src.count, out_height, out_width),
        masked=True,
        resampling=Resampling.average,
    )


def plot_feature_bands(report: dict) -> None:
    with rasterio.open(FEATURE_PATH) as src:
        preview = read_preview(src)
        fig, axes = plt.subplots(5, 4, figsize=(12, 14), constrained_layout=True)
        axes = axes.ravel()
        stats = []
        for band_idx in range(src.count):
            band = preview[band_idx]
            values = band.compressed()
            percentiles = np.percentile(values, [1, 5, 50, 95, 99])
            stats.append(
                {
                    "band": band_idx + 1,
                    "description": src.tags(band_idx + 1).get("description"),
                    "category": src.tags(band_idx + 1).get("data_category"),
                    "preview_valid_cells": int(values.size),
                    "preview_percentiles_1_5_50_95_99": percentiles.tolist(),
                    "preview_min": float(values.min()),
                    "preview_max": float(values.max()),
                }
            )
            low, high = percentiles[0], percentiles[-1]
            shown = np.ma.clip(band, low, high)
            image = axes[band_idx].imshow(shown, cmap="viridis", vmin=low, vmax=high)
            description = src.tags(band_idx + 1).get("description", f"Band {band_idx + 1}")
            short = description.split(" - ")[0]
            axes[band_idx].set_title(f"{band_idx + 1}. {short}", fontsize=10)
            axes[band_idx].axis("off")
            fig.colorbar(image, ax=axes[band_idx], fraction=0.035, pad=0.02)
        for axis in axes[src.count :]:
            axis.axis("off")
        fig.suptitle(
            "GEMS numerical feature bands\nNorth is up; colors are scaled independently to each band's 1st–99th percentiles",
            fontsize=16,
        )
        fig.savefig(OUTPUT_DIR / "numerical_features_overview.png", dpi=100)
        plt.close(fig)
        report["feature_preview_statistics"] = stats


def exact_value_counts(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with rasterio.open(path) as src:
        data = src.read(1)
        values, counts = np.unique(data, return_counts=True)
        mask = src.dataset_mask() > 0
    return values, counts, mask


def plot_fault_rasters(report: dict) -> None:
    with rasterio.open(LABEL_PATH) as labels_src, rasterio.open(SUBMISSION_PATH) as sub_src:
        labels = labels_src.read(1)
        submission = sub_src.read(1)
        label_valid = labels_src.dataset_mask() > 0
        submission_valid = sub_src.dataset_mask() > 0

        known = (labels > 0) & label_valid
        finite_submission = np.isfinite(submission) & submission_valid
        predicted = (submission > 0) & finite_submission

        report["alignment_checks"] = {
            "features_labels_same_shape": None,
            "features_labels_same_crs": None,
            "features_labels_same_transform": None,
            "labels_submission_same_shape": labels.shape == submission.shape,
            "labels_submission_same_crs": labels_src.crs == sub_src.crs,
            "labels_submission_same_transform": labels_src.transform == sub_src.transform,
            "labels_submission_valid_masks_equal": bool(np.array_equal(label_valid, submission_valid)),
            "known_fault_pixels_equal_positive_submission_pixels": bool(np.array_equal(known, predicted)),
        }
        with rasterio.open(FEATURE_PATH) as features_src:
            report["alignment_checks"].update(
                {
                    "features_labels_same_shape":
                        (features_src.height, features_src.width) == labels.shape,
                    "features_labels_same_crs": features_src.crs == labels_src.crs,
                    "features_labels_same_transform": features_src.transform == labels_src.transform,
                }
            )

        report["label_counts"] = {
            "total_cells": int(labels.size),
            "valid_cells": int(label_valid.sum()),
            "outside_or_nodata_cells": int((~label_valid).sum()),
            "known_fault_cells": int(known.sum()),
            "valid_background_cells": int((label_valid & ~known).sum()),
            "known_fault_share_of_valid_percent": float(known.sum() / label_valid.sum() * 100),
        }
        report["example_submission_counts"] = {
            "finite_valid_cells": int(finite_submission.sum()),
            "positive_cells": int(predicted.sum()),
            "minimum_finite_valid": float(submission[finite_submission].min()),
            "maximum_finite_valid": float(submission[finite_submission].max()),
        }

        stride = 4
        footprint = label_valid[::stride, ::stride]
        known_small = known[::stride, ::stride]
        submission_small = np.ma.masked_where(
            ~submission_valid[::stride, ::stride], submission[::stride, ::stride]
        )

        fig, axes = plt.subplots(1, 3, figsize=(18, 7), constrained_layout=True)
        axes[0].imshow(footprint, cmap="Greys", vmin=0, vmax=1)
        axes[0].set_title("Valid survey footprint")
        axes[1].imshow(known_small, cmap="gray_r", vmin=0, vmax=1)
        axes[1].set_title("Existing fault labels")
        axes[2].imshow(submission_small, cmap="magma", vmin=0, vmax=1)
        axes[2].set_title("Example submission values")
        for axis in axes:
            axis.axis("off")
        fig.suptitle("Aligned 100 m competition rasters (north is up)", fontsize=16)
        fig.savefig(OUTPUT_DIR / "fault_rasters_overview.png", dpi=170)
        plt.close(fig)


def plot_fault_rich_closeup(report: dict) -> None:
    """Show several feature layers around a label-rich 25.6 km square."""
    window_size = 256
    with rasterio.open(LABEL_PATH) as labels_src:
        labels = labels_src.read(1)
        valid_height = labels_src.height // window_size * window_size
        valid_width = labels_src.width // window_size * window_size
        positives = (labels[:valid_height, :valid_width] > 0).reshape(
            valid_height // window_size,
            window_size,
            valid_width // window_size,
            window_size,
        )
        block_counts = positives.sum(axis=(1, 3))
        block_row, block_col = np.unravel_index(np.argmax(block_counts), block_counts.shape)
        row_off = int(block_row * window_size)
        col_off = int(block_col * window_size)
        window = Window(col_off, row_off, window_size, window_size)
        label_window = labels_src.read(1, window=window) > 0
        left, bottom, right, top = rasterio.windows.bounds(window, labels_src.transform)

    selected_bands = [1, 3, 5, 12, 15, 19]
    with rasterio.open(FEATURE_PATH) as features_src:
        fig, axes = plt.subplots(2, 4, figsize=(14, 7), constrained_layout=True)
        axes = axes.ravel()
        for axis, band_idx in zip(axes, selected_bands):
            band = features_src.read(band_idx, window=window, masked=True)
            values = band.compressed()
            low, high = np.percentile(values, [1, 99])
            axis.imshow(np.ma.clip(band, low, high), cmap="viridis", vmin=low, vmax=high)
            axis.contour(label_window, levels=[0.5], colors="red", linewidths=0.7)
            short = features_src.tags(band_idx).get("description", "").split(" - ")[0]
            axis.set_title(f"Band {band_idx}: {short}", fontsize=9)
            axis.axis("off")
        axes[6].imshow(label_window, cmap="gray_r", vmin=0, vmax=1)
        axes[6].set_title("Known-fault label only")
        axes[6].axis("off")
        axes[7].axis("off")
        fig.suptitle(
            "Fault-rich 25.6 km × 25.6 km close-up\nKnown labels are outlined in red over each feature",
            fontsize=14,
        )
        fig.savefig(OUTPUT_DIR / "fault_rich_closeup.png", dpi=130)
        plt.close(fig)

    report["closeup"] = {
        "pixel_window_row_col_size": [row_off, col_off, window_size],
        "utm_bounds_left_bottom_right_top": [left, bottom, right, top],
        "known_fault_cells": int(label_window.sum()),
        "selected_bands": selected_bands,
    }


def summarize_dem_links(report: dict) -> None:
    links = json.loads(DEM_LINKS_PATH.read_text(encoding="utf-8"))
    projects = []
    extensions = []
    hosts = []
    filenames = []
    for link in links:
        parsed = urlparse(link)
        parts = parsed.path.split("/")
        projects.append(parts[parts.index("Projects") + 1] if "Projects" in parts else "unknown")
        filename = Path(parsed.path).name
        filenames.append(filename)
        extensions.append(Path(filename).suffix.lower())
        hosts.append(parsed.netloc)
    report["dem_links"] = {
        "count": len(links),
        "unique_count": len(set(links)),
        "hosts": dict(Counter(hosts)),
        "extensions": dict(Counter(extensions)),
        "project_counts": dict(Counter(projects).most_common()),
        "first_five_filenames": filenames[:5],
        "first_url": links[0],
        "last_url": links[-1],
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    report = {
        "rasters": {
            path.name: raster_summary(path)
            for path in (FEATURE_PATH, LABEL_PATH, SUBMISSION_PATH)
        }
    }
    plot_feature_bands(report)
    plot_fault_rasters(report)
    plot_fault_rich_closeup(report)
    summarize_dem_links(report)
    (OUTPUT_DIR / "data_inventory.json").write_text(
        json.dumps(report, indent=2, allow_nan=True), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
