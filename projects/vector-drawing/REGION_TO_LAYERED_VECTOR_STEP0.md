# Region → Layered Vector Step 0

## Status

`RESEARCH_PROTOTYPE` / `NOT_PRODUCTION_OUTPUT`

This experiment tests one narrow part of the proposed open-domain image pipeline:

```text
normalized region partition
        ↓
closed region boundaries
        ↓
vector fill regions
        +
explicitly selected line boundaries
        ↓
layered SVG
```

It deliberately starts **after segmentation**. No SAM, diffusion model, VLM,
photograph, garment classifier, curve fitter, or production DXF is involved yet.

## Important correction: masks are not automatically a partition

A raw segmentation system may return:

- overlapping masks;
- unassigned pixels;
- multiple competing labels;
- disconnected fragments;
- topology that changes under thresholding.

Therefore the topology guarantee does **not** begin at `raw masks`.

The intended architecture is:

```text
raw masks / generated regions
        ↓
NORMALIZE
(each raster cell has exactly one region id)
        ↓
RegionPartition
        ↓
closed-loop vectorization
```

Only after normalization do we have a true planar partition from which closed
boundaries can be deterministically traced.

## Prototype implementation

```text
vector_drawing/region_partition.py
```

The v0 prototype uses an integer cell grid. For each labelled region it:

1. finds cell edges adjacent to another region or the outside;
2. orients the edges consistently;
3. chains them into closed loops;
4. safe-stops on non-manifold / ambiguous corner topology;
5. renders region loops under `<g id="regions">`;
6. renders only explicitly selected visible boundaries under `<g id="lines">`.

The output is intentionally rectilinear. This is a topology test, not the final
Bezier/smoothing stage.

## Boundary roles

A key rule is that **not every region boundary becomes a visible line**.

The current research vocabulary is:

```text
REGION_BOUNDARY
INTERNAL_DETAIL
CONSTRUCTION
OCCLUSION
FILL_ONLY
```

For example, a shadow can be a separate fill region while its boundary is
`FILL_ONLY`. A belt edge or seam may instead be `INTERNAL_DETAIL`.

This keeps two different questions separate:

```text
Where does one fill region end?
                ≠
Should that boundary be drawn as a line?
```

The second question remains the open research problem for real images.

## Known-answer synthetic fixture

The regression fixture contains four labelled regions:

```text
background
body
shadow
belt
```

with explicit roles:

```text
background ↔ body  = REGION_BOUNDARY
body ↔ shadow      = FILL_ONLY
body ↔ belt        = INTERNAL_DETAIL
shadow ↔ belt      = FILL_ONLY
```

This lets the test know the correct topology and the intended visible-line
behavior before any real image segmentation is introduced.

## Step-0 acceptance checks

The tests currently require:

1. every emitted region loop is closed;
2. changing only the palette changes the region layer but leaves the exact line
   group byte-identical;
3. a `FILL_ONLY` boundary can remain a color-region boundary without appearing
   in the line layer;
4. ambiguous diagonal-touch topology safe-stops instead of guessing a loop;
5. missing/unassigned partition cells are rejected rather than silently filled.

The strongest property demonstrated by this design is:

```text
palette change
        ↓
regions change
lines remain identical
```

That is the first concrete proof target for the original idea that line and
color should not be generated as one inseparable raster image.

## What this does NOT prove

Step 0 does not show that real AI-generated images can be segmented into useful
regions.

It does not solve:

- which segmentation method to use;
- overlapping SAM masks;
- tiny-region cleanup;
- antialiasing / soft boundaries;
- smooth Bezier fitting;
- deciding whether a boundary is a seam, object contour, shadow, highlight or
  texture transition;
- semantic region naming;
- open-domain illustration quality.

Those are intentionally deferred.

## Next falsification step

If this topology layer remains stable, the next experiment should replace the
hand-labelled fixture with **one actual raster image plus an explicitly recorded
region map**.

Run two tracks separately:

```text
Track A — known labels
raster + manually verified region partition
→ vector loops
→ layered SVG

Track B — automatic proposal
same raster
→ segmentation proposal
→ normalization
→ same vectorizer
```

Comparing A and B tells us whether failure comes from segmentation or from the
vector/layer backend.

Only after that should we add smoothing / Bezier fitting.

## Current conclusion

The useful research claim is narrower than "segmentation solves line art":

> If an image can first be converted into a valid region partition, closed fill
> topology and independent recoloring can be deterministic. The unresolved
> problem is obtaining the right partition and deciding which region boundaries
> deserve visible lines.
