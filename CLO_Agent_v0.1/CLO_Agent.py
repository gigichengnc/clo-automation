# -*- coding: utf-8 -*-
"""
CLO_Agent  v0.1  ——  單一可重用 CLO3D 自動化控制器 (state machine)

流程 (v0.1, 模擬前停):
    scan -> identify -> validate -> mirror -> validate -> auto-sew safe seams
         -> validate -> checkpoint -> STOP at SAFE CHECKPOINT

用法:
  * CLO 內: Main Menu > Edit > Python Script > 開此檔 > Run。
             (自動偵測 CLO API, 用 REAL backend。)
  * CLO 外測試: `python CLO_Agent.py`  (無 CLO API -> MOCK backend, state/mock_fresh_11.json)

讀 state/command.json {style, action}; 寫 state/current_state.json。
只做已驗證安全的 9 條縫; 遇任何 ambiguity/未驗證情況 -> SAFE STOP。
"""
import os, sys, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from core import logger as _logger
from core import clo_api, scanner, matcher, mirror, sewing, validator, checkpoint


def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def write_state(style, status, clo, warnings, errors, extra=None):
    st = {"style": style, "status": status,
          "pattern_count": clo.pattern_count(),
          "sewing_groups": clo.seam_group_count(),
          "backend": "REAL_CLO" if clo.is_real else "MOCK",
          "warnings": warnings, "errors": errors,
          "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    if extra:
        st.update(extra)
    with open(os.path.join(HERE, "state", "current_state.json"), "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    return st


def run():
    log = _logger.Logger(os.path.join(HERE, "logs"))
    cmd = load_json(os.path.join(HERE, "state", "command.json"), {"style": "demo", "action": "build_safe"})
    style_id = cmd.get("style", "11")
    action = cmd.get("action", "build_safe")

    style = load_json(os.path.join(HERE, "styles", f"{style_id}.json"))
    if style is None:
        log.stop(f"style config styles/{style_id}.json not found")
        return

    log.raw(""); log.raw("=" * 42)
    log.raw("CLO AGENT  v0.1"); log.raw(f"Style: {style_id}   Action: {action}")
    log.raw("=" * 42)

    clo = clo_api.make_backend(os.path.join(HERE, "state", f"mock_fresh_{style_id}.json"), log)
    warnings, errors = [], []

    if action != "build_safe":
        log.stop(f"action '{action}' not supported in v0.1 (only 'build_safe')")
        write_state(style_id, "UNSUPPORTED_ACTION", clo, warnings, ["unsupported action"])
        return

    # ---- 偵測狀態 ----
    state_name, pc, sg = validator.detect_state(clo, style)
    log.info(f"detected state: {state_name}  (patterns={pc}, seams={sg})")

    if state_name == "SAFE_CHECKPOINT":
        log.header("RESULT")
        log.ok("SAFE CHECKPOINT already reached")
        log.info("next stage (arrange/simulate) not yet enabled in v0.1 — nothing to do")
        write_state(style_id, "SAFE_CHECKPOINT", clo, warnings, errors)
        _summary(log, clo)
        return

    if state_name not in ("FRESH", "MIRRORED"):
        log.stop(f"unexpected state (patterns={pc}, seams={sg}) — refuse to continue")
        write_state(style_id, "STOP_UNEXPECTED_STATE", clo, warnings,
                    [f"unexpected state patterns={pc} seams={sg}"])
        return

    tol = style.get("tolerance_mm", 6.0)

    # ---- FRESH: 驗證 + 鏡像 ----
    if state_name == "FRESH":
        log.header("SCAN / IDENTIFY  (fresh)")
        scanned = scanner.scan(clo, log)
        assign, unresolved = matcher.identify(scanned, matcher.expand_patterns(style, False), tol, log)
        if not validator.check_expected(clo, style, "FRESH", log):
            errors.append("fresh count mismatch")
            write_state(style_id, "STOP_FRESH_MISMATCH", clo, warnings, errors); return
        if not validator.check_pieces_present(assign, style, log, need_mirrored=False):
            errors.append("missing source pieces")
            write_state(style_id, "STOP_MISSING_PIECES", clo, warnings, errors); return
        checkpoint.save(clo, os.path.join(HERE, "checkpoints"), f"{style_id}_00_fresh.zprj", log)

        if not mirror.make_mirrors(clo, style, scanner, matcher, log):
            errors.append("mirror failed")
            write_state(style_id, "STOP_MIRROR", clo, warnings, errors); return
        if not validator.check_expected(clo, style, "MIRRORED", log):
            errors.append("post-mirror count mismatch")
            write_state(style_id, "STOP_MIRROR_COUNT", clo, warnings, errors); return
        checkpoint.save(clo, os.path.join(HERE, "checkpoints"), f"{style_id}_01_mirrored.zprj", log)
        state_name = "MIRRORED"

    # ---- MIRRORED: 安全縫合 ----
    if state_name == "MIRRORED":
        log.header("IDENTIFY  (mirrored, for sewing)")
        scanned = scanner.scan(clo, log)
        assign, _ = matcher.identify(scanned, matcher.expand_patterns(style, True), tol, log)
        if not validator.check_pieces_present(assign, style, log, need_mirrored=True):
            errors.append("missing mirrored pieces before sew")
            write_state(style_id, "STOP_MISSING_MIRRORED", clo, warnings, errors); return

        ok, sewn = sewing.sew_safe(clo, style, scanner, matcher, log)
        if not ok:
            errors.append(f"sewing safe-stopped after {sewn} seams")
            write_state(style_id, "STOP_SEWING", clo, warnings, errors,
                        extra={"seams_completed": sewn}); return
        if not validator.check_expected(clo, style, "SAFE_CHECKPOINT", log):
            errors.append("post-sew count mismatch")
            write_state(style_id, "STOP_SEW_COUNT", clo, warnings, errors); return
        checkpoint.save(clo, os.path.join(HERE, "checkpoints"), f"{style_id}_02_safe_sewn.zprj", log)

    write_state(style_id, "SAFE_CHECKPOINT", clo, warnings, errors)
    _summary(log, clo)


def _summary(log, clo):
    log.header("STATUS")
    log.raw(f"Patterns = {clo.pattern_count()}")
    log.raw(f"Sewing groups = {clo.seam_group_count()}")
    log.raw("STATUS = SAFE CHECKPOINT")
    log.raw("(v0.1 stops before arrange / simulate)")


if __name__ == "__main__":
    run()
