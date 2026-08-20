# -*- coding: utf-8 -*-
"""
metadata_to_style — 由 DXF_AUTOMATION_V2/<id>/<id>.metadata.json + <id>.seams.json
種出一份 CLO_Agent styles/<id>.json 的 signature 草稿。

注意: 這只是「草稿」。CLO 匯入 DXF 時會按 import 設定重新切曲線, 邊數/邊長可能與
DXF 略有出入。務必在 CLO 內用 GetLineLength 重新 probe 一次, 用實測數覆蓋草稿,
才是權威。用法:
    python tools/metadata_to_style.py 11
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
V2 = os.path.normpath(os.path.join(ROOT, "..", "DXF_AUTOMATION_V2"))

def main(style_id):
    md = json.load(open(os.path.join(V2, style_id, f"{style_id}.metadata.json"), encoding="utf-8"))
    patterns = {}
    for pid, spec in md["patterns"].items():
        sem = pid.split("_", 1)[1] if pid.startswith(style_id + "_") else pid
        sig = [round(e["expected_length_mm"], 2) for e in spec["edges"].values()]
        patterns[sem] = {"quantity": spec.get("quantity", 1), "signature": sig,
                         "_from_dxf": True, "mirror": spec.get("mirror", False)}
    draft = {
        "style": style_id,
        "_comment": "DRAFT seeded from DXF metadata. RE-PROBE inside CLO with GetLineLength "
                    "and overwrite signatures before trusting. See README.",
        "unit": "mm", "tolerance_mm": 6.0,
        "patterns": patterns,
    }
    outp = os.path.join(ROOT, "styles", f"{style_id}.draft.json")
    json.dump(draft, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", outp, "with", len(patterns), "pattern signatures (DRAFT — re-probe in CLO)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "11")
