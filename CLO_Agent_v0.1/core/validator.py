# -*- coding: utf-8 -*-
"""validator — 狀態機驗證。比對實際 (pattern_count, sewing_groups) 對期望狀態。"""

def detect_state(clo, style):
    pc = clo.pattern_count()
    sg = clo.seam_group_count()
    sm = style["state_machine"]
    for name, exp in sm.items():
        if pc == exp["pattern_count"] and sg == exp["sewing_groups"]:
            return name, pc, sg
    return "UNKNOWN", pc, sg


def check_expected(clo, style, state_name, logger):
    exp = style["state_machine"][state_name]
    pc, sg = clo.pattern_count(), clo.seam_group_count()
    ok = True
    if pc == exp["pattern_count"]:
        logger.ok(f"pattern count = {pc}")
    else:
        logger.fail(f"pattern count = {pc}, expected {exp['pattern_count']}"); ok = False
    if sg == exp["sewing_groups"]:
        logger.ok(f"sewing groups = {sg}")
    else:
        logger.fail(f"sewing groups = {sg}, expected {exp['sewing_groups']}"); ok = False
    return ok


def _seam_patterns(style):
    """所有出現在 safe_seams 的 pattern 語意名 (含 list 形式)。"""
    out = set()
    for s in style.get("safe_seams", []):
        for side in ("a", "b"):
            p = s.get(side, {}).get("pattern")
            if isinstance(p, list):
                out.update(p)
            elif p:
                out.add(p)
    return out


def check_pieces_present(assign, style, logger, need_mirrored):
    """確認 safe_seams 需要的片都辨識到 —— 由 style 推導, 不 hardcode 款式。"""
    ok = True
    seam_pats = _seam_patterns(style)
    if need_mirrored:
        need = sorted(seam_pats)
    else:
        # fresh 狀態: 把鏡像後的 L/R 名對回其 source
        rev = {}
        for src, pair in style.get("mirror_result", {}).items():
            for nm in pair:
                rev[nm] = src
        need = sorted({rev.get(n, n) for n in seam_pats})
    for n in need:
        if n in assign:
            logger.ok(f"{n} found")
        else:
            logger.fail(f"{n} MISSING"); ok = False
    return ok


def check_no_dup_seams(planned_ids, logger):
    seen = set(); ok = True
    for sid in planned_ids:
        if sid in seen:
            logger.fail(f"duplicate seam {sid}"); ok = False
        seen.add(sid)
    return ok
