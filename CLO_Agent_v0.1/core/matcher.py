# -*- coding: utf-8 -*-
"""
matcher — 由 edge-length signature 語意辨識 pattern, 不靠固定 index。

  * expand_patterns(style, mirrored): 依狀態產生 semantic->signature 表。
      mirrored=False -> mirror_source 保持單片 (FRESH 狀態, 例 BACK_CENTER)。
      mirrored=True  -> mirror_source 換成 L/R 兩片 (同 signature), 用 centroid 分。
  * identify(): signature multiset 容差比對; 同 signature 多片用 centroid.x 分 L/R;
      無 centroid 而需要分 -> SAFE STOP (不亂猜)。
  * find_by_signature(): targeted 搜尋 (mirror loop 用)。
"""
from collections import defaultdict


def expand_patterns(style, mirrored):
    src = style["patterns"]
    if not mirrored:
        return {k: dict(v) for k, v in src.items()}
    out = {}
    mres = style.get("mirror_result", {})
    for sem, spec in src.items():
        if spec.get("mirror_source") and sem in mres:
            l, r = mres[sem]
            out[l] = {"signature": spec["signature"], "side": "L"}
            out[r] = {"signature": spec["signature"], "side": "R"}
        else:
            out[sem] = dict(spec)
    return out


def _sig_err(edges, sig, tol):
    if len(edges) != len(sig):
        return None
    a, b = sorted(edges), sorted(sig)
    if all(abs(x - y) <= tol for x, y in zip(a, b)):
        return sum(abs(x - y) for x, y in zip(a, b))
    return None


def find_by_signature(scanned, sig, tol):
    hits = []
    for sc in scanned:
        e = _sig_err(sc["edges"], sig, tol)
        if e is not None:
            hits.append((e, sc["index"]))
    return [i for _, i in sorted(hits)]


def identify(scanned, patterns, tol, logger):
    """回傳 assign: semantic_id -> pattern_index, 及 unresolved list。"""
    sig_groups = defaultdict(list)
    for sem, spec in patterns.items():
        key = tuple(sorted(round(x, 1) for x in spec["signature"]))
        sig_groups[key].append(sem)

    scan_by_key = defaultdict(list)
    unresolved = []
    for sc in scanned:
        best = None
        for key, sems in sig_groups.items():
            e = _sig_err(sc["edges"], patterns[sems[0]]["signature"], tol)
            if e is not None and (best is None or e < best[1]):
                best = (key, e)
        if best:
            scan_by_key[best[0]].append(sc)
        else:
            unresolved.append(sc)

    assign = {}
    for key, sems in sig_groups.items():
        scs = scan_by_key.get(key, [])
        sems_sorted = sorted(sems, key=lambda s: {"L": 0, "R": 2}.get(patterns[s].get("side"), 1))
        if len(scs) == len(sems_sorted) == 1:
            assign[sems_sorted[0]] = scs[0]["index"]
        elif len(scs) == len(sems_sorted) and len(scs) > 1:
            if any(s["centroid"] is None for s in scs):
                logger.fail(f"signature {key}: {len(scs)} pieces need L/R split but no centroid -> SAFE STOP")
                unresolved.extend(scs); continue
            for sem, sc in zip(sems_sorted, sorted(scs, key=lambda s: s["centroid"][0])):
                assign[sem] = sc["index"]
        else:
            # 數量不符: 盡量對 (fresh 狀態或部分鏡像), 其餘 unresolved
            for i, sc in enumerate(sorted(scs, key=lambda s: (s["centroid"] or [0])[0])):
                if i < len(sems_sorted):
                    assign[sems_sorted[i]] = sc["index"]
                else:
                    unresolved.append(sc)
    return assign, unresolved


def find_line_index(edges, target_length, tol, pick=None, near=1.0):
    """在一片的邊長 list 中找 ≈target 的 line index。

    取「最接近」而非「第一個在容差內」——避免把相近但不同的邊 (例:center-back 與
    back-princess 只差幾 mm) 認錯。只有當最接近的兩條邊長之差 <= near (1mm),
    才視為真正 ambiguous (例:左右對稱的兩條公主縫幾乎等長), 此時用 pick 規則並回報。
    回傳 (line_index, ambiguous)。"""
    scored = sorted(((abs(L - target_length), k) for k, L in enumerate(edges)),
                    key=lambda t: t[0])
    within = [(d, k) for d, k in scored if d <= tol]
    if not within:
        return None, False
    if len(within) == 1:
        return within[0][1], False
    d0 = within[0][0]
    tied = sorted(k for d, k in within if d - d0 <= near)
    if len(tied) == 1:
        return within[0][1], False        # 最接近者明顯勝出, 不 ambiguous
    if pick == "right":
        return tied[-1], True
    return tied[0], True
