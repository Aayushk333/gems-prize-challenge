# GEMS Prize Challenge Dataset Explanation

**Document purpose:** A standalone, beginner-friendly handbook for understanding the downloaded GEMS Prize Challenge data before performing any modelling or transformation.

**Workspace:** `C:\Users\ak32028\Downloads\GEMS Prize Challenge`

**Local data directory:** `gems-prize-reference-solution/data/`

**Local files inspected:** 25 September 2026

**Scope:** This document explains what the supplied files are, what a raster and GeoTIFF are, what each file and numerical band contains, how the files align, what the stored values mean, how to view the data, and which facts remain uncertain. It intentionally does not design or train a model.

---

## 1. Executive summary

The downloaded data describes part of Nevada and eastern California using maps made from regular grids.

The most useful mental picture is:

```text
The study region is divided into 100 m × 100 m squares.

For each square:
    - the numerical-feature file stores 19 scientific measurements;
    - the existing-fault file stores whether a supplied known fault crosses it;
    - the example-submission file demonstrates how a future answer must be stored.
```

The three GeoTIFF files cover exactly the same grid. Their rows and columns line up cell for cell.

The fourth downloaded file, `tnm_items.json`, is not a map. It is a text list containing 894 web links to much more detailed 1-metre elevation tiles hosted by the USGS. Those elevation tiles have not been downloaded into this workspace.

The downloaded files are:

| File | Plain-language role |
|---|---|
| `gems-geodawn-numerical-features.tif` | The main scientific measurements: 19 aligned maps in one file |
| `existing_faults.tif` | The supplied map of known faults, converted into grid cells |
| `example_submission.tif` | An example output/template using the same grid; not a new source of geological evidence |
| `tnm_items.json` | A list of 894 URLs for separate USGS 1 m elevation GeoTIFFs |

The main numerical raster has 3,730 rows, 3,292 columns, and 19 bands. A single grid cell therefore has 19 feature values describing the same 100 m × 100 m location.

---

## 2. Start with the basic idea: a map can be stored as numbers

A paper map uses colors, symbols, and lines that a person can see. A computer needs those objects to be stored as numbers.

One way to do this is to divide the map into equally sized squares:

```text
                 Columns increase to the right
                    0       1       2       3
                 ┌───────┬───────┬───────┬───────┐
Row 0            │ cell  │ cell  │ cell  │ cell  │
                 ├───────┼───────┼───────┼───────┤
Row 1            │ cell  │ cell  │ cell  │ cell  │
                 ├───────┼───────┼───────┼───────┤
Row 2            │ cell  │ cell  │ cell  │ cell  │
                 └───────┴───────┴───────┴───────┘
                           Rows increase downward
```

Each square is called a **cell**, **grid cell**, or **pixel**. In raster mapping, these words are often used interchangeably.

A raster pixel is not merely a dot on a monitor. It represents a physical area on Earth. In the main GEMS rasters, one pixel represents:

```text
100 metres east-west × 100 metres north-south
```

That is:

```text
10,000 square metres
= 1 hectare
= 0.01 square kilometres
```

Every cell can store a number. What that number means depends on the map:

- In an elevation map, the number can represent height.
- In a magnetic map, the number represents a magnetic measurement or a derived magnetic quantity.
- In the fault-label map, `1` means a supplied known fault crosses the cell.
- In a prediction map, a decimal such as `0.75` can represent confidence that a fault is present.

---

## 3. What is a raster?

A **raster** is a rectangular grid of cells in which every cell stores a value.

This is similar to a spreadsheet:

- A spreadsheet has rows and columns.
- A raster has rows and columns.
- A spreadsheet cell stores a number or text.
- A raster cell stores a number associated with a geographic area.

The difference is that a geographic raster also knows where its grid belongs on Earth.

### Raster versus vector data

There are two common ways of storing maps:

1. **Raster:** a grid of cells.
2. **Vector:** points, lines, and polygons defined by coordinates.

A geological fault is naturally a line, so it may originally exist as vector data. To store it in `existing_faults.tif`, the line was converted into a chain of marked raster cells. This conversion is called **rasterization**.

```text
Original line                 Rasterized cells

       ╱                       0 0 0 0 1
      ╱                        0 0 0 1 0
     ╱             →          0 0 1 0 0
    ╱                         0 1 0 0 0
   ╱                          1 0 0 0 0
```

Rasterization loses some geometric precision because a thin line is represented by entire 100 m squares. This is one reason a mapped fault cell should not be interpreted as a 100 m-wide physical fault.

---

## 4. What is a `.tif` file?

`.tif` and `.tiff` are two extensions for the same format: **TIFF**, or Tagged Image File Format.

A TIFF is a flexible container for rectangular image data. Compared with a normal JPEG, a TIFF can store:

- several bands or layers;
- decimal numbers;
- negative values;
- large scientific grids;
- lossless compression;
- missing-data markers;
- descriptive tags and other metadata.

### Ordinary TIFF versus GeoTIFF

An ordinary TIFF stores pixels but does not necessarily know where those pixels are located on Earth.

A **GeoTIFF** is a TIFF with geographic metadata attached. This metadata tells mapping software:

- the physical size of every cell;
- the coordinate system;
- where the upper-left corner lies;
- the geographic bounds;
- how rows and columns convert to map coordinates;
- which value represents missing data.

All three downloaded `.tif` files are GeoTIFFs.

### Why a GeoTIFF is not the same as a normal photograph

A normal color photograph usually has three bands:

```text
Band 1: red
Band 2: green
Band 3: blue
```

Values are commonly displayed as colors from 0 to 255.

A scientific GeoTIFF can instead contain values such as:

```text
-204.3
0.0267
707.24
52,844.2
NaN
```

These are scientific values, not ready-made colors. A mapping program chooses colors to represent them on a screen.

This is why opening a scientific GeoTIFF in Windows Photos may produce a black, white, blank, or strange-looking image. The file may be perfectly valid; the program simply does not understand how the scientific values should be displayed.

---

## 5. What is a band?

A **band** is one complete grid of values inside a raster.

The numerical feature GeoTIFF contains 19 bands. Imagine 19 transparent maps stacked on top of one another:

```text
Band 19: detrended elevation slope
Band 18: gravity horizontal gradient
Band 17: conductivity
...
Band 2:  reduced-to-pole magnetic data
Band 1:  magnetic anomaly
          ───────────────────────────
          All cover the same locations
```

At one row and column, there is one value from every band. The data can therefore be pictured as a three-dimensional box:

```text
3,730 rows × 3,292 columns × 19 feature values
```

Some software, including Rasterio, initially reads this as:

```text
19 bands × 3,730 rows × 3,292 columns
```

Both arrangements describe the same data. Only the order of the dimensions differs.

---

## 6. Essential GeoTIFF vocabulary

### 6.1 Width and height

The main GEMS rasters have:

```text
Width  = 3,292 columns
Height = 3,730 rows
```

The rectangular envelope therefore contains:

```text
3,292 × 3,730 = 12,279,160 grid positions
```

Not all of these positions are part of the valid survey footprint.

### 6.2 Resolution

Resolution means the ground size represented by one cell.

The three downloaded GeoTIFFs use:

```text
100 m × 100 m cells
```

A smaller cell provides more spatial detail. For example, a 1 m DEM is much more detailed than a 100 m raster.

Resolution is not the same as accuracy. A value can be stored every 100 m without being perfectly accurate at that scale.

### 6.3 Coordinate Reference System (CRS)

A **Coordinate Reference System** is a set of rules that tells software how map coordinates correspond to locations on Earth.

The GEMS rasters use:

```text
EPSG:32611
WGS 84 / UTM Zone 11N
```

In plain language:

- this is a flat projected coordinate grid appropriate for this part of the western United States;
- coordinates are measured in metres;
- an **easting** measures position in the east-west direction;
- a **northing** measures position in the north-south direction;
- the coordinates are not latitude and longitude.

`EPSG:32611` is a standard identifier that lets GIS software recognize the coordinate system unambiguously.

### 6.4 Bounds or extent

Bounds describe the outer rectangle covered by the grid:

```text
Left:   243,350 m easting
Right:  572,550 m easting
Bottom: 4,135,550 m northing
Top:    4,508,550 m northing
```

The rectangular envelope is therefore:

```text
329.2 km wide × 373 km tall
```

The real survey footprint is irregular and occupies only part of this rectangle.

### 6.5 Affine transform

The transform is the mathematical rule that connects array positions to map coordinates.

For these files, the practical interpretation is:

```text
Move one column to the right → move 100 m east
Move one row downward        → move 100 m south
```

The grid begins at the upper-left corner:

```text
Easting  = 243,350 m
Northing = 4,508,550 m
```

### 6.6 No-data value

The raster file must be rectangular even though the valid survey area is irregular. Cells outside the survey footprint therefore need a special value meaning:

> No valid observation exists here.

This is called **no-data**.

The three files use different no-data representations:

| File | No-data representation |
|---|---:|
| Numerical features | Approximately `-3.4028235 × 10^38` |
| Existing fault labels | `-1` |
| Example submission | `NaN` |

`NaN` means “Not a Number.”

No-data is not zero:

```text
0       = a real stored value, depending on the band
no-data = no usable measurement exists at this cell
```

Replacing no-data with an ordinary zero without keeping a separate validity mask can cause serious misunderstandings later.

### 6.7 Valid-data mask

A **mask** is another grid that marks which cells are usable.

Conceptually:

```text
Mask value 1 = valid survey cell
Mask value 0 = outside the valid footprint
```

The valid footprint contains 5,167,373 cells. The remaining 7,111,787 positions in the enclosing rectangle are outside the footprint or otherwise no-data.

Because every valid cell covers 0.01 km², the valid raster cells represent approximately:

```text
5,167,373 × 0.01 km² = 51,673.73 km²
```

This is a grid-derived area, not a new independent survey-area measurement.

### 6.8 Data type

A data type tells the computer how a value is stored.

| Data type | Meaning in this dataset |
|---|---|
| `float32` | A 32-bit decimal number, including negative values and fractions |
| `int8` | A small 8-bit whole number, sufficient for `-1`, `0`, and `1` |

The numerical features and example submission are `float32`. The existing-fault labels are `int8`.

### 6.9 Compression

The GeoTIFFs use **LZW** compression. LZW reduces file size without changing the stored values. It is lossless.

The raw numerical array would require approximately 933 million bytes, or about 890 MiB, before masks and other processing arrays. LZW compression reduces the on-disk file to about 399.51 MiB.

---

## 7. Exact local file inventory and integrity hashes

The following files were inspected locally on 25 September 2026.

| File | Size | SHA-256 |
|---|---:|---|
| `example_submission.tif` | 1,599,597 bytes (1.53 MiB) | `2176D08E485AA2CD2860CE8DF539DB4FAF4D76163B38A4DD8C30A40454D35CBC` |
| `existing_faults.tif` | 425,830 bytes (0.41 MiB) | `7BA308CCDC4418B31A178F4F1EF21AAA6E152E4028F2F6F64B01F7EB25AE4093` |
| `gems-geodawn-numerical-features.tif` | 418,912,844 bytes (399.51 MiB) | `4371C82E3B8339B807BDFFCF4EF59A225520FE2988D521BE208AE33743123BC5` |
| `tnm_items.json` | 145,842 bytes (0.14 MiB) | `42F02AD8D0E71D6E65498B267A391D8198A6E0783648A38A81BC05B8CE4D6849` |

A SHA-256 hash is like a highly specific digital fingerprint. If a future copy has a different hash, the file contents have changed or the copy is corrupt.

These hashes describe the local copies only; they are not claimed here as organizer-published checksums.

---

## 8. File 1: the numerical feature raster

**Path:** `gems-prize-reference-solution/data/gems-geodawn-numerical-features.tif`

This is the main collection of scientific measurements.

### 8.1 Verified metadata

| Property | Value |
|---|---|
| Format | GeoTIFF |
| Driver | GTiff |
| Width | 3,292 columns |
| Height | 3,730 rows |
| Bands | 19 |
| Data type | `float32` for every band |
| CRS | EPSG:32611 |
| Cell size | 100 m × 100 m |
| No-data | Approximately `-3.4028235 × 10^38` |
| Compression | LZW |

Every valid cell contains 19 numbers describing the same location from different geoscientific perspectives.

### 8.2 Why several types of measurements are provided

There is no single instrument that perfectly reveals geological structure everywhere.

Different measurements respond to different physical properties:

- Magnetics respond to magnetic minerals and rock boundaries.
- Gravity responds to differences in underground density.
- Geodetic strain describes broad crustal deformation.
- Earthquake-derived layers describe seismic context.
- Terrain layers describe the shape of the land surface.
- Conductivity responds to how easily electric current passes through subsurface material.
- Depth-to-basement estimates describe sediment thickness and deeper structural relief.

The bands are evidence about the landscape and subsurface. A band is not itself a declaration that a fault exists.

### 8.3 All 19 numerical bands in plain language

#### Band 1 — Magnetic anomaly (`mag_anom`)

**Metadata description:** Magnetic anomaly — deviation from the expected Earth's magnetic field.

This shows where measured magnetism differs from an expected regional background. Rocks contain different amounts and types of magnetic minerals. Changes in rock type, displaced rock bodies, or boundaries can therefore create magnetic patterns.

#### Band 2 — Reduced-to-pole magnetic data (`rtp`)

**Metadata description:** Magnetic anomaly corrected for latitude effects.

Magnetic anomalies can appear shifted away from their source because Earth's magnetic field is tilted. A reduced-to-pole transformation attempts to make the pattern easier to relate to the underground source.

It is a processed version of magnetic information, not an independent photograph.

#### Band 3 — Total magnetic intensity horizontal gradient (`tmi_hg`)

**Metadata description:** Rate of change in the horizontal direction.

This emphasizes locations where the magnetic signal changes rapidly from one place to another. It often makes boundaries and edges more visible than a raw magnetic map.

#### Band 4 — Geodetic second invariant (`geod_2ndinv`)

**Metadata description:** Measure of strain-rate tensor magnitude.

This is a combined measure of the overall strength of crustal deformation. It usually varies smoothly over broad areas rather than drawing every individual structure as a sharp line.

#### Band 5 — Isostatic gravity anomaly slope (`iso_grav_anom_slope`)

**Metadata description:** Gradient of gravity after isostatic correction.

Gravity varies slightly because underground rocks have different densities. This band describes how rapidly a corrected gravity field changes spatially.

#### Band 6 — Tilt angle or total curvature (`tc`)

**Metadata description:** Magnetic field derivative for edge detection.

This is a processed magnetic quantity intended to emphasize boundaries or edges. The metadata wording is somewhat ambiguous about whether “tilt angle” or “total curvature” is the exact authoritative name, so its derivation should be checked against the source documentation before making a precise physical claim.

#### Band 7 — Geodetic shear rate (`geod_shearrate`)

**Metadata description:** Rate of angular deformation from GPS/InSAR.

Shear means a change in shape, similar to pushing the top of a rectangle sideways while holding the bottom still. This band describes broad patterns of that kind of crustal deformation.

#### Band 8 — Geodetic dilatation rate (`geod_dilaterate`)

**Metadata description:** Rate of expansion or contraction.

Dilatation describes whether an area is expanding or contracting. Positive and negative values can represent different deformation directions, subject to the dataset's precise convention.

#### Band 9 — Total magnetic intensity vertical gradient (`tmi_vg`)

**Metadata description:** Rate of change in the vertical direction.

This is another derived magnetic layer. Vertical gradients can emphasize relatively shallow magnetic sources and spatial boundaries.

#### Band 10 — Distance to earthquake (`deq_n100a15`)

**Metadata description:** Distance to earthquake with `n=100 km radius` and `a=15° azimuth` parameters.

This is an engineered seismic-proximity feature rather than a simple list of earthquake points. The exact algorithm and output units are not fully documented in the GeoTIFF tags and must be confirmed from the authoritative source before interpreting its absolute values.

#### Band 11 — Isostatic gravity anomaly vertical gradient (`iso_grav_anom_vg`)

**Metadata description:** Vertical rate of change.

This is a derived gravity layer designed to sharpen or emphasize changes in the subsurface density field.

#### Band 12 — Detrended elevation (`det_elev`)

**Metadata description:** Topography with regional trends removed.

This is not ordinary height above sea level. A broad regional trend has been removed so local hills, basins, ridges, and depressions stand out more clearly.

An analogy is placing a table on a sloping floor. Detrending removes the overall floor slope so the local shape of the table is easier to study.

Negative detrended elevation does not necessarily mean “below sea level.” It means lower than the fitted local or regional trend used in processing.

#### Band 13 — Isostatic gravity anomaly (`iso_grav_anom`)

**Metadata description:** Gravity after compensating for topographic mass.

This is a processed gravity map intended to reveal differences associated with underground density rather than simply the gravitational effect of mountains and terrain.

#### Band 14 — Total magnetic intensity (`tmi`)

**Metadata description:** Total strength of the magnetic field.

This is another representation of measured magnetic information. It is related to, but not identical with, the magnetic anomaly and reduced-to-pole bands.

#### Band 15 — Depth to basement surface (`depth_to_base_surf`)

**Metadata description:** Thickness of sedimentary cover.

“Basement” generally refers to deeper, older, more consolidated rock beneath overlying sediments. Larger estimated values can indicate thicker sediment-filled regions; smaller values can indicate basement closer to the surface.

This is an estimate, not a direct photograph of the subsurface.

#### Band 16 — Earthquake intensity or density (`ieq_n100a15`)

**Metadata description:** Earthquake intensity or density with `n=100 km radius` and `a=15°` parameters.

This is another engineered seismic-context feature. It broadly indicates the influence or concentration of earthquake information. The exact formula and units need authoritative source documentation.

#### Band 17 — Conductivity surface (`cond_surf`)

**Metadata description:** Electrical conductivity of the subsurface.

Conductivity describes how easily electric current can pass through material. It may be influenced by:

- water or other fluids;
- clay;
- rock type;
- mineral alteration;
- temperature;
- measurement and inversion assumptions.

A high or low conductivity value does not by itself prove that a fault exists.

#### Band 18 — Isostatic gravity anomaly horizontal gradient (`iso_grav_anom_hg`)

**Metadata description:** Horizontal rate of change.

This emphasizes how rapidly the corrected gravity field changes while moving across the surface. Such changes can reveal boundaries between materials of different density.

#### Band 19 — Detrended elevation slope (`det_elev_slope`)

**Metadata description:** Gradient of elevation after detrending.

This describes how steeply the locally detrended terrain changes. It can emphasize ridges, valleys, scarps, and other terrain edges.

Many ordinary landscape features also produce strong slopes, so it should not be read as a fault map.

### 8.4 Band groups at a glance

| Evidence family | Bands |
|---|---|
| Magnetic | 1, 2, 3, 6, 9, 14 |
| Geodetic strain/deformation | 4, 7, 8 |
| Gravity | 5, 11, 13, 18 |
| Seismic/earthquake-derived | 10, 16 |
| Terrain/topography | 12, 19 |
| Subsurface depth/conductivity | 15, 17 |

### 8.5 Important limitation: units are not fully documented in the raster tags

The file includes band names, descriptions, and broad categories, but it does not provide a complete scientific data dictionary with authoritative physical units, source versions, mathematical derivations, and uncertainty for every band.

Therefore:

- broad interpretations in this document are appropriate;
- exact claims such as “Band 16 is earthquakes per square kilometre” must not be made without source documentation;
- a future data-provenance task should find the authoritative definitions and units for every band.

---

## 9. File 2: the existing-fault label raster

**Path:** `gems-prize-reference-solution/data/existing_faults.tif`

This is a one-band raster containing supplied known-fault labels.

### 9.1 Verified metadata

| Property | Value |
|---|---|
| Format | GeoTIFF |
| Width | 3,292 columns |
| Height | 3,730 rows |
| Bands | 1 |
| Data type | `int8` |
| CRS | EPSG:32611 |
| Cell size | 100 m × 100 m |
| No-data | `-1` |
| Compression | LZW |

### 9.2 Meaning of its values

| Stored value | Meaning |
|---:|---|
| `1` | A supplied known-fault trace crosses this 100 m cell |
| `0` | No supplied known-fault label is present in this valid cell |
| `-1` | The cell is outside the valid footprint/no-data |

The file contains:

| Cell type | Count |
|---|---:|
| Total positions in the rectangle | 12,279,160 |
| Valid survey cells | 5,167,373 |
| Known-fault cells (`1`) | 60,988 |
| Other valid cells (`0`) | 5,106,385 |
| Outside/no-data cells (`-1`) | 7,111,787 |

Known-fault cells are approximately 1.18% of valid cells.

### 9.3 What `1` does and does not mean

`1` means that a supplied mapped fault trace intersects that cell.

It does not mean:

- the entire 100 m × 100 m square is a physical fault;
- the physical fault is exactly 100 m wide;
- the map location is perfectly accurate;
- every supplied trace is equally certain or equally active.

The 100 m square is simply the grid unit used to represent a much thinner mapped line.

### 9.4 What `0` does and does not mean

`0` means no supplied fault label is present in that valid cell.

It does not prove that no fault exists there. A `0` may represent:

- genuine background ground;
- an unmapped fault;
- a buried or subtle fault;
- a structure absent from the supplied database;
- a mapping or alignment limitation.

This distinction is a property of the data and should be remembered even before any modelling begins.

### 9.5 Why fault-cell area should not be interpreted literally

Multiplying 60,988 cells by 0.01 km² would give 609.88 km², but this should not be reported as the physical area of faults. The labels represent rasterized lines, and their apparent width is controlled by the 100 m grid.

---

## 10. File 3: the example-submission raster

**Path:** `gems-prize-reference-solution/data/example_submission.tif`

This is not another input feature. It demonstrates the required structure of a future answer file.

Think of it as an answer-sheet template placed over exactly the same map grid.

### 10.1 Verified metadata

| Property | Value |
|---|---|
| Format | GeoTIFF |
| Width | 3,292 columns |
| Height | 3,730 rows |
| Bands | 1 |
| Data type | `float32` |
| CRS | EPSG:32611 |
| Cell size | 100 m × 100 m |
| No-data | `NaN` |
| Compression | LZW |

### 10.2 Meaning of possible values

| Stored value | Plain-language interpretation |
|---:|---|
| `0.0` | No confidence that a fault is present |
| `0.25` | Low confidence |
| `0.50` | Medium confidence |
| `0.90` | High confidence |
| `1.0` | Maximum confidence |
| `NaN` | Outside the valid footprint |

### 10.3 What this specific example contains

This example has values only at `0.0` and `1.0` inside the valid region. Its 60,988 positive cells match the known-fault cells in `existing_faults.tif` exactly.

```text
existing_faults.tif = 1
        ↓
example_submission.tif = 1.0

existing_faults.tif = 0
        ↓
example_submission.tif = 0.0

existing_faults.tif = -1 / outside footprint
        ↓
example_submission.tif = NaN
```

The dataset description states that submitting this example will score zero because supplied known faults are excluded from the relevant evaluation. For understanding the data, its main purpose is to demonstrate the correct:

- width and height;
- CRS;
- cell resolution;
- bounds and transform;
- valid-data mask;
- one-band layout;
- `float32` data type;
- `NaN` behavior outside the footprint.

It should not be treated as a twentieth feature band or an independent source of fault evidence.

---

## 11. File 4: the 1 m DEM link list

**Path:** `gems-prize-reference-solution/data/tnm_items.json`

This is a JSON text file, not a GeoTIFF.

### 11.1 What JSON means

JSON is a text format for storing structured information. It can contain lists, names, numbers, and nested records.

In this case, the file is simply a list of web addresses:

```text
[
  "https://...first-elevation-tile.tif",
  "https://...second-elevation-tile.tif",
  ...
]
```

### 11.2 Verified contents

- 894 URLs are present.
- All 894 URLs are unique.
- Every URL points to a `.tif` file.
- All links use the host `prd-tnm.s3.amazonaws.com`.
- The links refer to USGS one-metre elevation products from eight acquisition-project names.

Project counts in the link list are:

| Project name in URL | Number of links |
|---|---:|
| `NV_WestCentral_EarthMRI_2020_D20` | 590 |
| `NV_EastCentral_2021_D21` | 141 |
| `NV_NorthWestElko_2020_D20` | 73 |
| `NV_Reno_Carson_QL2_2017` | 34 |
| `CA_SierraNevada_B22` | 22 |
| `NV_Reno_Carson_QL1_2017` | 16 |
| `NV_Humboldt_2021_D21` | 15 |
| `NV_UpperHumboldt_2016` | 3 |

### 11.3 The JSON does not contain elevation values

The file contains only links. The actual elevation measurements remain in the remotely hosted GeoTIFF files.

Those 894 DEM GeoTIFFs have not been downloaded or inspected locally, so this document does not claim their exact:

- file sizes;
- CRS values;
- cell dimensions;
- no-data conventions;
- overlap patterns;
- total storage requirement;
- detailed coverage within the competition footprint.

Those facts must be checked before a bulk download.

### 11.4 What “1 m DEM” means

DEM stands for **Digital Elevation Model**: a raster in which cells store ground elevation.

A 1 m DEM has approximately 1 m × 1 m cells. This is much more detailed than the supplied 100 m numerical grid.

One 100 m competition cell covers:

```text
100 one-metre cells across
× 100 one-metre cells down
= 10,000 one-metre DEM cells
```

The 1 m products are separate map tiles, similar to floor tiles that can be assembled into a larger mosaic. They cannot be assumed to line up directly with the 100 m grid until their own metadata are inspected and an explicit alignment procedure is defined.

---

## 12. How the three GeoTIFFs connect

The files do not need a database key or location name to join them. They connect because their grids are identical.

Local inspection verified that the numerical features, fault labels, and example submission have the same:

- width and height;
- CRS;
- 100 m resolution;
- geographic bounds;
- affine transform.

The label and example-submission valid masks are also identical.

Conceptually:

```text
                              Same 100 m map cell
                                      │
                 ┌────────────────────┼────────────────────┐
                 │                    │                    │
        Numerical feature       Existing-fault      Example-submission
             GeoTIFF                GeoTIFF               GeoTIFF
                 │                    │                    │
       19 scientific values       one label          one confidence
```

At row `r` and column `c`:

```text
features[1..19, r, c]
labels[r, c]
example_submission[r, c]
```

all refer to the same geographic square.

### 12.1 A concrete cell from the downloaded data

One inspected known-fault cell is:

```text
Row:    1,252
Column: 1,293

UTM easting:  372,700 m
UTM northing: 4,383,300 m

Existing-fault label: 1
```

The 19 numerical values at exactly that location are:

| Band | Short name | Stored value |
|---:|---|---:|
| 1 | `mag_anom` | 148.0562 |
| 2 | `rtp` | 171.7457 |
| 3 | `tmi_hg` | 2.3044 |
| 4 | `geod_2ndinv` | 25.0000 |
| 5 | `iso_grav_anom_slope` | 0.1118 |
| 6 | `tc` | 18.2932 |
| 7 | `geod_shearrate` | 16.7000 |
| 8 | `geod_dilaterate` | -1.1000 |
| 9 | `tmi_vg` | 0.0267 |
| 10 | `deq_n100a15` | 551.3000 |
| 11 | `iso_grav_anom_vg` | -0.9934 |
| 12 | `det_elev` | -122.6144 |
| 13 | `iso_grav_anom` | -13.4319 |
| 14 | `tmi` | 52.5556 |
| 15 | `depth_to_base_surf` | 707.2360 |
| 16 | `ieq_n100a15` | 832.5074 |
| 17 | `cond_surf` | 3.0855 |
| 18 | `iso_grav_anom_hg` | 1.6492 |
| 19 | `det_elev_slope` | 0.2441 |

These 19 values describe the location. The separate label value says a supplied known-fault trace crosses it.

The numbers are not directly comparable across bands because the bands represent different physical quantities, transformations, and scales.

---

## 13. What the data looks like

Read-only previews were generated during inspection. They do not replace the original scientific files and do not change their values.

### 13.1 All 19 numerical bands

File:

`data_overview/numerical_features_overview.png`

This overview displays every band with an independent color scale. Dark purple/blue generally means relatively lower values within that band, while green/yellow means relatively higher values within that band.

Important: colors cannot be compared numerically across panels. Yellow in Band 1 and yellow in Band 15 do not mean the same value or physical quantity.

The plot uses each band's approximate 1st-to-99th percentile range for display. This makes broad patterns visible without allowing a few extreme values to control the entire color scale. It changes only the visualization, not the source data.

Two broad visual families can be seen:

- Smooth regional fields, especially several strain and earthquake-derived layers.
- Detailed textures and edges, especially magnetic, gravity-gradient, and terrain layers.

### 13.2 Footprint, labels, and example submission

File:

`data_overview/fault_rasters_overview.png`

This shows:

1. the valid survey footprint;
2. the supplied known-fault cells;
3. the example-submission values.

The fault map consists of many thin, disconnected or branching line segments. At full-region scale, individual 100 m cells are difficult to see because the region is hundreds of kilometres across.

### 13.3 Fault-rich close-up

File:

`data_overview/fault_rich_closeup.png`

This shows a 256 × 256-cell area:

```text
25.6 km × 25.6 km
```

Selected feature bands are shown with supplied known-fault labels outlined in red. The close-up demonstrates that:

- the same red label lines can be placed over every feature because the rasters align;
- a mapped fault may coincide with a visible edge in one band but not another;
- visually strong edges can also exist where no supplied fault is marked;
- different bands provide different types and scales of information.

### 13.4 Machine-readable inspection report

Detailed metadata and preview statistics are stored at:

`data_overview/data_inventory.json`

The read-only inspection script is:

`inspect_data.py`

The script creates previews and an inventory but does not modify the source GeoTIFFs.

---

## 14. How to view the GeoTIFFs interactively

### 14.1 Recommended tool: QGIS

QGIS is a free, open-source desktop Geographic Information System. It is much better suited to scientific GeoTIFFs than Windows Photos.

Official download page:

<https://qgis.org/download/>

The QGIS project recommends its Long Term Release when stability is preferred over the newest features. Do not rely on the version number written in an old handoff; check the official download page for the current release.

Official opening-data documentation:

<https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/opening_data.html>

### 14.2 Opening a raster in QGIS

1. Start QGIS.
2. Find the GeoTIFF in Windows Explorer.
3. Drag the `.tif` file into the main QGIS map area.
4. In the Layers panel, right-click the new layer.
5. Select **Zoom to Layer**.

Alternatively, use:

```text
Layer → Add Layer → Add Raster Layer
```

Opening or viewing a GeoTIFF does not alter it.

### 14.3 Viewing a selected numerical band

QGIS may initially display only one band or choose an unhelpful color stretch.

To display one feature band:

1. Right-click the numerical-feature layer.
2. Select **Properties**.
3. Select **Symbology**.
4. Choose **Singleband gray** or **Singleband pseudocolor**.
5. Select the desired band.
6. Ask QGIS to calculate minimum and maximum values.
7. A cumulative count cut or percentile stretch can make patterns easier to see.
8. Click **Apply**.

Bands 1, 3, 12, and 19 are useful first examples because their spatial patterns are visually apparent.

### 14.4 Displaying the fault labels over a numerical band

1. Load `gems-geodawn-numerical-features.tif`.
2. Load `existing_faults.tif`.
3. Keep the fault layer above the feature layer in the Layers panel.
4. Open the fault layer's **Properties → Symbology**.
5. Give value `1` a visible color such as red.
6. Make value `0` transparent.
7. Treat `-1` as no-data/transparent.

This creates an overlay similar to the generated close-up.

### 14.5 Looking up exact cell values

Use QGIS's **Identify Features** tool, often represented by an information icon.

Click a location on the map. For the numerical raster, QGIS can display the stored values for all 19 bands at that cell. Clicking the aligned label raster at the same location shows `-1`, `0`, or `1`.

### 14.6 Inspecting metadata in QGIS

Right-click a raster and open **Properties**, then inspect **Information** or **Source**.

Look for:

- width and height;
- band count;
- data type;
- cell or pixel size;
- CRS;
- extent/bounds;
- no-data value;
- compression;
- band descriptions.

### 14.7 Why Windows Photos is insufficient

A normal image viewer may:

- show only the first band;
- ignore map coordinates;
- apply a poor display range;
- mishandle negative or decimal values;
- make a valid scientific raster appear blank.

Use QGIS or a geospatial library for authoritative inspection.

---

## 15. Programmatic viewing and inspection

Python libraries commonly used for these files include:

- **Rasterio:** reading/writing rasters and metadata;
- **NumPy:** working with numerical arrays;
- **Matplotlib:** creating visualizations.

An isolated temporary Python environment containing Rasterio and Matplotlib was used for the read-only inspection. The competition repository itself still declares Python 3.12 or newer for its reference environment; the temporary inspection environment should not be confused with the final project environment.

Programmatic inspection should begin by checking metadata before reading or changing values:

```python
import rasterio

with rasterio.open("data/gems-geodawn-numerical-features.tif") as src:
    print(src.width, src.height)
    print(src.count)
    print(src.crs)
    print(src.res)
    print(src.bounds)
    print(src.nodata)
```

This is illustrative only. Understanding the files does not require running model code.

---

## 16. Common misunderstandings to avoid

### 16.1 “A TIFF is just a photograph”

Not here. These GeoTIFFs contain scientific numerical arrays plus geographic metadata.

### 16.2 “Every pixel is a screen pixel”

Each competition pixel represents a 100 m × 100 m ground cell. Screen pixels only display it.

### 16.3 “All 19 bands are colors”

They are separate scientific variables. Display colors are chosen later by software.

### 16.4 “A zero always means nothing is there”

No. Zero can be a legitimate measurement, a valid background label, or a zero confidence value depending on the file. No-data is separate.

### 16.5 “No-data means no fault”

No. No-data means the location is outside the valid footprint or has no usable observation.

### 16.6 “A label of zero proves no fault exists”

No. It means no supplied known-fault label is present at that cell.

### 16.7 “A label of one means the whole square is fault rock”

No. It means a mapped fault trace intersects that 100 m cell.

### 16.8 “The example submission is another feature”

No. It is an output-format example aligned with the inputs.

### 16.9 “The JSON file contains elevation”

No. It contains URLs from which separate elevation GeoTIFFs can be downloaded.

### 16.10 “A 1 m DEM can be placed directly beside the 100 m bands”

Not without alignment and scale handling. One 100 m cell covers 10,000 one-metre cells.

### 16.11 “Bright colors mean faults”

No. A bright color means a relatively high displayed value for that particular band and color scale.

### 16.12 “Values from different bands can be compared directly”

No. The bands have different quantities, ranges, derivations, and possibly different units.

### 16.13 “Resolution and accuracy are the same”

No. Resolution describes cell spacing/size. Accuracy describes closeness to the real-world quantity.

---

## 17. Safe data-handling rules

Until a formal data pipeline is designed:

1. Keep the downloaded source files unchanged.
2. Use their SHA-256 hashes to detect accidental changes.
3. Write derived files to a separate directory.
4. Never overwrite the original GeoTIFFs during experiments.
5. Preserve CRS, transform, bounds, resolution, and mask information.
6. Do not convert no-data to ordinary zero without also preserving a validity mask.
7. Do not assume units not stated in authoritative documentation.
8. Do not download all 894 DEM tiles until storage, coverage, licenses, and required subsets are audited.
9. Treat visual color stretches as display choices, not transformations of the stored source values.
10. Record how any derived raster was created.

---

## 18. Confirmed local findings

The following statements were verified directly from the downloaded files:

1. The three GeoTIFFs are all 3,292 columns × 3,730 rows.
2. They use EPSG:32611 and 100 m × 100 m cells.
3. Their geographic bounds and transforms match.
4. The numerical GeoTIFF contains 19 `float32` bands.
5. The existing-fault raster contains one `int8` band with no-data `-1`.
6. The example submission contains one `float32` band with `NaN` no-data.
7. The label and example-submission valid masks match.
8. The example submission's positive cells exactly match the supplied known-fault cells.
9. The valid footprint contains 5,167,373 cells.
10. The known-fault raster contains 60,988 positive cells, about 1.18% of valid cells.
11. The JSON contains 894 unique USGS `.tif` URLs.
12. The actual 1 m DEM tiles are not present locally.

---

## 19. Open data questions for later investigation

These questions are intentionally left open rather than answered by guesswork:

1. What are the authoritative physical units for every numerical band?
2. What exact formulas produced Bands 6, 10, and 16?
3. Which source dataset and version contributed each band?
4. What uncertainty or effective spatial resolution does each band have before being placed on the common 100 m grid?
5. Does “depth to basement surface” exactly correspond to the feature described elsewhere as a conductive-base or magnetic-source depth product, or are the public descriptions inconsistent?
6. What are the exact metadata, sizes, coverage, and overlap of the 894 DEM tiles?
7. Which DEM tiles intersect the competition footprint and are therefore actually needed?
8. Are there gaps or duplicate acquisition areas among those DEM projects?

These questions require authoritative data documentation and direct inspection of the DEM files, not assumptions based only on filenames.

---

## 20. Beginner glossary

| Term | Plain-language meaning |
|---|---|
| Raster | A map stored as a regular grid of cells |
| Cell / pixel | One square in a raster grid |
| Band | One complete grid/layer inside a raster |
| Multi-band raster | Several aligned grids stored in one file |
| TIFF | A flexible image/container format |
| GeoTIFF | A TIFF containing geographic location metadata |
| Metadata | Information describing a file and how to interpret it |
| Width | Number of grid columns |
| Height | Number of grid rows |
| Resolution | Physical ground size of one cell |
| CRS | Rules connecting coordinates to positions on Earth |
| EPSG:32611 | WGS 84 / UTM Zone 11N, the CRS used here |
| Easting | Projected coordinate measuring east-west position in metres |
| Northing | Projected coordinate measuring north-south position in metres |
| Bounds / extent | Outer coordinate rectangle of a raster |
| Transform | Mathematical rule mapping rows/columns to coordinates |
| No-data | Special marker meaning no usable value exists |
| Mask | Grid that separates valid cells from invalid/no-data cells |
| `float32` | A 32-bit decimal-number storage type |
| `int8` | A small 8-bit whole-number storage type |
| `NaN` | “Not a Number,” used here as no-data in the example submission |
| LZW | Lossless compression used to reduce GeoTIFF file size |
| Vector data | Geographic points, lines, or polygons represented by coordinates |
| Rasterization | Converting vector shapes into marked grid cells |
| DEM | Digital Elevation Model, a grid of ground-elevation values |
| Gradient | A measure of how rapidly a value changes across space |
| Anomaly | Difference from an expected or corrected background value |
| Detrended | A broad trend has been removed to emphasize local variation |
| Magnetic data | Measurements related to Earth's magnetic field and magnetic rocks |
| Gravity data | Measurements related to small gravity differences caused by density variation |
| Conductivity | How easily electric current passes through material |
| Strain | Deformation or change in shape/size of Earth's crust |
| Shear | Deformation that changes shape |
| Dilatation | Expansion or contraction |
| Basement | Older consolidated rock below younger sediments/cover |
| QGIS | Free desktop software for viewing and analysing geographic data |
| SHA-256 | A digital fingerprint used to verify file contents |

---

## 21. One-page mental model for a future session

```text
STUDY REGION
    │
    ├── represented by a common 3,292 × 3,730 rectangular grid
    │       ├── each cell is 100 m × 100 m
    │       ├── only 5,167,373 cells are valid
    │       └── all GeoTIFFs use EPSG:32611
    │
    ├── gems-geodawn-numerical-features.tif
    │       ├── 19 bands
    │       ├── float32
    │       └── scientific measurements at each valid cell
    │
    ├── existing_faults.tif
    │       ├── 1 band
    │       ├── int8
    │       ├── 1 = supplied known-fault cell
    │       ├── 0 = no supplied fault label in a valid cell
    │       └── -1 = no-data/outside footprint
    │
    ├── example_submission.tif
    │       ├── 1 band
    │       ├── float32
    │       ├── aligned answer-sheet example
    │       └── NaN outside the valid footprint
    │
    └── tnm_items.json
            ├── not a raster
            ├── contains 894 unique USGS URLs
            └── points to separate 1 m elevation GeoTIFF tiles
```

At any valid row and column:

```text
19 scientific feature values
           +
one supplied fault-label value
           +
one example/future submission value
           =
information about the same 100 m × 100 m location
```

That alignment is the central fact needed to understand the downloaded dataset.

---

## 22. Handoff notes for the next session

A new collaborator should begin with this document and the generated previews before running the reference notebook.

Recommended read-only orientation sequence:

1. Open `fault_rasters_overview.png` to understand the footprint and labels.
2. Open `numerical_features_overview.png` to see all 19 bands.
3. Open `fault_rich_closeup.png` to see how labels overlay feature patterns.
4. Use QGIS to toggle bands and click individual cells.
5. Review `data_inventory.json` for exact local metadata.
6. Confirm the source-file hashes before any derived-data workflow.
7. Resolve the open questions about band units and provenance from authoritative sources.
8. Keep modelling, metric design, normalization, patch creation, and DEM processing outside the scope of initial data understanding.

The original source data were not modified during inspection. The PNG previews and JSON inventory are derived, read-only aids stored separately under `data_overview/`.
