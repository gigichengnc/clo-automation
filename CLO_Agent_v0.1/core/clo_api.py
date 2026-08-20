# -*- coding: utf-8 -*-
"""
clo_api  ——  單一封裝層, 隔離所有 CLO Python API 呼叫。

* 在 CLO 內執行  -> REAL backend, 只呼叫官方已驗證函式 (見 API_AUDIT.md)。
* 在 CLO 外執行  -> MOCK backend, 由 fixture 驅動, 令 state machine / matcher /
                    sewing 邏輯可以在普通 Python 完整測試。MOCK 絕不假冒真 API 結果,
                    它是 test double, 每個回傳都標明來自 mock。

只在此檔 import 真 CLO 模組; 其餘 core/* 一律經此層, 永不直接 import pattern_api。
每個 method 都對應 API_AUDIT.md 一條已驗證簽名。未驗證的 (ExportZPrj 所屬模組)
以 try 多個候選 + 明確 log 處理, 絕不假裝成功。
"""
import os, json

# ---- 嘗試載入真 CLO 模組 ----
_REAL = False
try:
    import pattern_api as _pat          # verified: GetPatternCount / GetLineLength / ...
    import import_api as _imp           # verified: ImportFile
    _REAL = True
except Exception:
    _REAL = False

try:
    import export_api as _exp           # ExportZPrj 疑似在此模組 (見 audit)
except Exception:
    _exp = None


class CloBackend:
    """Base interface — 兩個 backend 都實作同一組 method。"""
    is_real = False
    def import_file(self, path): raise NotImplementedError
    def pattern_count(self): raise NotImplementedError
    def pattern_info(self, idx): raise NotImplementedError
    def line_length(self, idx, line): raise NotImplementedError
    def line_count(self, idx): raise NotImplementedError
    def symmetry(self, idx): raise NotImplementedError
    def add_seam_group(self): raise NotImplementedError
    def add_seam_pair(self, g, p1, l1, p2, l2): raise NotImplementedError
    def seam_group_count(self): raise NotImplementedError
    def export_zprj(self, path): raise NotImplementedError


# ============================================================
#  REAL backend — 只用官方已驗證 API
# ============================================================
class RealBackend(CloBackend):
    is_real = True

    def import_file(self, path):
        return _imp.ImportFile(path)                       # Import_API (v4.0.2+)

    def pattern_count(self):
        return int(_pat.GetPatternCount())                # Pattern_API (v3.2.0+)

    def pattern_info(self, idx):
        # returns list[str] — 格式未在官方 changelog 明列; 原樣回傳並由 scanner 記錄
        return _pat.GetPatternInputInformation(int(idx))  # Pattern_API (v3.2.0+)

    def line_length(self, idx, line):
        return float(_pat.GetLineLength(int(idx), int(line)))   # Pattern_API (v3.2.0+)

    def line_count(self, idx):
        # 官方無 GetLineCount。探測法: line_length 由 0 起遞增, 失敗/<=0 即止。
        n = 0
        while n < 128:
            try:
                v = _pat.GetLineLength(int(idx), n)
            except Exception:
                break
            if v is None or v <= 0.0:
                break
            n += 1
        return n

    def symmetry(self, idx):
        return bool(_pat.SymmetryPatternPiece(int(idx)))  # Pattern_API

    def add_seam_group(self):
        return int(_pat.AddSeamlinePairGroup())           # Pattern_API -> group index

    def add_seam_pair(self, g, p1, l1, p2, l2):
        return bool(_pat.AddSeamlinePair(int(g), int(p1), int(l1), int(p2), int(l2)))

    def seam_group_count(self):
        return int(_pat.GetSeamlinePairGroupCount())      # Pattern_API

    def export_zprj(self, path):
        # ExportZPrj(_filePath, _bCreateThumbnail) -> str  (簽名已驗證; 所屬模組待確認)
        for mod in (_exp, _pat):
            if mod is not None and hasattr(mod, "ExportZPrj"):
                return mod.ExportZPrj(path, True)
        raise RuntimeError("ExportZPrj not found on export_api/pattern_api — "
                           "checkpoint save unavailable in this CLO build")


# ============================================================
#  MOCK backend — test double, fixture 驅動
# ============================================================
class MockBackend(CloBackend):
    is_real = False

    def __init__(self, fixture):
        # fixture["patterns"] = [ {semantic, sig:[...], centroid:[x,y], point_count}, ... ]
        self.pats = [dict(p) for p in fixture["patterns"]]
        self.groups = []          # each group = list of pairs
        self.export_calls = []

    def import_file(self, path):
        return f"[MOCK] pretended import of {os.path.basename(path)}"

    def pattern_count(self):
        return len(self.pats)

    def pattern_info(self, idx):
        p = self.pats[idx]
        # mock format: 明確標 MOCK, 內含 centroid 供 matcher 解析
        return [f"MOCK_PATTERN name={p.get('semantic','?')}",
                f"point_count={p.get('point_count', len(p['sig']))}",
                f"centroid={p['centroid'][0]:.2f},{p['centroid'][1]:.2f}"]

    def line_length(self, idx, line):
        sig = self.pats[idx]["sig"]
        if line < 0 or line >= len(sig):
            return 0.0
        return float(sig[line])

    def line_count(self, idx):
        return len(self.pats[idx]["sig"])

    def symmetry(self, idx):
        src = self.pats[idx]
        mir = dict(src)
        mir["sig"] = list(src["sig"])                 # 鏡像不改邊長
        mir["centroid"] = [src["centroid"][0] + 400.0, src["centroid"][1]]  # 放右邊
        mir["semantic"] = src.get("semantic", "?") + "_MIRROR"
        mir["_mirrored_from"] = src.get("semantic")
        self.pats.append(mir)
        return True

    def add_seam_group(self):
        self.groups.append([])
        return len(self.groups) - 1

    def add_seam_pair(self, g, p1, l1, p2, l2):
        if g < 0 or g >= len(self.groups):
            return False
        # 驗證 line index 有效
        if l1 >= self.line_count(p1) or l2 >= self.line_count(p2):
            return False
        self.groups[g].append((p1, l1, p2, l2))
        return True

    def seam_group_count(self):
        return len(self.groups)

    def export_zprj(self, path):
        self.export_calls.append(path)
        marker = path + ".MOCK.json"
        with open(marker, "w", encoding="utf-8") as f:
            json.dump({"MOCK_CHECKPOINT": True, "requested_path": path,
                       "pattern_count": self.pattern_count(),
                       "sewing_groups": self.seam_group_count()}, f, indent=1)
        return f"[MOCK] wrote checkpoint marker {os.path.basename(marker)} "
    # 注意: MOCK 不會產生真 .zprj。REAL backend 才呼叫 ExportZPrj。


# ============================================================
#  Factory
# ============================================================
def make_backend(mock_fixture_path=None, logger=None):
    if _REAL:
        if logger: logger.ok("CLO Python API detected — REAL backend")
        return RealBackend()
    # off-CLO
    if mock_fixture_path and os.path.exists(mock_fixture_path):
        with open(mock_fixture_path, encoding="utf-8") as f:
            fx = json.load(f)
        if logger:
            logger.warn("CLO Python API NOT found — MOCK backend (off-CLO test mode)")
            logger.info(f"mock fixture: {os.path.basename(mock_fixture_path)}")
        return MockBackend(fx)
    raise RuntimeError("Not inside CLO and no mock fixture provided. "
                       "Run this inside CLO's Python Editor, or pass a mock fixture.")
