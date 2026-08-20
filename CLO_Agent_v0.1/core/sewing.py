# -*- coding: utf-8 -*-
"""
sewing — 只縫 style config 的 safe_seams。每條縫縫前驗證:

  * 兩片都已語意辨識 (semantic -> index)。
  * 目標邊長在該片的 OUTER 邊 (GetLineLength 回傳的) 中找得到。
    ——這正是 yoke 陷阱的防線: 189mm 只存在於 InnerShape, GetLineLength 拿不到,
       故此永遠不會被縫到。若目標長度找不到 -> SAFE STOP。
  * 不縫任何 sew_in_v01=false 的片 (yoke/collar/facing/belt)。
  * 每片一個 AddSeamlinePairGroup + 一個 AddSeamlinePair, 全部 log line index。

若任何一條縫無法安全解析 -> 立即 SAFE STOP, 已縫的不動。
"""

def _piece_edges(scanned, index):
    for sc in scanned:
        if sc["index"] == index:
            return sc["edges"]
    return None


def sew_safe(clo, style, scanner, matcher, logger):
    logger.header("SEW")
    tol = style.get("tolerance_mm", 6.0)

    # 鏡像後的完整辨識
    scanned = scanner.scan(clo, logger)
    patterns = matcher.expand_patterns(style, mirrored=True)
    assign, unresolved = matcher.identify(scanned, patterns, tol, logger)

    planned = []
    for seam in style["safe_seams"]:
        sid = seam["id"]
        a, b = seam["a"], seam["b"]
        for side in (a, b):
            if side["pattern"] not in assign:
                logger.fail(f"{sid}: pattern {side['pattern']} not identified -> SAFE STOP")
                return False, 0
        ia, ib = assign[a["pattern"]], assign[b["pattern"]]
        ea, eb = _piece_edges(scanned, ia), _piece_edges(scanned, ib)
        la, amb_a = matcher.find_line_index(ea, a["length"], tol, a.get("pick"))
        lb, amb_b = matcher.find_line_index(eb, b["length"], tol, b.get("pick"))
        if la is None:
            logger.fail(f"{sid}: edge {a['length']}mm NOT on outer boundary of "
                        f"{a['pattern']} (InnerShape trap?) -> SAFE STOP")
            return False, 0
        if lb is None:
            logger.fail(f"{sid}: edge {b['length']}mm NOT on outer boundary of "
                        f"{b['pattern']} -> SAFE STOP")
            return False, 0
        if amb_a or amb_b:
            logger.warn(f"{sid}: ambiguous edge pick "
                        f"({a['pattern']}#{la} / {b['pattern']}#{lb}) — used '{a.get('pick') or b.get('pick') or 'first'}' rule")
        planned.append((sid, ia, la, ib, lb))

    # 全部規劃成功才開始縫 (原子性: 規劃階段任何 STOP 都不會縫任何一條)
    sewn = 0
    for sid, ia, la, ib, lb in planned:
        g = clo.add_seam_group()
        ok = clo.add_seam_pair(g, ia, la, ib, lb)
        if not ok:
            logger.fail(f"{sid}: AddSeamlinePair(g={g}, {ia}#{la}, {ib}#{lb}) -> False -> SAFE STOP")
            return False, sewn
        logger.ok(f"{sid}: sewn  ({ia}#{la} <-> {ib}#{lb})")
        sewn += 1

    logger.info(f"sewing groups now = {clo.seam_group_count()}")
    return True, sewn
