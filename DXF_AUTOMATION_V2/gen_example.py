# -*- coding: utf-8 -*-
"""
gen_example — demonstrate patternlib on a SYNTHETIC piece (no real garment data).

Shows the core moves the real generator uses:
  * corner detection on a net boundary
  * splitting the boundary into named semantic edges (identity = corner endpoints)
  * inserting a collinear vertex to split one straight outer edge into two real segments
    (the "yoke bottom" fix — perimeter unchanged)

The real No.11 generator (gen11.py) and its measurement templates are kept LOCAL and not
published. Use this file as the pattern for writing your own <style> generator.

Run: python gen_example.py
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import patternlib as pl

# A synthetic 4-corner "panel": waist (bottom) 200, side 300, top 200, side 300.
pts = []
# bottom edge (0,0)->(200,0) with a mid curve point
pts += [(0, 0), (100, -2), (200, 0)]
# right side up
pts += [(205, 150), (200, 300)]
# top
pts += [(100, 302), (0, 300)]
# left side down
pts += [(-5, 150)]
pts = pl.dedup(pts)

print("perimeter:", round(pl._perim(pts), 1), "mm")
cidx = pl.corner_indices(pts, angle_thresh_deg=20, min_seg=8)
print("corner vertices:", cidx)
print("segment lengths:", [round(x, 1) for x in pl.measured_segments(pts, cidx)])

# name the 4 edges in cyclic order (identity = endpoints, robust to curve optimization)
template = [("E_WAIST", 200, "seam"), ("E_SIDE_R", 300, "seam"),
            ("E_TOP", 200, "seam"), ("E_SIDE_L", 300, "seam")]
edges, cost, direction = pl.edge_vertex_cycle(pts, cidx, template)
print("\nnamed edges (edge_id, role, v_start, v_end, measured_len):")
for e in edges:
    vs, ve = e[2], e[3]
    print(f"  {e[0]:9s} {e[1]:5s} start={tuple(round(v,1) for v in pts[vs])} "
          f"end={tuple(round(v,1) for v in pts[ve])} len={e[4]}")

# split E_WAIST into two real outer segments at its midpoint (collinear vertex; perimeter unchanged)
per_before = pl._perim(pts)
waist = [e for e in edges if e[0] == "E_WAIST"][0]
pts2, mid = pl.insert_collinear_vertex(pts, waist[2], waist[3], waist[4] / 2.0)
print(f"\ninserted collinear vertex at waist midpoint -> new vertex index {mid}")
print(f"perimeter before/after: {per_before:.3f} / {pl._perim(pts2):.3f}  "
      f"(delta {abs(per_before - pl._perim(pts2)):.4f} mm — must be ~0)")
