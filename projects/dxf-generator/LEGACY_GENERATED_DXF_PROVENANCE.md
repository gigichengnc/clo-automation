# Legacy Generated DXF Provenance Graph

## Scope and authority

This document reconstructs the lineage of Claude-era generated DXFs from surviving Python source, generated DXFs, and direct inspection of purchased `1.dxf` and `2.dxf`.

Only `1.dxf` and `2.dxf` are purchased/custom-made production references. Every other DXF discussed here is a generated or transformed artifact unless explicitly stated otherwise.

This is a **forensic provenance map**, not a declaration that generated geometry is production-correct.

## Provenance classes

- `DIRECT_COPY_FROM_1` / `DIRECT_COPY_FROM_2` — source net/cut geometry is rigidly re-oriented/translated but otherwise preserved from a purchased reference.
- `DERIVED_FROM_1` / `DERIVED_FROM_2` — purchased geometry is clipped, re-shaped, extended, re-sampled or otherwise transformed.
- `PARAMETRIC_FROM_PURCHASED_LINING_PROFILE` — new geometry is generated from rounded legacy profile numbers that align with purchased lining layer-14 geometry; the original extraction mechanism is unverified.
- `PARAMETRIC_FROM_LEGACY_MEASUREMENTS` — new geometry is generated from historical hard-coded values whose exact source path remains unresolved.
- `PARAMETRIC_FROM_SIZE_CHART` — new geometry is solved from size-chart values embedded in surviving code.
- `PARAMETRIC_ASSUMPTION` — geometry comes from explicit generator constants/formulas rather than copied production geometry.
- `GENERATED_FROM_GENERATED` — source geometry is another generated DXF.
- `FORMAT_TRANSFORM_FROM_GENERATED` — generated geometry is preserved while representation changes, for example seam allowance removed for CLO.
- `UNKNOWN_INVOCATION` — geometry definition survives, but the exact historical command/runner that produced the stored file is not preserved.

A generated artifact agreeing with its own upstream source does not count as independent evidence for a production drafting rule.

## High-level dependency graph

```text
PURCHASED 1.dxf
  ├─ lining layer-14 profile numerically matches PROF_A
  │    ratio 2.84 / front-side 569
  │    historical extraction mechanism UNVERIFIED
  │       ├─ build_five PROF_A -> 11 / 13 / 14
  │       └─ combos PROF_A -> 17 and related legacy skirt choices
  └─ direct production geometry
       └─ limited block-library derivatives

PURCHASED 2.dxf
  ├─ compatibility-selected production body blocks
  │    ├─ exact copies -> 4, 09-12, 14-21
  │    ├─ clipped/re-shaped derivatives -> 5, 12, 13, 15
  │    ├─ sleeve-cap derivatives -> 4 / 16 / 18 / 19 / 20
  │    └─ net-only library derivatives
  ├─ lining layer-14 profile numerically matches PROF_B
  │    ratio 2.27 / front-side 681
  │    historical extraction mechanism UNVERIFIED
  │       ├─ build_five PROF_B -> 09 / 10 / 12
  │       └─ combos PROF_B -> 20
  └─ other legacy values
       WAIST / NECK / ARMH remain separately audited

external size-chart values recorded in code
  ├─ build_set -> design dimensions for 4 / 5 additions
  └─ build_two -> 6 / 7, every size generated parametrically

GENERATED 4.L / 5.L
  └─ build_library.grade_file -> 4/5 full-size M-4XL

GENERATED 6 / 7
  ├─ build_library.build_marker -> 8.MARKER.6-L / 8.MARKER.7-L
  └─ nest2.run -> 8.MARKER-v2.6-L / 8.MARKER-v2.7-L

GENERATED 3-15
  └─ CLO conversion -> CLO.* net-only variants

GENERATED 11
  └─ fix11.py -> 11_corrected
```

## Mechanical replay evidence

### Direct copies from purchased `2.dxf`

Using the reconstructed legacy `parse()` / `upright()` compatibility behavior, 76 pieces labelled by surviving source code as direct `Style.blk()` / `S.blk()` copies were compared against the **stored generated DXFs re-parsed from disk** across styles 09-12 and 14-21.

After removing placement translation, maximum pointwise difference across layer-14 net and layer-1 cut contours was approximately:

```text
4.10e-12 mm
```

A separate re-check on stored styles 09 and 16 also reproduces direct-copy pieces at roughly `10^-12 mm`. This is not an in-memory comparison; the generated DXF writer retained sufficient decimal precision for the stored round-trip to remain at floating-point-noise scale.

The previously checked seven direct-copy pieces in style 4 replay to within `4.61e-7 mm`, consistent with that file's write rounding.

These tests verify rigid-copy lineage. They do **not** uniquely identify the exact internal duplicate-selection algorithm of the lost `blocks.py`; `first occurrence wins` remains the chosen compatibility behavior, not production authority.

### CLO 09-15 derivatives

The surviving `to_clo.py` entry point lists jobs for styles 3-7 only, so the historical invocation for `CLO.09` through `CLO.15` is missing. Direct file comparison nevertheless shows for every block in CLO 09-15:

- layer-14 equals the corresponding generated source style;
- CLO layer-1 equals that layer-14 net contour.

The stored CLO 09-15 files are therefore mechanically verified `FORMAT_TRANSFORM_FROM_GENERATED` artifacts with `UNKNOWN_INVOCATION` for the historical runner.

## File-level lineage

| Output | Generator | Lineage | Production independence |
| --- | --- | --- | --- |
| `0.BLOCK-LIBRARY.dxf` | `build_library.py` | net-only derivatives from purchased blocks | not independent |
| `0.MODULE-LIBRARY.dxf` | `build_library.py` | purchased derivatives + parametric modules | mixed |
| `0.MODULE-LIBRARY-v2.dxf` | `modules2.py` | sleeve-cap derivative + parametric modules | mixed |
| `3.裙片.L.dxf` | `run_gen.py` -> `skirt_gen` | hard-coded parametric skirt; historical comments reference 1/2 but no raw parse occurs | parametric legacy claim |
| `3.裙片.size-set.dxf` | `run_sizeset.py` | measurements change by size, then geometry re-solves | parametric |
| `4.恤衫連衣裙.L.dxf` | `build_set.py` | seven exact 2.dxf block copies + derived/generated components | mixed |
| `5.馬甲.L.dxf` | `build_set.py` | clipped/derived from `2.前中.L` + generated accessories | derivative/parametric |
| `4.全碼.M-4XL.dxf` | `build_library.grade_file` | generated 4.L -> coordinate warp -> SA recomputed | generated-from-generated |
| `5.全碼.M-4XL.dxf` | `build_library.grade_file` | generated 5.L -> coordinate warp -> SA recomputed | generated-from-generated |
| `6.背帶連衣裙.M-4XL.dxf` | `build_two.py` | size-chart + generator formulas | parametric |
| `7.抹胸連衣裙.M-4XL.dxf` | `build_two.py` | size-chart + generator formulas | parametric |
| `8.MARKER*` | library/nesting scripts | layout transform of generated 6/7 | generated-from-generated |
| `09`-`13` | `build_five.py` | exact 2.dxf body copies mixed with generated components | mixed |
| `14` / `15` | `s14()` / `s15()` | code lineage survives; historical invocation missing | mixed + `UNKNOWN_INVOCATION` |
| `16`-`21` | `combos.py` | exact 2.dxf body copies + derivatives + parametric modules | mixed |
| `22.學生A字裙.W60-76.dxf` | `school_skirt.py` | hard-coded algorithmic assumptions | parametric assumption only |
| `CLO.3`-`CLO.7` | `to_clo.py` | generated source -> net-only transform | format transform |
| `CLO.09`-`CLO.15` | runner not preserved | mechanically verified net-only transform | format transform + `UNKNOWN_INVOCATION` |
| `11_corrected.dxf` | `fix11.py` | generated 11 + newly reconstructed geometry | generated-from-generated / reconstruction |

## Piece-level lineage summary

### Style 3

Parametric skirt generated from hard-coded measurements. It is not a direct 1/2 copy.

### Style 4

`DIRECT_COPY_FROM_2`: front centre, both front sides, back centre, back side, collar and collar stand.

Sleeve preserves a purchased sleeve-cap lineage but builds a new sleeve body. Remaining skirt/accessory pieces are parametric.

### Style 5

Front/related upper geometry is `DERIVED_FROM_2` via clipping/reconstruction from `2.前中.L`; accessories are parametric.

### Styles 6 and 7

`PARAMETRIC_FROM_SIZE_CHART` + `PARAMETRIC_ASSUMPTION`. No purchased 1/2 geometry is parsed.

### Style 09

Ten exact `2.dxf` block copies. Front/back skirt is `PARAMETRIC_FROM_PURCHASED_LINING_PROFILE` using `PROF_B`; placket/belt/loops are generated.

### Style 10

Seven exact `2.dxf` body/sleeve copies. Tiered skirts use `PROF_B` numeric lineage plus generator-chosen tier/gathering assumptions.

### Style 11

Six exact `2.dxf` body copies. Generated collar/facing. Front/back skirt uses `PROF_A`, so its correct lineage is `PARAMETRIC_FROM_PURCHASED_LINING_PROFILE`, not shell production geometry.

### Style 12

Five exact `2.dxf` copies; front centre is clipped from purchased geometry. Skirts use `PROF_B` lining-profile numeric lineage.

### Style 13

Upper pieces are clipped/derived from `2.前中.L`; skirt uses `PROF_A` lining-profile numeric lineage.

### Style 14

Six exact `2.dxf` body copies. Inner/outer skirts use `PROF_A` lining-profile numeric lineage plus additional code multipliers. Historical runner invocation is not preserved.

### Style 15

Back centre and sleeve are exact `2.dxf` copies. Front geometry is derived from `2.前中.L`; strips are generated. Historical runner invocation is not preserved.

### Style 16

Six exact `2.dxf` body copies; lantern sleeve is a sleeve-cap derivative; skirt/waist modules are parametric.

### Style 17

Seven exact `2.dxf` body/sleeve copies; front/back skirt uses `PROF_A` lining-profile numeric lineage.

### Style 18

Six exact `2.dxf` body copies; sleeve is derived from purchased sleeve cap; fishtail geometry is parametric.

### Style 19

Six exact `2.dxf` body copies; sleeve derivative + parametric box-pleat skirt.

### Style 20

Six exact `2.dxf` body copies; sleeve derivative; front/back skirt uses `PROF_B` lining-profile numeric lineage.

### Style 21

Nine exact `2.dxf` body/collar/sleeve copies. Trousers and waistband are `PARAMETRIC_ASSUMPTION` from hard-coded formulas, not purchased trouser geometry.

### Style 22

All blocks are `PARAMETRIC_ASSUMPTION`. `school_skirt.py` does not parse purchased `1.dxf` or `2.dxf`. Style 22 is useful only as historical algorithm/regression evidence for the new school-skirt engine.

## Important contradictions / caveats

1. `build_five.py` prose says styles 09-13 are assembled from `0.BLOCK-LIBRARY`, but executable code directly calls `parse(2.dxf)`. Executable lineage wins.
2. Historical README/handover words such as `verified` record the old project's confidence; they do not make generated geometry production ground truth.
3. **Resolved:** the old contradiction that `PROF_A/B` paths were unknown has been removed. The constants numerically align with purchased lining layer-14 profiles. The original extraction/selection mechanism remains `UNVERIFIED`.
4. The current `build_five.py` entry point runs only 09-13 although `s14()` / `s15()` survive; stored 14/15 therefore have an unpreserved invocation step.
5. The current `to_clo.py` entry point lists 3-7; stored CLO 09-15 are mechanically verified transforms but their historical invocation is missing.
6. The old compatibility choice `first duplicate BLOCK occurrence wins` reproduces observed Claude-era direct-copy output, but available copied pieces do not uniquely rule out every alternative duplicate-selection heuristic. Treat it as compatibility behavior, not a recovered original source algorithm.

## Safety boundary

Generated artifacts may be used as regression fixtures, parser/adapter compatibility tests and historical behavior evidence. They must not be used as independent confirmation of a production drafting rule merely because they agree with `1.dxf`, `2.dxf`, or one another.
