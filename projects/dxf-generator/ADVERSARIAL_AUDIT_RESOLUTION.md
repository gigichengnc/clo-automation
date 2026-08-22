# Adversarial audit resolution

This note records the disposition of the external adversarial review performed after commit `3adf7e8`.

The reviewer did not have access to private `1.dxf` / `2.dxf`, so every important finding was re-checked against the local purchased originals and surviving Claude-era code before acceptance.

## BLOCKER

### B1 — stale `PROF_A/B` provenance contradiction

**Disposition: ACCEPTED.**

`LEGACY_GENERATED_DXF_PROVENANCE.md` still said the exact `PROF_A/B` paths were unknown while newer documents described them as lining-profile numeric lineage.

Action:

- provenance graph rewritten;
- affected generated skirts now use `PARAMETRIC_FROM_PURCHASED_LINING_PROFILE`;
- original extraction mechanism remains explicitly `UNVERIFIED`.

## HIGH

### H1 — lining numeric lineage is strong; causal parser story was too strong

**Disposition: PARTIALLY ACCEPTED.**

Raw purchased source confirms lower-skirt BLOCK order is lining first / shell second in both `1.dxf` and `2.dxf`.

The published ratios and lengths re-measure as:

```text
1.dxf lining: 2323.409049 / 819.221924 = 2.836116785 -> 2.84
front side: 568.551237 -> 569

2.dxf lining: 2060.424036 / 907.988483 = 2.269218250 -> 2.27
front side: 681.172684 -> 681
```

Shell geometry does not produce those values. Layer-1 cut-side candidates also do not reproduce the legacy lengths in the same way.

Therefore lining **numeric lineage** remains strongly supported.

However no surviving derivation script proves that the original lost `blocks.py` automatically selected these values via first-occurrence behavior. The compatibility parser still uses first occurrence because it replays observed direct-copy outputs, but that is not uniquely proven as the historical internal algorithm.

Action:

- causal wording downgraded;
- front-side specificity documented;
- reproducible audit tool added.

### H2 — `2.dxf` 12.7 mm front/back shell side mismatch

**Disposition: ACCEPTED; previous conclusion withdrawn.**

The earlier audit selected the wrong back edge.

Using the surviving Claude-era `edges.py` geometric-corner split on purchased `2.dxf` shell gives:

```text
front side = 711.200183 mm
back side  = 711.199804 mm
difference = -0.000379 mm
```

The `723.900048 mm` path is another centre/back construction edge, not the side seam.

The front left side is split into two geometric segments:

```text
533.400272 + 177.799961 = 711.200233 mm
```

which also matches the opposite front side.

The approximately `12.7 mm` relation survives only between the shell side (`~711.2`) and the maker `27.5 in = 698.5 mm` annotation. That is now treated as a length-semantics question, not a sewing mismatch.

### H3 — `1.dxf` ~3x waist does not prove gathering

**Disposition: ACCEPTED.**

`1.dxf` shell front is annular-sector-like and the two radial side paths match each other and the back side at approximately `606.586 mm`. Inner-versus-outer arc identity is strong from sector topology.

If the current back waist assignment is correct, the shell waist is about 3x the lining waist. That supports substantial fullness reduction but **not the mechanism**.

Action:

- gathering language removed as a conclusion;
- gather / pleat / tuck / other controlled fullness remain open.

### H4 — lining semantics were labelled more strongly than the evidence

**Disposition: PARTIALLY ACCEPTED.**

Lining front/back side equality and simple A-line topology make the side/hem/waist labels high-confidence. They are not, however, an independently supplied seam map.

Action:

- changed from `resolved semantic paths` to high-confidence semantic interpretation;
- `PROF_A/B` remains resolved only as **numeric lineage**.

### H5 — `DIRECT_DXF` / `DIRECT_PATH` conflated source facts with semantic inference

**Disposition: ACCEPTED IN PRINCIPLE.**

Action:

- evidence vocabulary split into `RAW_DXF_FACT`, `DIRECT_GEOMETRY`, `HIGH_CONFIDENCE_SEMANTIC`, `CANDIDATE_SEMANTIC` and legacy-lineage classes;
- rigid re-orientation is allowed for invariant path length but does not itself prove a semantic label.

The review also raised bulge/LWPOLYLINE risk. Direct re-check of the actual purchased files found:

```text
1.dxf: 0 LWPOLYLINE, 0 non-zero VERTEX bulges
2.dxf: 0 LWPOLYLINE, 0 non-zero VERTEX bulges
```

So hidden-bulge chord under-measurement does not apply to these two sources, although it remains a generic parser limitation to consider for future files.

## MEDIUM

### M1 — `4.10e-12 mm` replay may have been in-memory rather than stored-DXF

**Disposition: REJECTED for the round-trip concern; duplicate-selection caveat retained.**

Stored generated DXFs were re-parsed from disk and compared to reconstructed purchased source geometry after translation removal.

Examples:

```text
09 direct-copy blocks: max error ~3.64e-12 mm
16 direct-copy body blocks: max error ~2.29e-12 mm
```

The generator writes enough numeric precision that stored round-trips remain at floating-point-noise scale. The earlier `4.10e-12 mm` claim is therefore plausible as a disk-to-disk replay result.

However the review is correct that observed copied pieces do not uniquely discriminate `first occurrence wins` from every possible alternative duplicate-selection heuristic. First-wins remains a compatibility choice, not recovered original source code.

### M2 — `WAIST=907` is numerically close to `2.dxf` lining waist 907.988

**Disposition: ACCEPTED AS A HYPOTHESIS, NOT A RESOLUTION.**

The coincidence is now explicit in the reference audit. Surviving code comments call `907` the block lower opening, while the purchased lining waist measures `907.988483`. The exact historical source of `907` requires a separate semantic audit.

### M3 — `1.dxf` back waist vs centre ambiguity

**Disposition: ACCEPTED.**

The similar `~615.95 / ~616.25 mm` paths remain candidate semantics. Centre-back zipper evidence helps but does not fully settle path identity.

### M4 — hand-entered rounding drift / inch-structure clues

**Disposition: ACCEPTED.**

A reproducible script was added so mechanical source tables can be regenerated rather than manually transcribed. Inch-like differences remain observations only, not drafting rules.

### M5 — generated-artifact evidence leak

**Disposition: ACCEPTED VIA B1 FIX.**

The stale provenance sentence was the main leak. Generated artifacts remain explicitly non-independent.

## Files changed as a result

- `REFERENCE_PATTERN_AUDIT.md`
- `LEGACY_GENERATED_DXF_PROVENANCE.md`
- `LEGACY_SKIRT_PROFILE_FORENSIC.md`
- `SHELL_LINING_SKIRT_COMPARISON.md`
- `tools/audit_purchased_skirt_profiles.py`

## Current safe state

The adversarial review materially improved the evidence model.

The most important correction is:

```text
2.dxf shell front side ~= back side ~= 711.200 mm
```

not:

```text
front/back mismatch ~= 12.7 mm
```

The most important retained finding is:

```text
PROF_A/B numerically align with purchased lining layer-14 profiles
```

with the corrected qualification:

```text
original historical extraction mechanism remains unverified
```

No drafting constant or new production geometry is adopted from this audit alone.
