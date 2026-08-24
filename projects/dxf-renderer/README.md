# DXF Renderer

Status: v0.1 outline-pass prototype.

Purpose: turn structured DXF geometry into deterministic rendering passes instead of generating final pixels directly.

```text
DXF / vector geometry
        ↓
vector scene
        ↓
outline pass       [v0.1]
        ↓
region/mask pass   [next]
        ↓
base-color pass
        ↓
shadow pass
        ↓
highlight pass
        ↓
texture/composite
```

The renderer is deliberately not garment-specific. Garment patterns are one source of clean vector structure, but the same pipeline should later accept other structured drawings.

## v0.1

`dxf_renderer.loader` expands DXF INSERTs and converts supported 2D entities to deterministic vector paths. Curves are flattened at an explicit tolerance. Text and point-only construction data are ignored in v0.1.

`dxf_renderer.svg` writes a clean black-line SVG outline pass. Original DXF layer/source/entity metadata is attached to each SVG path as `data-*` attributes so later region and rendering stages do not have to rediscover structure from pixels.

Example:

```bash
python -m dxf_renderer.cli input.dxf outline.svg --layers 14
```

For a general DXF, omit `--layers` to render all supported vector layers.

## Boundary

v0.1 does **not**:

- infer garment semantics;
- decide which closed contour should be colored;
- generate shadows/highlights;
- rasterize with AI;
- alter source DXF geometry.

Those are later passes built on the same vector scene.
