# Legacy interface constants — forensic lineage

## Scope

This note resolves or narrows the Claude-era constants:

```python
WAIST = 907.0
NECK = 455.0
ARMH = 520.0   # build_five.py
ARMH = 526.0   # combos.py / modules2.py
```

Only purchased `2.dxf` is used for direct geometry. Historical generated DXFs and prose are supporting provenance, not independent production evidence.

## Summary

| Legacy constant | Best-supported lineage | Status |
| --- | --- | --- |
| `NECK=455` | `2.领坐.L` layer-14 edge `454.929384 mm`, paired with `2.领子.L` edge `457.227468 mm` | `RESOLVED_LEGACY_NUMERIC_LINEAGE`; semantic variable name is misleading |
| `ARMH=526` | `2.袖子.L` layer-14 sleeve-cap edge `526.064330 mm` | `RESOLVED_LEGACY_NUMERIC_LINEAGE`; this is sleeve-cap length, not bodice armhole |
| `ARMH=520` | historical physical tape measurement `52 cm` / `26 cm × 2`, explicitly recorded as approximate | `HUMAN_MEASURED_LEGACY`; not recovered as a direct purchased-DXF edge total |
| `WAIST=907` | strongest numeric match is `2.dxf` lining full waist `~907.989 mm`; together with `PROF_B=2.27` it reconstructs the lining hem to within `~1.53 mm` | strong numeric hypothesis; original extraction and `block lower opening` wording remain unverified |

No value above becomes a new-engine production default from this lineage alone.

## `NECK = 455`

Direct `2.dxf` layer-14 geometric-corner segments:

```text
2.领坐.L: 447.612907, 454.929384 mm
2.领子.L: 457.227468, 503.062903 mm
```

The legacy `455` matches:

```text
454.929384 mm -> 455 mm
```

The closest stand/collar pair is:

```text
领坐 edge 454.929384
领子 edge 457.227468
difference 2.298084 mm
```

Surviving `build_library.py` labels this pair explicitly as:

```text
领座 上口 45.5 <-> 领面 下口 45.7
```

Therefore the numeric lineage of `455` is strong. But `build_five.py` calls the variable `NECK` and comments `领圈(领座上口)`. Those are not the same semantic interface:

```text
collar face <-> collar stand upper edge
!=
bodice neckline <-> collar stand lower edge
```

So `NECK=455` is a historically misnamed interface constant if interpreted as the bodice neckline circumference.

The other collar-stand edge (`447.612907 mm`) is the natural candidate for the neckline-side interface, but that semantic assignment is not promoted here without an explicit seam map / CLO verification.

## `ARMH = 526`

Direct `2.dxf` sleeve layer-14 segments are:

```text
352.238828, 526.064330, 37.390818 mm
```

The legacy `526` matches the sleeve-cap path:

```text
526.064330 mm -> 526 mm
```

This is consistent with surviving library annotations such as:

```text
袖山 52.6
```

Therefore `ARMH=526` has strong direct numeric lineage, but its historical name is misleading: it is a **sleeve-cap length**, not proof that the bodice armhole is 526 mm.

`combos.py` and `modules2.py` retain `ARMH=526`, while their sleeve generators actually extract the purchased sleeve cap geometry directly. The constant is therefore partly documentation/legacy interface state rather than an independent armhole measurement.

## `ARMH = 520`

`build_five.py` uses:

```python
ARMH = 520.0  # 袖窿
```

The later handover and `fix11.py` identify the source differently:

```text
TOTAL_ARMHOLE = 520.0  # 实物实测 26 x 2
```

and describe the physical measurement as approximate (`±2 cm`).

The surviving `edges.py` decomposition on purchased `2.dxf` gives high-confidence candidate bodice armhole components:

```text
front-centre armhole candidate = 101.265370 mm
front-side armhole candidate   = 129.297019 mm
front total                    = 230.562389 mm
back-side armhole candidate    = 265.428895 mm
one-side bodice total          = 495.991283 mm
```

This does **not** reproduce 520 mm. Meanwhile the purchased sleeve cap is `526.064330 mm`.

Therefore the current safe lineage is:

```text
520 = approximate human tape measurement / historical target
526 = direct purchased-DXF sleeve-cap measurement
```

The old claim `52.6 sleeve cap / 52 armhole = +1.2% ease` must not be treated as a precise production calculation because the `52 cm` denominator is explicitly approximate and does not match the current direct edge decomposition.

## `WAIST = 907`

`build_five.py` comments:

```python
WAIST = 907.0  # 腰口 = block 下口实测(2.dxf)
```

No surviving derivation script proves that wording.

The strongest direct numeric candidate currently found is the purchased `2.dxf` **lining lower-skirt waist**.

Using the purchased lining layer-14 geometry:

```text
front waist ~= 469.395417 mm
back waist  ~= 219.296612 mm each
full waist  ~= 469.395417 + 2*219.296612
            ~= 907.988641 mm
```

So:

```text
legacy 907 - direct lining waist ~= -0.989 mm
```

The same historical family uses `PROF_B=2.27`. Together:

```text
907 * 2.27 = 2058.890 mm
purchased 2.dxf lining full hem ~= 2060.424 mm
difference ~= 1.534 mm
```

That paired fit is much stronger evidence for a **lining waist/profile lineage** than the prose label `block lower opening` by itself.

However `907.988...` would normally round to `908`, not `907`, and no surviving source shows whether Claude truncated, used a slightly different path, or measured another interface that happened to be close. Therefore `WAIST=907` remains a strong numeric hypothesis rather than a fully resolved extraction path.

Do not describe it as confirmed bodice lower opening without a separate bodice-interface reconstruction.

## Consequences

The legacy constants should no longer be treated as one coherent set of production interfaces:

```text
WAIST 907  -> likely lining-waist/profile lineage, extraction unverified
NECK 455   -> collar-stand upper / collar-face interface
ARMH 526   -> sleeve-cap length
ARMH 520   -> approximate physical armhole measurement
```

Their names collapsed different semantic layers into generic words (`WAIST`, `NECK`, `ARMH`). The new engine must instead keep explicit interface identities, for example:

```text
collar_stand_upper_length
collar_stand_neckline_edge_length
sleeve_cap_length
bodice_armhole_length
shell_waist_interface
lining_waist_interface
```

This note does not choose production defaults or drafting formulas.

## Reproducibility

Use:

```text
python tools/audit_legacy_interface_constants.py /path/to/private/2.dxf
```

The private DXF remains gitignored.
