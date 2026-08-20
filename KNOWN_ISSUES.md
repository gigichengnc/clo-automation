# Known Issues and Safety Risks

This file records known architectural and runtime risks. It is intentionally conservative: a successful mock test does not prove a safe real-CLO garment build.

Priority meanings:

- **P0** — can invalidate real execution or mark an unsafe garment as safe
- **P1** — can create wrong matching, hidden ambiguity, or broken cross-project identity
- **P2** — maintainability / regression risk

---

## P0 — Real CLO API contract is not yet treated as a verified runtime contract

### Problem

The CLO adapter and the historical API audit contain assumptions that need to be checked against the version of CLO actually running the automation.

Areas requiring explicit verification include:

- return format of pattern-information APIs
- seam/sewing group creation signatures and workflow
- pattern-line versus internal-line addressing
- project export signatures
- sewing-group inspection APIs used for post-action verification

The public CLO API documentation is actively versioned. As of August 2026, CLO publishes SDK/API documentation for v10.0.3 / CLO 2026.0.356, with the v10.0.3 changelog dated July 2026.

### Risk

A mock backend may pass while the real backend calls an API using the wrong signature, wrong return-type assumption, or wrong object/index model.

### Required fix

1. Record the exact installed CLO application and SDK/API version.
2. Compare the adapter against that installation's `ApiStubFiles` or equivalent shipped stubs.
3. Add a small contract probe that reports available methods and representative return types without changing the garment.
4. Make the real backend fail closed when the expected API contract is not present.
5. Update `docs/clo-api-verification.md` whenever CLO is upgraded.

### Safety rule

> MockBackend success does not imply RealBackend compatibility.

---

## P0 — State validation can be weaker than topology validation

### Problem

A garment state must not be declared safe only because expected object counts are present.

For example:

```text
13 patterns + 9 sewing groups
```

only proves that those quantities exist. It does not prove that the intended pattern edges are connected to the intended partners.

### Risk

A garment can have the correct number of seams but the wrong seam topology and still look superficially like a completed state to a count-based validator.

### Required fix

A checkpoint must verify semantic seam identities, for example:

```text
front_left.side
    ↔
back_left.side
```

Validation should compare the expected topology with the observed topology after an action.

Counts remain useful as sanity checks, never as proof of correctness.

---

## P1 — DXF → CLO semantic identity bridge is incomplete

### Problem

The DXF side can know stable pattern and edge identities, while the CLO side may later rediscover an edge from weaker geometric signals.

### Risk

Known information is discarded and ambiguity is reintroduced downstream.

Two edges with similar lengths can be confused even though the upstream pipeline already knew which edge was which.

### Required fix

Preserve identity end-to-end:

```text
DXF
→ pattern ID
→ stable edge ID
→ seam specification
→ CLO reconciliation
→ observed topology validation
```

The style/compiler bridge should consume seam definitions and validation metadata rather than only recreating enough information to guess later.

---

## P1 — Ambiguous geometry must not be silently resolved by index order

### Problem

Implementation details such as a lower or higher line index are not semantic definitions of left/right, front/back, upper/lower, or inside/outside.

### Risk

A deterministic tie-breaker can make an incorrect result appear reliable because it always produces the same answer.

### Required fix

Ambiguity policy:

```text
one verified match   → continue
multiple valid match → stop
no valid match       → stop
```

If a deterministic fallback is ever allowed, it must be explicitly encoded in the garment specification and covered by a test fixture.

---

## P1 — Parse failures must not become plausible geometry

### Problem

If input returned by CLO cannot be parsed using the expected contract, fallback extraction of arbitrary numeric values can create plausible-looking centroids or coordinates.

### Risk

Bad data becomes apparently valid geometry, making later matching errors hard to detect.

### Required fix

```text
parse success → typed geometry
parse failure → UNKNOWN / validation error
```

Do not infer a centroid or pattern identity from untrusted numeric fragments.

---

## P1 — Operation success is not equivalent to verified garment state

### Problem

There are multiple different meanings of "success":

1. function was called
2. API returned without exception
3. object/seam was created
4. created object matches requested identity
5. complete expected topology is verified
6. garment passes the checkpoint

These states should not be collapsed into one boolean.

### Required fix

Runtime state should distinguish at least:

```text
ATTEMPTED
API_SUCCEEDED
OBSERVED
VERIFIED
SAFE_CHECKPOINT
FAILED
AMBIGUOUS
```

Persist enough evidence to explain why a checkpoint was declared safe.

---

## P1 — Garment-specific knowledge can leak into engine code

### Problem

If a script contains hard-coded assumptions for one skirt, blouse, or dress, the engine becomes a growing collection of garment-specific exceptions.

### Required fix

Move garment-specific facts into versioned data/fixtures:

- pattern semantic IDs
- expected piece multiplicity
- mirror rules
- seam topology
- allowed tolerances
- checkpoints

Keep the engine generic.

---

## P2 — Regression coverage is not yet the primary expansion mechanism

### Problem

Adding garments faster than tests creates a codebase where every new item can break a previously working garment.

### Required fix

Each approved garment should become a regression fixture.

A future 09–22 migration should be treated as a fixture/test matrix, not as 14 independent one-off scripts.

Minimum fixture evidence should include:

- source garment ID
- source DXF checksum/version
- expected pattern IDs
- expected edge IDs
- expected seam topology
- expected mirror relations
- known tolerances
- human-approved final state reference

---

## P2 — API/version provenance should be stored with outputs

Generated state and exported assets should record relevant provenance where practical:

- garment schema version
- source garment ID
- source data version/checksum
- CLO version
- adapter version
- pipeline version/commit

This will make future failures reproducible after CLO or Blender upgrades.
