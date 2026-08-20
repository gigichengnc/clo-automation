# -*- coding: utf-8 -*-
"""selftest — verify safety branches off-CLO on the SYNTHETIC demo (no real data). Run: python selftest.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from core import logger as _logger, clo_api, scanner, matcher, sewing, validator

STYLE = json.load(open(os.path.join(HERE, "styles", "demo.json"), encoding="utf-8"))
FRESH = json.load(open(os.path.join(HERE, "state", "mock_fresh_demo.json"), encoding="utf-8"))
log = _logger.Logger(os.path.join(HERE, "logs"), echo=False)
fails = []

def check(name, cond):
    print(f"  [{'ok' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)

# 1) find_line_index: closest-wins; near-equal ambiguity resolved by pick
back = [266.0, 270.0, 190.0]
i, amb = matcher.find_line_index(back, 270.0, 6.0)
check("270 -> that edge, not the 266 neighbour (closest-wins)", i == 1 and not amb)
i, amb = matcher.find_line_index(back, 266.0, 6.0)
check("266 -> its own edge", i == 0 and not amb)
front = [280.0, 500.0, 280.0, 400.0]
il, a1 = matcher.find_line_index(front, 280.0, 6.0, pick="left")
ir, a2 = matcher.find_line_index(front, 280.0, 6.0, pick="right")
check("two equal 280 edges disambiguated by pick left/right", il == 0 and ir == 2 and a1 and a2)
i, _ = matcher.find_line_index(front, 999.0, 6.0)
check("missing length -> None", i is None)

# 2) outer-edge / InnerShape guard: a seam whose length is absent -> SAFE STOP
bad = json.loads(json.dumps(STYLE))
bad["safe_seams"] = [{"id": "S_FAKE",
    "a": {"pattern": "DEMO_BACK_L", "length": 135.0},   # not on outer edges -> InnerShape-style trap
    "b": {"pattern": "DEMO_BACK_R", "length": 270.0}}]
clo = clo_api.MockBackend(FRESH)
clo.symmetry(3)                                          # mirror DEMO_BACK -> 5 patterns
ok, sewn = sewing.sew_safe(clo, bad, scanner, matcher, log)
check("guard SAFE STOPs when a seam length is not on the outer boundary", ok is False and sewn == 0)
check("no seams created after guard stop", clo.seam_group_count() == 0)

# 3) state machine detection
clo2 = clo_api.MockBackend(FRESH)
check("fresh detected", validator.detect_state(clo2, STYLE)[0] == "FRESH")
clo2.symmetry(3)
check("mirrored detected", validator.detect_state(clo2, STYLE)[0] == "MIRRORED")
for _ in range(3):
    g = clo2.add_seam_group(); clo2.add_seam_pair(g, 0, 0, 1, 0)
check("safe-checkpoint detected", validator.detect_state(clo2, STYLE)[0] == "SAFE_CHECKPOINT")
clo2.add_seam_group()
check("extra seam -> UNKNOWN (would STOP)", validator.detect_state(clo2, STYLE)[0] == "UNKNOWN")

print("\nSELFTEST:", "ALL PASS" if not fails else f"{len(fails)} FAILED: {fails}")
sys.exit(1 if fails else 0)
