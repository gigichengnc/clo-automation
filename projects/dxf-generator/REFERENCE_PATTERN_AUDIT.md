# DXF 1 / DXF 2 — Production Reference Audit

## Purpose

`1.dxf` and `2.dxf` are confirmed purchased/custom-made production patterns. They are the only independent production references in the current folder.

All other DXFs are Claude-generated or transformed artifacts and may be used for regression/provenance only, not as independent confirmation of drafting rules.

This audit distinguishes raw source facts, direct geometry, semantic interpretation and legacy numeric lineage. No observed number becomes a production default automatically.

## Evidence levels

- `HUMAN_CONFIRMED` — provenance/intent confirmed by the garment owner.
- `RAW_DXF_FACT` — source metadata/entity/material/annotation read directly from the purchased file.
- `DIRECT_GEOMETRY` — length/topology measured from the purchased contour; rigid orientation changes do not alter the measurement.
- `HIGH_CONFIDENCE_SEMANTIC` — edge role strongly supported by geometry/topology/counterpart matching, but not yet independently proven by an explicit seam map or CLO sewing check.
- `CANDIDATE_SEMANTIC` — edge role remains ambiguous.
- `RESOLVED_LEGACY_NUMERIC_LINEAGE` — a historical constant has a reproducible numeric match to purchased-source geometry, while the original extraction mechanism may remain unknown.
- `DERIVED_LEGACY` — historical value whose source path remains unresolved.
- `GENERATED_ARTIFACT` — Claude/automation output; not independent production evidence.
- `UNVERIFIED` — required fact not yet established.

## Direct source status

| Reference | Status | Direct source facts |
| --- | --- | --- |
| `1.dxf` | HUMAN_CONFIRMED + RAW_DXF_FACT | ANSI/AAMA; style `1`; sample size `L`; author `BUYI-TECH`; timestamp `2026/7/27/18/46`; metric metadata |
| `2.dxf` | HUMAN_CONFIRMED + RAW_DXF_FACT | ANSI/AAMA; style `2`; sample size `L`; author `BUYI-TECH`; timestamp `2026/7/27/18/47`; metric metadata |

The purchased files contain duplicate BLOCK names for different material instances. Lower-skirt raw order is lining first, shell second in both files. The forensic compatibility parser chooses first occurrence, but the exact duplicate-selection algorithm of the lost original `blocks.py` is not uniquely proven and must not be treated as production authority.

## Piece inventories

`1.dxf` has 14 unique production piece names:

`后中`, `前中`, `袖子`, `前侧`, `后侧`, `落肩贴`, `落肩条`, `绑带`, `飘带`, `后下裙`, `前下裙`, `口袋`, `领子`, `袖口`.

`2.dxf` has 21 unique production piece names:

`捆条`, `前中`, `右前侧`, `右边门襟实样`, `门襟贴`, `单杠`, `后侧`, `后中`, `袖子`, `袖口`, `前下裙`, `后下裙`, `左前侧`, `耳仔`, `领坐`, `领子`, `口袋面`, `口袋底`, `口袋底层`, `开袋贴`, `袋唇`.

Both are full multi-piece production garments, not isolated skirt templates.

## Lower-skirt material instances

### `1.dxf`

| Piece | Material | Qty | Annotation examples |
| --- | --- | ---: | --- |
| front lower skirt | `色丁里` lining | 1 | `拉边1/8寸` |
| front lower skirt | `弹力面布` shell | 1 | `前中`, `拉边3/16寸`, `裙长23.1/2寸` |
| back lower skirt | `色丁里` lining | 2 | `后中拉链` |
| back lower skirt | `弹力面布` shell | 2 | `后中拉链位` |

### `2.dxf`

| Piece | Material | Qty | Annotation examples |
| --- | --- | ---: | --- |
| front lower skirt | `卡其色里` lining | 1 | `拉边1/8寸`, `左侧拉链位` |
| front lower skirt | `卡其色面` shell | 1 | `拉边1/8寸`, two `口袋位`, `裙长27.1/2寸` |
| back lower skirt | `卡其色里` lining | 2 | `左侧拉链位` |
| back lower skirt | `卡其色面` shell | 2 | `左侧拉链位` |

## Source representation check

The purchased files contain no `LWPOLYLINE` entities and no non-zero VERTEX bulges. Their relevant boundaries are dense classic `POLYLINE` contours, so the measured path lengths are not hidden-bulge chord approximations.

A reproducible local audit helper is committed at:

```text
projects/dxf-generator/tools/audit_purchased_skirt_profiles.py
```

The private DXFs remain gitignored; the script accepts their paths explicitly.

## Resolved legacy `PROF_A / PROF_B` numeric lineage

Historical code contains:

```python
PROF_A = dict(ratio=2.84, length=569.0)
PROF_B = dict(ratio=2.27, length=681.0)
```

These numbers align with purchased **lining layer-14** geometry, not shell geometry.

### `1.dxf` lining

| Path | Front qty 1 | Back qty 2 |
| --- | ---: | ---: |
| hem | 985.530783 | 668.939133 each |
| waist | 425.457520 | 196.882202 each |
| side | 568.551237 | 568.390462 |

```text
full hem   = 985.530783 + 2×668.939133 = 2323.409049
full waist = 425.457520 + 2×196.882202 = 819.221924
ratio      = 2.836116785 -> 2.84
front side = 568.551237 -> 569
```

### `2.dxf` lining

| Path | Front qty 1 | Back qty 2 |
| --- | ---: | ---: |
| hem | 987.633640 | 536.395198 each |
| waist | 469.395259 | 219.296612 each |
| side | 681.172684 | 681.657061 |

```text
full hem   = 987.633640 + 2×536.395198 = 2060.424036
full waist = 469.395259 + 2×219.296612 = 907.988483
ratio      = 2.269218250 -> 2.27
front side = 681.172684 -> 681
```

This is `RESOLVED_LEGACY_NUMERIC_LINEAGE`, with two important qualifications:

1. the historical length matches the **front** lining side specifically; the back rounds differently;
2. no surviving derivation script proves how Claude originally selected these measurements. Raw BLOCK order plus first-occurrence compatibility behavior is a plausible mechanism, not established causal fact.

Generated `PROF_A/B` skirts must therefore be labelled `PARAMETRIC_FROM_PURCHASED_LINING_PROFILE`, not direct shell copies.

## Shell-versus-lining correction

The first shell/lining comparison contained one important semantic-edge error in `2.dxf`: the `723.900048 mm` back edge was treated as a side seam because of length proximity.

Re-running the surviving `edges.py` geometric-corner split shows the real shell side pair is:

```text
front side = 711.200183 mm
back side  = 711.199804 mm
back-front = -0.000379 mm
```

So `2.dxf` shell front/back side seams match essentially exactly. The earlier approximately `12.7 mm` front/back mismatch is withdrawn.

The same corrected split gives:

- front waist interface `622.009747 mm`;
- back waist group `126.900239 + 168.606055 = 295.506294 mm` per back piece;
- full shell waist `1213.022335 mm`;
- full shell hem `2847.201099 mm`;
- shell hem/waist `2.347196`.

The shell side remains about `12.7 mm` longer than the maker's `27.5 in = 698.5 mm` annotation, but that is a separate length-semantics question, not a sewing mismatch.

For `1.dxf`, shell side identity is strong: the two front radial paths and matching back side are approximately `606.586 mm`. The front is annular-sector-like, so inner-arc waist / outer-arc hem interpretation is also strong. However the mechanism reducing the large shell waist to the much smaller lining/bodice interface remains unresolved: gather, pleat, tuck or another controlled-fullness construction are all possible.

See `SHELL_LINING_SKIRT_COMPARISON.md` for the detailed corrected comparison.

## Maker skirt-length annotations

Shell annotations remain separate evidence:

- `1.dxf`: `裙长23.1/2寸` -> 23.5 in = 596.9 mm if interpreted as inches;
- `2.dxf`: `裙长27.1/2寸` -> 27.5 in = 698.5 mm.

They do not equal the lining `PROF_A/B` lengths because they refer to different material instances and likely different path/finished-length conventions. What exactly the maker means by `裙长` remains `UNVERIFIED`.

## Layer semantics

The legacy replay treats layer `14` as net geometry and layer `1` as cut geometry. This is verified as **legacy compatibility behavior**, not automatically adopted as the new engine's semantic contract.

Source layer-2 points must **not** be treated as semantic contour corners. Purchased shell blocks contain many layer-2 points, including construction/reference points offset from the boundary. Edge segmentation must use geometry/topology plus explicit construction evidence.

## Other legacy observations still quarantined

| Historical observation | Value | Status |
| --- | ---: | --- |
| `1.dxf` profile label | circular/fuller | descriptive legacy label only |
| `2.dxf` profile label | A-line | descriptive legacy label only |
| `WAIST` constant | 907 mm | unresolved; numerically close to 2.dxf full lining waist 907.988 mm, but original code comments call it block lower opening |
| neckline/collar-seat | 455 mm | legacy measurement; source path requires separate audit |
| armhole | 520–526 mm | surviving scripts disagree |

The `907` coincidence is now an explicit hypothesis to investigate, not a hidden assumption.

## Promotion rule

```text
HUMAN_CONFIRMED purchased reference
        ↓
RAW_DXF_FACT / DIRECT_GEOMETRY
        ↓
semantic identity supported independently
        ↓
cross-reference comparison
        ↓
explicit hypothesis
        ↓
parametric production rule only if supported
```

Generated artifacts never add an independent vote to this chain.

## Current safe conclusion

`1.dxf` and `2.dxf` are the only independent production references. Claude-generated derivatives are now provenance-mapped but remain non-independent.

`PROF_A/B` have strong purchased-lining numeric lineage, while their original extraction mechanism is unverified. The `2.dxf` shell front/back side seams are equal after corrected geometric edge identification, and the earlier 12.7 mm sewing-mismatch conclusion is invalid.

The new engine must preserve shell/lining identity, explicit semantic edges and safe-stop behavior whenever edge identity remains ambiguous.
