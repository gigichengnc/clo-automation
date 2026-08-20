# -*- coding: utf-8 -*-
"""
patternlib  ——  可重用的裁片幾何 / 邊分割 / 機讀化工具 (No.09-22 共用)

設計原則:
  1. 不改幾何。只讀既有 net line、偵測角點、把外框「命名」成語意邊。
  2. 邊的機讀身分 = 兩個角點座標 (start_xy/end_xy)，對 CLO 曲線優化穩定,
     不靠 edge length 去猜。line_index 只作 best-effort 排序輔助。
  3. 需要真實分割一條直邊 (例:過肩下口 CB) 時,插入一個「共線頂點」——
     周長不變、幾何不變,但外框由此變成兩段 segment。
"""
import math
import numpy as np

# ---------- 讀取 ----------

def poly_pts(e):
    if e.dxftype() == 'LWPOLYLINE':
        return [(float(x), float(y)) for x, y, *_ in e.get_points()]
    if e.dxftype() == 'POLYLINE':
        return [(float(v.dxf.location.x), float(v.dxf.location.y)) for v in e.vertices]
    if e.dxftype() == 'LINE':
        return [(float(e.dxf.start.x), float(e.dxf.start.y)),
                (float(e.dxf.end.x), float(e.dxf.end.y))]
    return None


def layer_poly(block, layer):
    """回傳指定 layer 上周長最大的 polyline 頂點 (list[(x,y)])。"""
    best = None; bestper = -1
    for e in block:
        if e.dxftype() in ('LWPOLYLINE', 'POLYLINE') and e.dxf.layer == layer:
            p = poly_pts(e)
            if p and len(p) >= 3:
                per = _perim(p, closed=True)
                if per > bestper:
                    best, bestper = p, per
    return best


def grain_line(block, layer='7'):
    for e in block:
        if e.dxf.layer == layer and e.dxftype() == 'LINE':
            s, t = e.dxf.start, e.dxf.end
            return [(float(s.x), float(s.y)), (float(t.x), float(t.y))]
    return None


# ---------- 幾何基礎 ----------

def _perim(pts, closed=True):
    P = np.asarray(pts); d = np.diff(P, axis=0)
    L = float(np.hypot(d[:, 0], d[:, 1]).sum())
    if closed:
        L += float(np.hypot(*(P[0] - P[-1])))
    return L


def seg_length(pts, a, b):
    """closed poly 上由頂點 index a 走到 b 的弧長。"""
    P = np.asarray(pts); n = len(P); L = 0.0; i = a
    while i != b:
        j = (i + 1) % n
        L += float(np.hypot(*(P[j] - P[i]))); i = j
    return L


def dedup(pts, tol=1e-6):
    out = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > tol:
            out.append(p)
    if len(out) > 1 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= tol:
        out.pop()
    return out


def corner_indices(pts, angle_thresh_deg=12.0, min_seg=8.0):
    """
    偵測角點: 轉角 > 閾值。再把相距太近 (< min_seg mm) 的角點群
    合併成單一角點 (取群中轉角最大者),消除毛刺 (1.4 / 1.5 / 6.0mm 那種)。
    回傳排序後的頂點 index list。
    """
    P = np.asarray(pts); n = len(P)
    thr = math.radians(angle_thresh_deg)
    raw = []
    for i in range(n):
        a = P[i] - P[(i - 1) % n]; b = P[(i + 1) % n] - P[i]
        if np.hypot(*a) < 1e-9 or np.hypot(*b) < 1e-9:
            continue
        ang = math.atan2(b[1], b[0]) - math.atan2(a[1], a[0])
        ang = (ang + math.pi) % (2 * math.pi) - math.pi
        if abs(ang) > thr:
            raw.append((i, abs(ang)))
    if not raw:
        return []
    # 合併鄰近角點
    idxs = [i for i, _ in raw]
    strength = {i: s for i, s in raw}
    groups = []; cur = [idxs[0]]
    for i in idxs[1:]:
        if seg_length(pts, cur[-1], i) < min_seg:
            cur.append(i)
        else:
            groups.append(cur); cur = [i]
    groups.append(cur)
    # 環繞: 若頭尾群相近則併
    if len(groups) > 1 and seg_length(pts, groups[-1][-1], groups[0][0]) < min_seg:
        groups[0] = groups.pop() + groups[0]
    keep = [max(g, key=lambda i: strength[i]) for g in groups]
    return sorted(set(keep))


def measured_segments(pts, cidx):
    """由角點 index 切出各段的弧長 (cyclic order,與 cidx 對應)。"""
    segs = []
    for k in range(len(cidx)):
        a = cidx[k]; b = cidx[(k + 1) % len(cidx)]
        segs.append(seg_length(pts, a, b))
    return segs


def align_template(measured, template_lens):
    """
    把 measured (cyclic) 對齊 template_lens。試所有旋轉 + 兩個方向,
    取總長度差最小者。回傳 (rotation, direction, cost)。
    direction = +1 同向 / -1 反向。
    """
    m = len(measured)
    assert m == len(template_lens), (m, len(template_lens))
    best = None
    for d in (+1, -1):
        seq = measured if d == +1 else measured[::-1]
        for r in range(m):
            rot = seq[r:] + seq[:r]
            cost = sum(abs(a - b) for a, b in zip(rot, template_lens))
            if best is None or cost < best[2]:
                best = (r, d, cost)
    return best


# ---------- 分割 / 命名 ----------

def edge_vertex_cycle(pts, cidx, template):
    """
    template = [(edge_id, approx_len, role), ...] cyclic order.
    回傳 [(edge_id, role, v_start, v_end, measured_len)],
    v_start/v_end = pts 中的頂點 index。
    """
    segs = measured_segments(pts, cidx)
    tlen = [t[1] for t in template]
    r, d, cost = align_template(segs, tlen)
    n = len(cidx)
    if d == +1:
        order = [cidx[(r + k) % n] for k in range(n)]
    else:
        # 反向: 由 cidx 反排,再旋轉
        rev = cidx[::-1]
        order = [rev[(r + k) % n] for k in range(n)]
    out = []
    for k, (eid, _, role) in enumerate(template):
        vs = order[k]; ve = order[(k + 1) % n]
        out.append([eid, role, vs, ve, round(seg_length(pts, vs, ve), 2)])
    return out, cost, d


def insert_collinear_vertex(pts, v_start, v_end, at_length):
    """
    在 v_start→v_end 這段(沿 polyline)距 v_start 為 at_length 處插入一個
    頂點。若最近的既有頂點已在 ±0.5mm 內,直接用它 (不加點)。
    回傳 (new_pts, new_index)。周長不變。
    """
    P = list(pts); n = len(P)
    i = v_start; acc = 0.0
    path = [i]
    while i != v_end:
        j = (i + 1) % n
        d = math.hypot(P[j][0] - P[i][0], P[j][1] - P[i][1])
        if acc + d >= at_length - 1e-9:
            need = at_length - acc
            if need <= 0.5:
                return P, i
            if d - need <= 0.5:
                return P, j
            t = need / d
            nx = P[i][0] + (P[j][0] - P[i][0]) * t
            ny = P[i][1] + (P[j][1] - P[i][1]) * t
            P.insert(j, (nx, ny))
            return P, j
        acc += d; i = j; path.append(i)
    return P, v_end


def mirror_x(pts, axis_x):
    return [(2 * axis_x - x, y) for x, y in pts]


def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def normalize(pts, ref_bbox=None):
    """平移使 bbox 左下角 → (0,0)。回傳 (new_pts, (dx,dy))。"""
    x0, y0, x1, y1 = ref_bbox or bbox(pts)
    return [(x - x0, y - y0) for x, y in pts], (-x0, -y0)


# ---------- 驗證 ----------

def self_intersects(pts, min_seg=2.0):
    """
    O(n^2) 線段自交偵測 (忽略相鄰段)。回傳真實交叉數 (int)。
    忽略任一方短於 min_seg 的段 —— 曲線密點在深凹角會出現 <1mm 的
    near-coincident sliver, 那是 re-entrant corner 特徵而非破損幾何。
    """
    P = pts; n = len(P)
    def slen(a, b):
        return math.hypot(b[0]-a[0], b[1]-a[1])
    def seg_int(p1, p2, p3, p4):
        def ccw(a, b, c):
            return (c[1]-a[1])*(b[0]-a[0]) - (b[1]-a[1])*(c[0]-a[0])
        d1 = ccw(p3, p4, p1); d2 = ccw(p3, p4, p2)
        d3 = ccw(p1, p2, p3); d4 = ccw(p1, p2, p4)
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))
    edges = [(P[i], P[(i + 1) % n]) for i in range(n)]
    hits = 0
    for i in range(n):
        if slen(*edges[i]) < min_seg:
            continue
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if slen(*edges[j]) < min_seg:
                continue
            if seg_int(*edges[i], *edges[j]):
                hits += 1
    return hits


def zero_length_edges(pts, tol=1e-4):
    P = pts; n = len(P); bad = 0
    for i in range(n):
        if math.hypot(P[(i+1) % n][0]-P[i][0], P[(i+1) % n][1]-P[i][1]) < tol:
            bad += 1
    return bad
