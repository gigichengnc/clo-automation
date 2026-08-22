# Legacy skirt profile measurement lineage

## Question

What did the Claude-era constants below actually measure?

```python
PROF_A = dict(ratio=2.84, length=569.0)  # attributed to 1.dxf
PROF_B = dict(ratio=2.27, length=681.0)  # attributed to 2.dxf
```

## Conclusion

The constants have real lineage to the purchased production DXFs, but they describe the **lining layer-14 net/seam contours**, not the shell pieces.

This happened because the lost legacy `blocks.py` parser used **first duplicate BLOCK occurrence wins**. For the lower-skirt piece names in both purchased files, the first occurrence is the lining instance. Later shell instances with the same BLOCK name were therefore invisible to callers using the mapping returned by `parse()`.

The old constants must therefore be described as **lining-profile measurements**. They are not shell skirt-length or shell hem-ratio truth.

## Direct source reconstruction

Measurements below are from the purchased source DXFs after applying the forensically reconstructed legacy upright transform. Semantic boundaries are split at source layer-2 turn points on the layer-14 contour.

### Purchased `1.dxf` — lining (`色丁里`)

| Semantic path | Front lining, qty 1 | Back lining, qty 2 |
| --- | ---: | ---: |
| hem | 985.530783 mm | 668.939133 mm per piece |
| waist | 425.457520 mm | 196.882202 mm per piece |
| side seam | 568.551237 mm | 568.390462 mm |

Full lining hem:

```text
985.530783 + 2 × 668.939133 = 2323.409050 mm
```

Full lining waist:

```text
425.457520 + 2 × 196.882202 = 819.221924 mm
```

Therefore:

```text
2323.409050 / 819.221924 = 2.836116784 → 2.84
```

The legacy `569` matches the **front lining side seam** rounded to the nearest millimetre:

```text
568.551237 mm → 569 mm
```

The back lining side seam is independently very close at `568.390462 mm`.

### Purchased `2.dxf` — lining (`卡其色里`)

| Semantic path | Front lining, qty 1 | Back lining, qty 2 |
| --- | ---: | ---: |
| hem | 987.633640 mm | 536.395198 mm per piece |
| waist | 469.395259 mm | 219.296612 mm per piece |
| side seam | 681.172684 mm | 681.657061 mm |

Full lining hem:

```text
987.633640 + 2 × 536.395198 = 2060.424037 mm
```

Full lining waist:

```text
469.395259 + 2 × 219.296612 = 907.988483 mm
```

Therefore:

```text
2060.424037 / 907.988483 = 2.269218251 → 2.27
```

The legacy `681` matches the **front lining side seam** rounded to the nearest millimetre:

```text
681.172684 mm → 681 mm
```

The back lining side seam is independently close at `681.657061 mm`.

## Why the old values disagreed with shell annotations

The purchased shell front lower-skirt pieces contain explicit annotations:

- `1.dxf`: `裙长23.1/2寸` — 23.5 in = 596.9 mm if interpreted as inches;
- `2.dxf`: `裙长27.1/2寸` — 27.5 in = 698.5 mm on the same interpretation.

Those annotations belong to the **shell** pieces. The legacy values `569` / `681` came from the **lining** net contours. The apparent contradiction therefore came from comparing different material instances and different length semantics.

This resolves the provenance mismatch; it does **not** prove that either value is the universal definition of finished garment length.

## Consequences for generated styles

`build_five.py` and `combos.py` use `PROF_A/B` as inputs to a new radial `build_panel()` geometry. Consequently downstream generated skirts inherit the silhouette proportions of the purchased **lining**, then redraw them with a different mathematical construction.

Use the provenance label:

```text
PARAMETRIC_FROM_PURCHASED_LINING_PROFILE
```

not:

```text
DIRECT_COPY_FROM_1_OR_2
```

and not:

```text
SHELL_PRODUCTION_PROFILE
```

Examples affected include the `PROF_A/B` skirts in styles 09–14, 17 and 20, plus related legacy module skirts.

## Safety boundary

This finding establishes measurement provenance only.

It does not establish that:

- lining and shell should share the same hem/waist ratio;
- lining side-seam length should define requested garment length;
- `2.84` or `2.27` should become production defaults;
- the radial `build_panel()` reconstruction matches the purchased production drafting method;
- shell annotations or lining geometry are universally preferable.

For the new engine, shell and lining must remain explicit separate semantic instances and no duplicate-name parser is allowed to silently choose one.
