# Legacy skirt profile measurement lineage

## Question

What do the Claude-era constants below line up with in the purchased production DXFs?

```python
PROF_A = dict(ratio=2.84, length=569.0)  # attributed to 1.dxf
PROF_B = dict(ratio=2.27, length=681.0)  # attributed to 2.dxf
```

## Corrected conclusion after adversarial review

The numeric values align tightly with the **lining layer-14 profile geometry**, not with the shell geometry.

That numeric lineage is now reproducible from the private purchased DXFs with `tools/audit_purchased_skirt_profiles.py` plus the semantic path reconstruction documented below.

What is **not** proven is the exact historical mechanism by which Claude originally selected those values. The lost `blocks.py` compatibility reconstruction uses `first duplicate BLOCK occurrence wins`, and the raw purchased files do place lining before shell for the lower-skirt BLOCK names. That mechanism is a plausible explanation, but no surviving script shows the original derivation of `PROF_A/B`, so it must not be stated as causal fact.

Use this distinction:

```text
RESOLVED_LEGACY_NUMERIC_LINEAGE
historical selection mechanism = UNVERIFIED
```

not:

```text
original parser definitely measured these values automatically
```

## Raw BLOCK order

The purchased files contain duplicate lower-skirt BLOCK names.

`1.dxf`:

- first `1.前下裙.L` = `色丁里` lining;
- second `1.前下裙.L` = `弹力面布` shell;
- first `1.后下裙.L` = `色丁里` lining;
- second `1.后下裙.L` = `弹力面布` shell.

`2.dxf`:

- first `2.前下裙.L` = `卡其色里` lining;
- second `2.前下裙.L` = `卡其色面` shell;
- first `2.后下裙.L` = `卡其色里` lining;
- second `2.后下裙.L` = `卡其色面` shell.

This makes first-occurrence selection sufficient to produce the lining instances, but not uniquely proven as the original algorithm.

## `PROF_A` numeric reconstruction — purchased `1.dxf` lining

High-confidence lining paths:

| Path | Front lining, qty 1 | Back lining, qty 2 |
| --- | ---: | ---: |
| hem | 985.530783 mm | 668.939133 mm per piece |
| waist | 425.457520 mm | 196.882202 mm per piece |
| side | 568.551237 mm | 568.390462 mm |

Full lining hem:

```text
985.530783 + 2 × 668.939133 = 2323.409049 mm
```

Full lining waist:

```text
425.457520 + 2 × 196.882202 = 819.221924 mm
```

Therefore:

```text
2323.409049 / 819.221924 = 2.836116785 -> 2.84
```

Historical `length=569` matches the **front lining side** rounded to the nearest millimetre:

```text
568.551237 -> 569
```

Important limitation: the back lining side is `568.390462`, which rounds to `568`, not `569`. Therefore the evidence supports "the historical value matches the front lining side"; it does **not** prove that the original derivation used an average, generic side-seam definition, or any particular automatic rule.

## `PROF_B` numeric reconstruction — purchased `2.dxf` lining

| Path | Front lining, qty 1 | Back lining, qty 2 |
| --- | ---: | ---: |
| hem | 987.633640 mm | 536.395198 mm per piece |
| waist | 469.395259 mm | 219.296612 mm per piece |
| side | 681.172684 mm | 681.657061 mm |

Full lining hem:

```text
987.633640 + 2 × 536.395198 = 2060.424036 mm
```

Full lining waist:

```text
469.395259 + 2 × 219.296612 = 907.988483 mm
```

Therefore:

```text
2060.424036 / 907.988483 = 2.269218250 -> 2.27
```

Historical `length=681` matches the **front lining side** rounded to the nearest millimetre:

```text
681.172684 -> 681
```

The back lining side is `681.657061`, which rounds to `682`. Again, only the front-side numeric match is established.

## Net-versus-cut check

The purchased lower-skirt boundaries are classic dense `POLYLINE` entities with no non-zero VERTEX bulges and no `LWPOLYLINE` entities.

The corresponding layer-1 cut-boundary side candidates do **not** reproduce `569 / 681` in the same way; for example the `2.dxf` lining cut geometry contains side-length candidates around `699–711 mm`, not `681 mm`. This strengthens the conclusion that the historical constants align with layer-14 net geometry rather than layer-1 cut geometry.

## Why shell annotations differ

The shell front lower-skirt pieces contain maker annotations:

- `1.dxf`: `裙长23.1/2寸` = 23.5 in = 596.9 mm if interpreted as inches;
- `2.dxf`: `裙长27.1/2寸` = 27.5 in = 698.5 mm on the same interpretation.

Those annotations belong to shell pieces. `569 / 681` align with lining layer-14 front-side paths. The values therefore describe different material instances and likely different length semantics.

For `2.dxf`, the corrected shell side seam is approximately `711.200 mm`, while the 27.5 in annotation is `698.5 mm`, leaving a separate approximately `12.7 mm` semantic difference. That is **not** a front/back side-seam mismatch; see `SHELL_LINING_SKIRT_COMPARISON.md`.

## Consequences for generated styles

`build_five.py` and `combos.py` feed `PROF_A/B` into a new radial `build_panel()` construction. The generated skirts therefore inherit rounded numeric profile inputs that align with purchased lining geometry, then redraw a different mathematical shape.

Use:

```text
PARAMETRIC_FROM_PURCHASED_LINING_PROFILE
```

with the qualification:

```text
numeric lineage resolved; original extraction mechanism unverified
```

Do not use:

```text
DIRECT_COPY_FROM_1_OR_2
SHELL_PRODUCTION_PROFILE
```

Affected generated styles include the `PROF_A/B` skirts in 09–14, 17 and 20, plus related module/legacy skirt constructions.

## Safety boundary

This finding does not establish that:

- lining and shell should share one ratio;
- lining front-side length defines requested garment length;
- `2.84`, `2.27`, `569` or `681` are production defaults;
- the radial `build_panel()` method matches the purchased maker's drafting method;
- the lost `blocks.py` definitely caused the values to be selected.

For the new engine, shell and lining remain explicit separate instances and duplicate piece names must never be silently collapsed.
