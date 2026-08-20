# -*- coding: utf-8 -*-
"""mirror — 用 CLO SymmetryPatternPiece 生成後片鏡像。

每鏡像一片即重掃 (索引可能變), 用 targeted signature 搜尋下一個 source。
"""

def make_mirrors(clo, style, scanner, matcher, logger):
    logger.header("MIRROR")
    tol = style.get("tolerance_mm", 6.0)
    before = clo.pattern_count()

    for sem in style.get("mirror_sources", []):
        sig = style["patterns"][sem]["signature"]
        scanned = scanner.scan(clo, logger)
        hits = matcher.find_by_signature(scanned, sig, tol)
        # 已鏡像的會有 2 片; source 尚未鏡像時應恰好 1 片
        if len(hits) == 0:
            logger.fail(f"{sem}: source not found by signature -> SAFE STOP")
            return False
        if len(hits) > 1:
            logger.warn(f"{sem}: {len(hits)} pieces already match signature "
                        f"(already mirrored?) — skip to avoid duplicate")
            continue
        idx = hits[0]
        if not clo.symmetry(idx):
            logger.fail(f"{sem}: SymmetryPatternPiece(idx={idx}) -> False -> SAFE STOP")
            return False
        logger.ok(f"{sem}: mirrored (SymmetryPatternPiece idx={idx})")

    logger.info(f"pattern count {before} -> {clo.pattern_count()}")
    return True
