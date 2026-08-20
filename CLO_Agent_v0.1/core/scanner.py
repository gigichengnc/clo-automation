# -*- coding: utf-8 -*-
"""scanner — 掃描目前 project 內所有 pattern, 抽出可用於辨識的幾何特徵。"""
import re

def _parse_centroid(info_lines):
    """由 GetPatternInputInformation 回傳 (list[str]) 盡量抽出 centroid。
    找不到 -> None (matcher 會改用其他方法並 log)。"""
    for ln in info_lines or []:
        m = re.search(r"centroid\s*=\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)", ln)
        if m:
            return [float(m.group(1)), float(m.group(2))]
    # 後備: 收集所有數對, 取平均 (真 CLO 格式未知時的 best-effort)
    nums = []
    for ln in info_lines or []:
        nums += [float(x) for x in re.findall(r"-?\d+\.\d+", ln)]
    if len(nums) >= 2 and len(nums) % 2 == 0:
        xs = nums[0::2]; ys = nums[1::2]
        return [sum(xs) / len(xs), sum(ys) / len(ys)]
    return None


def scan(clo, logger):
    """回傳 list[dict]: {index, edges:[len...], point_count, centroid, info_raw}"""
    n = clo.pattern_count()
    logger.info(f"scanning {n} patterns ...")
    out = []
    for i in range(n):
        lc = clo.line_count(i)
        edges = [round(clo.line_length(i, k), 2) for k in range(lc)]
        info = clo.pattern_info(i)
        centroid = _parse_centroid(info)
        out.append({"index": i, "edges": edges, "point_count": lc,
                    "centroid": centroid, "info_raw": info})
        logger.info(f"  #{i}: {lc} edges {edges}  centroid={centroid}")
    return out
