# DXF_AUTOMATION_V2 — pattern → machine-readable / CLO-automatable

> **Measurement-free template.** This repo ships the reusable library `lib/patternlib.py`, the JSON
> schemas, and `gen_example.py` (a synthetic, data-free demo). The real per-style generator
> (`gen11.py`), its measurement templates, and the generated `<style>/*.json` + DXF are kept local
> and **not published**. The techniques are documented below; run `python gen_example.py` for a
> demonstration on invented numbers.

Turns a pattern DXF into a machine-readable form for CLO3D auto-sewing **without changing the
garment geometry**. The generator only **names / segments / mirrors** existing geometry — it never
moves a point. Perimeter of every physical piece is preserved to ~0.000 mm.

## Techniques (in `lib/patternlib.py`)

- **Corner detection + spur merge** — find the true construction corners of a net boundary, ignoring
  sub-mm curve-point noise.
- **Edge naming by endpoints** — split the outline into semantic edges (`E_WAIST`, `E_PRINCESS_L`, …)
  whose machine identity is the two corner endpoints (`start_xy`/`end_xy`), **not** the length. This
  is the whole point: automation should never have to "find the N-mm line".
- **Collinear vertex split** — when sewing needs two real outer segments out of one straight edge
  (the classic yoke-bottom case), insert a *collinear* vertex: two genuine segments, perimeter
  unchanged. Never fake a split with an overlapping internal line.
- **Baked L/R mirroring** — every physical piece becomes its own uniquely-named pattern.
- **Self-intersection / zero-length / grainline / scale checks** for validation.

## Outputs (produced locally by the per-style generator)

| file | what |
|---|---|
| `<style>.metadata.json` | patterns → edges with `line_index`, endpoint identity, length, role, notches, grainline |
| `<style>.seams.json` | seam map: `sew("PID","EID","PID","EID")`-style, type / gather / verified / source / tolerance |
| `<style>.validation.json` | status + errors + warnings (incl. reported ambiguities) |
| `<style>.source.dxf` / `CLO.<style>.dxf` | full-detail + CLO-clean net DXF, ASCII block names |

Schemas for the two JSON files: `schema/garment_metadata.schema.json`, `schema/seam_map.schema.json`
(both validate). See these for the exact field contracts.

## Schema quick reference

`metadata.patterns[PID].edges[EID]`:
```json
{ "line_index": 1, "role": "seam",
  "expected_length_mm": 0.0,
  "start_xy": [x, y], "end_xy": [x, y] }   // endpoints are the machine identity
```
`seams.seams[]`:
```json
{ "id": "S_...", "pattern_a": "PID_A", "edge_a": "E_...",
  "pattern_b": "PID_B", "edge_b": "E_...",
  "type": "1:1", "gathering_ratio": 1.0,
  "expected_length_mm": {"a": 0.0, "b": 0.0},
  "tolerance_mm": 3.0, "verified": true, "source": "geometry" }
```
`1:N` / `M:N` seams use arrays for `pattern_b`/`edge_b` and a `b_total` length.

## Principle: report ambiguity, don't silently fix

When the source geometry is inconsistent or under-defined (a stale stored length that disagrees with
the actual outline; a facing that only covers part of a seam; a collar whose stored numbers are
interface totals not per-piece; a required seam missing from the relationship list), the generator
**records it in `validation.json` and the seam `source`/`verified` fields** rather than quietly
"fixing" the pattern. Identity-by-endpoints exists precisely so a wrong stored number can't cause a
wrong seam.

## Relationship to `../CLO_Agent_v0.1/`

`CLO_Agent_v0.1/tools/metadata_to_style.py <style>` seeds a CLO_Agent style config from a generated
`metadata.json` (re-probe inside CLO to lock exact numbers, since CLO re-segments curves on import).
