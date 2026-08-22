# DXF 1 / DXF 2 — Production Reference Audit

## Purpose

`1.dxf` and `2.dxf` are not synthetic examples. The garment owner has confirmed that both files are patterns for garments actually ordered from a custom clothes maker and made into real clothes.

They therefore serve as **production reference patterns** for the parametric DXF rebuild.

This audit separates direct source measurements from values that survive only through old parser scripts or derived notes. No derived value is promoted to a universal drafting rule without direct re-measurement and cross-reference comparison.

## Evidence levels

- **HUMAN_CONFIRMED** — garment provenance or intent confirmed by the garment owner.
- **DIRECT_DXF** — observed or measured directly from the original DXF in the current audit.
- **DERIVED_LEGACY** — a value recorded by an older parser/script that previously consumed the original DXF, but not independently established by the current direct pass.
- **UNVERIFIED** — required production fact that has not yet been established.

A `DERIVED_LEGACY` value may guide measurement work but must not become a production constant by itself.

## Direct source status

Both original source files were loaded directly during this audit.

| Reference | Status | Direct file facts |
| --- | --- | --- |
| `1.dxf` | HUMAN_CONFIRMED + DIRECT_DXF | ANSI/AAMA; style name `1`; sample size `L`; author `BUYI-TECH`; creation timestamp `2026/7/27/18/46`; grade rule table `1`; `UNITS: METRIC` |
| `2.dxf` | HUMAN_CONFIRMED + DIRECT_DXF | ANSI/AAMA; style name `2`; sample size `L`; author `BUYI-TECH`; creation timestamp `2026/7/27/18/47`; grade rule table `2`; `UNITS: METRIC` |

The files use Chinese piece names encoded in the legacy DXF text stream. Geometry coordinates are preserved directly from the source; no global scaling has been applied in this audit.

## Direct piece inventory

### `1.dxf`

Fourteen production piece blocks were observed:

- `后中`
- `前中`
- `袖子`
- `前侧`
- `后侧`
- `落肩贴`
- `落肩条`
- `绑带`
- `飘带`
- `后下裙`
- `前下裙`
- `口袋`
- `领子`
- `袖口`

### `2.dxf`

Twenty-one production piece blocks were observed:

- `捆条`
- `前中`
- `右前侧`
- `右边门襟实样`
- `门襟贴`
- `单杠`
- `后侧`
- `后中`
- `袖子`
- `袖口`
- `前下裙`
- `后下裙`
- `左前侧`
- `耳仔`
- `领坐`
- `领子`
- `口袋面`
- `口袋底`
- `口袋底层`
- `开袋贴`
- `袋唇`

These inventories establish that both files are full multi-piece garment production patterns, not isolated skirt templates.

## Direct lower-skirt production evidence

Each lower-skirt block contains separate major closed contours associated with shell and lining metadata. The values below are read directly from source annotations and measured directly from the stored closed layer-1 contours.

### `1.dxf`

#### Front lower skirt

| Material instance | Quantity | Direct annotation | Layer-1 closed-contour perimeter | File-coordinate bounding box |
| --- | ---: | --- | ---: | ---: |
| `色丁里` lining | 1 | `拉边1/8寸` | 2636.238 | 629.104 × 985.151 |
| `弹力面布` shell | 1 | `前中`; `拉边3/16寸`; `裙长23.1/2寸` | 4840.459 | 901.714 × 2035.359 |

#### Back lower skirt

| Material instance | Quantity | Direct annotation | Layer-1 closed-contour perimeter | File-coordinate bounding box |
| --- | ---: | --- | ---: | ---: |
| `色丁里` lining | 2 | `后中拉链` | 2099.062 | 652.189 × 644.751 |
| `弹力面布` shell | 2 | `后中拉链位` | 3125.534 | 905.442 × 1038.692 |

### `2.dxf`

#### Front lower skirt

| Material instance | Quantity | Direct annotation | Layer-1 closed-contour perimeter | File-coordinate bounding box |
| --- | ---: | --- | ---: | ---: |
| `卡其色里` lining | 1 | `拉边1/8寸`; `左侧拉链位` | 2908.156 | 737.157 × 999.095 |
| `卡其色面` shell | 1 | `拉边1/8寸`; two `口袋位`; `裙长27.1/2寸` | 3512.294 | 809.683 × 1350.054 |

#### Back lower skirt

| Material instance | Quantity | Direct annotation | Layer-1 closed-contour perimeter | File-coordinate bounding box |
| --- | ---: | --- | ---: | ---: |
| `卡其色里` lining | 2 | `左侧拉链位` | 2216.329 | 738.107 × 553.812 |
| `卡其色面` shell | 2 | `左侧拉链位` | 2552.855 | 803.735 × 732.934 |

Bounding-box dimensions above are descriptive source-coordinate facts only. They are **not** interpreted as waist, hem, or garment length because the pieces are rotated/curved in file space.

## First direct correction to legacy measurements

The production DXFs contain explicit skirt-length annotations:

- `1.dxf`: `裙长23.1/2寸` on the shell front lower-skirt piece = **23.5 in = 596.9 mm** if the annotation uses the garment maker's inch notation.
- `2.dxf`: `裙长27.1/2寸` on the shell front lower-skirt piece = **27.5 in = 698.5 mm** on the same interpretation.

Legacy scripts separately recorded:

- `1.dxf`: `569 mm`
- `2.dxf`: `681 mm`

These pairs do **not** match. Therefore `569` and `681` must no longer be described simply as the production skirt lengths. Their geometric meaning remains `UNVERIFIED` until the exact source path measured by the old scripts is reconstructed.

The direct annotations are production evidence, but they still do not by themselves prove whether the stated skirt length is finished length, seam-line length, centre length, or another maker convention. That semantic distinction remains open.

## Direct contour/layer observations

The lower-skirt production instances contain paired large closed contours on layer `1` and layer `14`. For example:

- `1.dxf` front shell: layer-1 perimeter `4840.459`; paired layer-14 perimeter `4735.002`.
- `1.dxf` back shell: layer-1 perimeter `3125.534`; paired layer-14 perimeter `3005.276`.
- `2.dxf` front shell: layer-1 perimeter `3512.294`; paired layer-14 perimeter `3421.058`.
- `2.dxf` back shell: layer-1 perimeter `2552.855`; paired layer-14 perimeter `2465.883`.

The paired contours strongly support the existing hypothesis that different production boundary semantics are encoded on these layers, but this audit does **not** yet label layer `1` as cut line or layer `14` as net/seam line until the layer convention is explicitly verified against the source standard/house convention.

Other directly observed layers include `2`, `3`, `4`, `7`, `8`, `13` and `14`, depending on piece. Their semantic meanings remain separate from the fact that they exist.

## Direct construction annotations already established

The source files also expose construction information that can later constrain semantic-edge mapping:

- `1.dxf` lower skirt uses a **centre-back zipper** (`后中拉链` / `后中拉链位`).
- `2.dxf` lower skirt marks a **left-side zipper position** (`左侧拉链位`).
- `2.dxf` front lower skirt marks two pocket positions (`口袋位`).
- Shell and lining quantities differ by piece and are explicitly stored in the DXF metadata.

These are production facts, not inferred drafting rules.

## Legacy observations retained but quarantined

The following remain `DERIVED_LEGACY` until their measurement paths are reconstructed from the originals:

### `1.dxf`

| Observation | Value | Evidence |
| --- | ---: | --- |
| legacy profile classification | circular / fuller skirt | DERIVED_LEGACY |
| legacy skirt-length value | 569 mm | DERIVED_LEGACY; conflicts with direct `23.5 in` annotation |
| hem-to-waist ratio | 2.84 | DERIVED_LEGACY; exact path definition unknown |

### `2.dxf`

| Observation | Value | Evidence |
| --- | ---: | --- |
| legacy profile classification | A-line | DERIVED_LEGACY |
| legacy skirt-length value | 681 mm | DERIVED_LEGACY; conflicts with direct `27.5 in` annotation |
| hem-to-waist ratio | 2.27 | DERIVED_LEGACY; exact path definition unknown |
| bodice/block lower opening | 907 mm | DERIVED_LEGACY; semantic path still to reconstruct |
| neckline / collar-seat reference | 455 mm | DERIVED_LEGACY |
| armhole reference | 520–526 mm | DERIVED_LEGACY; surviving scripts disagree |

## Next direct measurement pass

Measure facts first and interpret later:

1. verify the AAMA/house layer semantics from source evidence
2. identify shell versus lining contour pairs mechanically for every piece
3. recover semantic edges on the lower-skirt shell pieces: waist, hem, centre and side seams
4. measure front/back side seams separately
5. measure waist and hem seam paths rather than relying on bounding boxes
6. locate any dart geometry and distinguish internal lines from outline-integrated darts
7. measure layer-1 versus layer-14 edge-by-edge offsets rather than using total-perimeter differences
8. reconstruct exactly what the legacy `569/681` and hem/waist ratios measured
9. compare the two custom-made references before promoting any rule

## Promotion rule

No production rule should be inferred from a single surviving or direct number.

```text
HUMAN_CONFIRMED reference
        ↓
DIRECT_DXF measurement
        ↓
cross-reference comparison
        ↓
explicit hypothesis
        ↓
parametric rule only if supported
```

Examples:

- matching dart intakes in two files do not automatically establish a universal fixed dart intake;
- matching contour offsets do not establish one seam allowance for every semantic edge;
- a front/back side-seam mismatch must be preserved and reported before deciding whether it is intentional, construction-related, grading-related or erroneous.

## Current safe conclusion

`1.dxf` and `2.dxf` are now directly accessible **production reference sources**. The first direct pass confirms their piece inventories, production metadata, material/quantity instances, lower-skirt construction annotations and major contour geometry. It also reveals that the old `569/681 mm` values conflict with the garment-maker skirt-length annotations and therefore cannot be treated as production skirt-length truth without further reconstruction.
