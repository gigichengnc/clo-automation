# Legacy Generated DXF Provenance Graph

## Scope and authority

This document reconstructs the lineage of Claude-era generated DXFs from the surviving Python source, the generated DXFs themselves, and the directly inspected purchased references `1.dxf` and `2.dxf`.

Only `1.dxf` and `2.dxf` are purchased/custom-made production references. Every other DXF discussed here is a generated or transformed artifact unless explicitly stated otherwise.

This is a **forensic provenance map**, not a declaration that generated geometry is production-correct.

## Provenance classes

- `DIRECT_COPY_FROM_1` / `DIRECT_COPY_FROM_2` — source net/cut geometry is rigidly re-oriented/translated but otherwise preserved from a purchased reference.
- `DERIVED_FROM_1` / `DERIVED_FROM_2` — source production geometry is clipped, re-shaped, extended, re-sampled, offset again, or otherwise transformed.
- `PARAMETRIC_FROM_LEGACY_MEASUREMENTS` — new geometry is generated from hard-coded measurements/ratios that old code attributes to `1.dxf` / `2.dxf`; this is **not** independent production evidence.
- `PARAMETRIC_FROM_SIZE_CHART` — new geometry is solved from the size-chart values embedded in the surviving generator.
- `PARAMETRIC_ASSUMPTION` — geometry comes from explicit constants/formulas chosen by the generator rather than copied production geometry.
- `GENERATED_FROM_GENERATED` — source geometry is another generated DXF.
- `FORMAT_TRANSFORM_FROM_GENERATED` — generated geometry is preserved while representation changes, for example seam allowance removed for CLO.
- `UNKNOWN_INVOCATION` — geometry definition survives, but the exact historical command/runner that produced the stored file is not present.

A generated artifact agreeing with its own upstream source does not count as independent evidence for a production drafting rule.

## High-level dependency graph

```text
PURCHASED 1.dxf
  ├─ legacy-measured/claimed skirt constants and proportions
  │    ├─ skirt_gen / run_gen / run_sizeset -> 3.*
  │    ├─ build_five PROF_A -> 11 / 13 / 14
  │    └─ combos PROF_A -> 17 and related skirt choices
  └─ direct net geometry
       └─ 0.BLOCK-LIBRARY: one elastic-front block only

PURCHASED 2.dxf
  ├─ lost blocks.py parse/upright behavior (forensically reconstructed)
  │    ├─ exact production-piece copies -> 4, 09-12, 14-21
  │    ├─ clipped/re-shaped derivatives -> 5, 12, 13, 15
  │    ├─ sleeve-cap derivatives -> 4 and several module/combo sleeves
  │    └─ net-only copies -> 0.BLOCK-LIBRARY / parts of 0.MODULE-LIBRARY
  └─ legacy-measured/claimed constants
       ├─ WAIST / NECK / ARMH
       └─ PROF_B skirt ratio/length

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
  └─ fix11.py -> 11_corrected (mixed copied + newly reconstructed geometry)
```

## Mechanical replay evidence

### Direct copies from purchased `2.dxf`

Using the reconstructed legacy `parse()` / `upright()` behavior, 76 pieces labelled by surviving source code as direct `Style.blk()` / `S.blk()` copies were compared against the stored generated DXFs across styles 09-12 and 14-21.

After removing the generated placement translation, the maximum pointwise difference across both layer-14 net and layer-1 cut contours was:

```text
4.10e-12 mm
```

This verifies that those 76 pieces are true rigid copies of the selected first-occurrence `2.dxf` blocks, not redrawn approximations.

The previously verified seven direct-copy pieces in style 4 replay to within `4.61e-7 mm`, consistent with DXF write rounding.

### CLO 09-15 derivatives

The surviving `to_clo.py` only lists jobs for styles 3-7, so the historical invocation/source for `CLO.09` through `CLO.15` is missing. However, direct file comparison shows for every block in CLO 09-15:

- layer-14 is exactly identical to the corresponding generated source style;
- CLO layer-1 is exactly equal to that layer-14 net contour.

Therefore the stored CLO 09-15 files are mechanically verified `FORMAT_TRANSFORM_FROM_GENERATED` artifacts even though their exact historical runner is not preserved.

## File-level lineage

| Output | Generator | Lineage | Production independence |
| --- | --- | --- | --- |
| `0.BLOCK-LIBRARY.dxf` | `build_library.py` | 10 net-only blocks from `2.dxf` + 1 net-only block from `1.dxf`; cut set equal to net | derivative library, not independent |
| `0.MODULE-LIBRARY.dxf` | `build_library.py` | direct 2.dxf collar/sleeve modules + sleeve derivatives + parametric bands/skirts/pockets | mixed derivative/parametric |
| `0.MODULE-LIBRARY-v2.dxf` | `modules2.py` | 2.dxf sleeve-cap derivative + parametric collar/skirt/waist/trouser modules | mixed derivative/parametric |
| `3.裙片.L.dxf` | `run_gen.py` -> `skirt_gen.make_skirt_dxf` | hard-coded skirt measurements; comments claim 1.dxf house-rule lineage but no raw 1/2 parse occurs | parametric legacy claim only |
| `3.裙片.size-set.dxf` | `run_sizeset.py` -> `make_size_set` | base hard-coded dimensions + grade increments; measurements change by size, then geometry is re-solved per size | parametric; not direct production |
| `4.恤衫連衣裙.L.dxf` | `build_set.py` | seven exact 2.dxf block copies; sleeve derived from 2.dxf sleeve cap; remaining pieces parametric | mixed |
| `5.馬甲.L.dxf` | `build_set.py` | upper pieces clipped/derived from 2.dxf front-centre block; accessories parametric | derived/parametric |
| `4.全碼.M-4XL.dxf` | `build_library.grade_file` | generated 4.L -> coordinate warp by size -> SA recomputed | generated-from-generated |
| `5.全碼.M-4XL.dxf` | `build_library.grade_file` | generated 5.L -> coordinate warp by size -> SA recomputed | generated-from-generated |
| `6.背帶連衣裙.M-4XL.dxf` | `build_two.py` | size-chart-driven + explicit generator constants; no raw 1/2 geometry | parametric |
| `7.抹胸連衣裙.M-4XL.dxf` | `build_two.py` | size-chart-driven + explicit generator constants; no raw 1/2 geometry | parametric |
| `8.MARKER.6-L.dxf` / `.7-L` | `build_library.build_marker` | layout transform of generated 6/7 size L | generated-from-generated |
| `8.MARKER-v2.6-L.dxf` / `.7-L` | `nest2.py` | alternate nesting/layout transform of generated 6/7 size L | generated-from-generated |
| `09`-`13` | `build_five.py` | exact 2.dxf block copies mixed with derived/parametric components | mixed |
| `14` / `15` | functions `s14()` / `s15()` in `build_five.py` | code-defined lineage recoverable, but current `__main__` does not invoke these functions | mixed + `UNKNOWN_INVOCATION` |
| `16`-`21` | `combos.py` | exact 2.dxf body blocks plus 2.dxf-derived sleeve caps and parametric modules | mixed |
| `22.學生A字裙.W60-76.dxf` | `school_skirt.py` | entirely algorithmic from hard-coded waist/ease/hip-add/depth/length/flare/dart/waistband constants | parametric assumption only |
| `CLO.3`-`CLO.7` | `to_clo.py` | generated source -> preserve net -> set cut equal to net | format transform |
| `CLO.09`-`CLO.15` | historical converter invocation not preserved | mechanically verified exact net-only transform of generated 09-15 | format transform + `UNKNOWN_INVOCATION` |
| `11_corrected.dxf` | `fix11.py` | generated 11 + newly drafted back/yoke/facing + copied 11 front/skirt/belt | generated-from-generated / reconstruction |

## Piece-level lineage — styles 3-22

### Style 3 — parametric skirt

`3.前下裙.*`, `3.后下裙.*`

- `PARAMETRIC_FROM_LEGACY_MEASUREMENTS`
- generated by `skirt_gen.build_panel()` from explicit waist/hem/length allocations;
- no call to `parse(1.dxf)` or `parse(2.dxf)` in either runner;
- comments attribute the parameter family to the purchased references, but that attribution is a legacy claim, not direct geometry lineage.

The size-set runner changes waist by 25.4 mm, hem by 76.2 mm, and length by 12.7 mm per step relative to L. It then calls the geometric solver again for every size. This is **measurement grading followed by independent geometric re-solve**, not a coordinate transform of the L pattern.

### Style 4 — shirt dress

`DIRECT_COPY_FROM_2`:

- `4.前中.L`
- `4.左前侧.L`
- `4.右前侧.L`
- `4.后中.L`
- `4.后侧.L`
- `4.领子.L`
- `4.领坐.L`

`DERIVED_FROM_2` + `PARAMETRIC_ASSUMPTION`:

- `4.袖子.L` — preserves the extracted `2.袖子.L` sleeve cap, then constructs a new 510 mm sleeve body/hem.

`PARAMETRIC_ASSUMPTION`:

- `4.袖口条.L`
- `4.袖口荷叶边.L`
- `4.一层裙前.L`
- `4.一层裙后.L`
- `4.二层裙前.L`
- `4.二层裙后.L`
- `4.门襟贴.L`

The script docstring also records external style-image/size-chart dimensions. Those dimensions are input evidence for the generated design, not production validation of the new pieces.

### Style 5 — vest

`DERIVED_FROM_2`:

- `5.前片.L` — clipped from `2.前中.L` with new V/armhole/hem decisions;
- `5.前贴边.L` — generated from the derived front piece bounds;
- `5.后片.L` — also derived from the `2.前中.L` geometry rather than a purchased back block.

`PARAMETRIC_ASSUMPTION`:

- `5.腰扣带.L`
- `5.绑带.L`
- `5.耳仔.L`

### Styles 6 and 7 — size-chart parametric garments

All pieces are `PARAMETRIC_FROM_SIZE_CHART` + `PARAMETRIC_ASSUMPTION`.

No raw purchased `1.dxf` / `2.dxf` geometry is parsed by `build_two.py`.

Each M-4XL size is generated from the code's size-chart values and formulas rather than transformed from a base L coordinate set.

### Style 09 — black shirt dress

`DIRECT_COPY_FROM_2` (10 pieces): front centre, both front sides, back yoke, back centre, back side, collar, collar stand, sleeve, cuff.

Generated: front/back skirt from `PROF_B`; placket facing; belt; loops.

### Style 10 — drawstring long dress

`DIRECT_COPY_FROM_2` (7 pieces): six body pieces + sleeve geometry. The sleeve is renamed/annotated as a short puff sleeve but its geometry is copied unchanged.

Generated: V-neck facing, cuff strip, drawstring channel, drawstring, two skirt tiers. The skirt tiers use `PROF_B` and generator-chosen gathering/split constants.

### Style 11 — fitted mini dress

`DIRECT_COPY_FROM_2` (6 pieces): the six-piece body set.

Generated: collar band, armhole facing, front/back skirt using `PROF_A`, narrow belt.

The later `11_corrected` file is a second-generation derivative of this generated style, not purchased production geometry.

### Style 12 — off-shoulder button dress

`DIRECT_COPY_FROM_2` (5 pieces): back centre, back side, both front sides, sleeve.

`DERIVED_FROM_2`: front centre is clipped 55 mm below the original top line.

Generated: large collar, collar facing, front/back skirt using `PROF_B`, placket facing.

### Style 13 — pinafore

`DERIVED_FROM_2`:

- front upper body — clipped from half of `2.前中.L` using a new deep-V/high-waist construction;
- back upper body — also clipped from the same purchased front-centre source, not from a purchased back piece.

Generated: skirt using `PROF_A`, hem trim, bow-tie straps, facing.

### Style 14 — lace formal dress

`DIRECT_COPY_FROM_2` (6 pieces): six-piece body set.

Generated: V-neck facing, cape sleeve, inner/outer front/back skirts, decorative waist strip. Skirts use `PROF_A`, with outer-layer length/hem multipliers chosen in code.

Historical generation invocation is not preserved in the current script entry point: `s14()` survives, but `build_five.py`'s `__main__` only calls `s09`-`s13`.

### Style 15 — faux-layer T-shirt

`DIRECT_COPY_FROM_2`: back centre and sleeve.

`DERIVED_FROM_2`: front geometry originates from `2.前中.L` but is passed through the generator's densify/reorientation/new-offset path, so it is not classified as an exact production copy.

Generated: neckline strip, cuff strips, hem strip.

As with style 14, `s15()` survives but is not called by the current `build_five.py` entry point.

### Style 16 — sailor-collar lantern-sleeve dress

`DIRECT_COPY_FROM_2` (6 pieces): six-piece body set.

`DERIVED_FROM_2`: lantern sleeve preserves the extracted purchased sleeve cap and generates a new sleeve body.

Generated: sailor collar, cuff strip, pleated skirt, waistband.

### Style 17 — Peter Pan collar circular-skirt dress

`DIRECT_COPY_FROM_2` (7 pieces): six-piece body set + sleeve.

Generated: collar, front/back skirt using `PROF_A`, belt.

### Style 18 — ruffle collar / leg-of-mutton sleeve / fishtail

`DIRECT_COPY_FROM_2` (6 pieces): six-piece body set.

`DERIVED_FROM_2`: sleeve preserves the purchased sleeve cap and generates new lower geometry.

Generated: ruffle collar, cuff strip, fishtail upper and lower skirt sections.

### Style 19 — dropped-shoulder box-pleat dress

`DIRECT_COPY_FROM_2` (6 pieces): six-piece body set.

`DERIVED_FROM_2`: generated sleeve uses the purchased sleeve cap.

Generated: neckline facing, box-pleat skirt, waistband.

### Style 20 — layered-collar high-waist long dress

`DIRECT_COPY_FROM_2` (6 pieces): six-piece body set.

`DERIVED_FROM_2`: long sleeve uses the purchased sleeve cap.

Generated: two collar layers, high-waist band, front/back skirt using `PROF_B`.

### Style 21 — shirt-top jumpsuit

`DIRECT_COPY_FROM_2` (9 pieces): six-piece body set + collar + collar stand + sleeve.

`PARAMETRIC_ASSUMPTION`: front trouser, back trouser, waistband. The trouser block uses hard-coded waist/hip-add/rise/inseam/hem/crotch-extension formulas and is not sourced from a purchased trouser pattern.

### Style 22 — school A-line skirt

All 15 blocks (front, back and waistband across W60-W76) are `PARAMETRIC_ASSUMPTION`.

`school_skirt.py` uses hard-coded constants including waist ease, synthetic hip addition, hip depth, skirt length, flare, dart count/intake/length, waistband cut height and hem shaping. It does not parse purchased `1.dxf` or `2.dxf`.

Therefore style 22 is useful as a historical algorithm/regression artifact but provides **zero independent production evidence** for the new school-skirt engine.

## Important contradictions between prose and executable lineage

1. `build_five.py` says styles 09-13 are assembled from `0.BLOCK-LIBRARY`, but the executable code directly does `parse(2.dxf)` and copies from that source. For provenance, the executable path wins.
2. README/handover claims such as "verified" describe the historical project's confidence state; they do not override direct source inspection or make generated pieces production ground truth.
3. `PROF_A` / `PROF_B` are hard-coded legacy measurements attributed to purchased files. Because their exact original measurement paths are still under reconstruction, downstream skirts remain parametric derivatives, not direct copies.
4. The current `build_five.py` entry point generates only 09-13 even though definitions for 14 and 15 survive later in the file. The stored 14/15 outputs therefore have an unpreserved invocation step.
5. The current `to_clo.py` entry point lists only styles 3-7. Stored CLO 09-15 outputs are exact net-only transforms by direct file comparison, but their historical converter invocation is missing.

## Safety boundary

Generated artifacts may be used as regression fixtures, parser/adapter compatibility tests, and historical behavior evidence. They must not be used as independent confirmation of a production drafting rule merely because they agree with `1.dxf`, `2.dxf`, or one another.
