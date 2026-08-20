# -*- coding: utf-8 -*-
"""
CLO runtime contract probe (read-only).

Captures the actual CLO Python runtime contract before Phase 2 changes the
RealBackend. This probe may import CLO API modules and call allow-listed
read-only getters. It never calls sewing, mirroring, importing, exporting,
simulation, setters, deletion, or other garment/project mutation APIs.

Output: state/clo_contract_probe.json
"""
from __future__ import print_function

import datetime
import importlib
import inspect
import json
import os
import platform
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE_DIR = os.path.join(ROOT, "state")
OUTPUT_PATH = os.path.join(STATE_DIR, "clo_contract_probe.json")

MODULE_NAMES = (
    "pattern_api",
    "export_api",
    "import_api",
    "utility_api",
    "fabric_api",
)

# Presence/signature inspection only. NEVER invoke these from this probe.
MUTATING_API_CANDIDATES = {
    "pattern_api": (
        "AddSeamlinePairGroup",
        "AddSeamlinePair",
        "SymmetryPatternPiece",
    ),
    "import_api": ("ImportFile",),
    "export_api": ("ExportZPrj", "ExportDXF", "ExportOBJ"),
    "utility_api": ("Simulate",),
}


def _utc_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _type_name(value):
    return type(value).__name__


def _doc_excerpt(obj, limit=1600):
    text = getattr(obj, "__doc__", None) or ""
    text = "\n".join(line.rstrip() for line in text.strip().splitlines())
    if len(text) > limit:
        return text[:limit] + "...<truncated>"
    return text


def _signature(obj):
    try:
        return str(inspect.signature(obj))
    except Exception:
        return None


def _function_info(module, name):
    if module is None:
        return {"available": False, "reason": "module_not_imported"}
    if not hasattr(module, name):
        return {"available": False, "reason": "attribute_missing"}
    obj = getattr(module, name)
    return {
        "available": True,
        "callable": callable(obj),
        "python_signature": _signature(obj),
        "doc_excerpt": _doc_excerpt(obj),
    }


def _json_shape(value):
    result = {
        "python_type": _type_name(value),
        "is_string": isinstance(value, str),
        "valid_json": False,
    }
    if not isinstance(value, str):
        return result
    try:
        parsed = json.loads(value)
    except Exception as exc:
        result["json_error"] = "%s: %s" % (_type_name(exc), str(exc))
        return result
    result["valid_json"] = True
    result["json_type"] = _type_name(parsed)
    if isinstance(parsed, dict):
        result["top_level_keys"] = sorted(str(k) for k in parsed.keys())[:100]
        result["top_level_key_count"] = len(parsed)
    elif isinstance(parsed, list):
        result["item_count"] = len(parsed)
        if parsed:
            result["first_item_type"] = _type_name(parsed[0])
            if isinstance(parsed[0], dict):
                result["first_item_keys"] = sorted(
                    str(k) for k in parsed[0].keys()
                )[:100]
    return result


def _call_read_only(module, name, *args):
    record = {"called": False, "ok": False, "args": list(args)}
    if module is None:
        record["error"] = "module_not_imported"
        return record, None
    if not hasattr(module, name):
        record["error"] = "attribute_missing"
        return record, None
    fn = getattr(module, name)
    record["called"] = True
    try:
        value = fn(*args)
        record["ok"] = True
        record["return_type"] = _type_name(value)
        if isinstance(value, (bool, int, float)) or value is None:
            record["value"] = value
        elif isinstance(value, str):
            record["string_length"] = len(value)
        elif isinstance(value, (list, tuple, dict)):
            record["container_length"] = len(value)
        return record, value
    except Exception as exc:
        record["error"] = "%s: %s" % (_type_name(exc), str(exc))
        record["traceback"] = traceback.format_exc(limit=3)
        return record, None


def _import_modules():
    modules = {}
    report = {}
    for name in MODULE_NAMES:
        try:
            module = importlib.import_module(name)
            modules[name] = module
            report[name] = {
                "imported": True,
                "module_file": getattr(module, "__file__", None),
            }
        except Exception as exc:
            modules[name] = None
            report[name] = {
                "imported": False,
                "error": "%s: %s" % (_type_name(exc), str(exc)),
            }
    return modules, report


def _version_probe(utility_api):
    out = {}
    parts = []
    for name, label in (
        ("GetMajorVersion", "major"),
        ("GetMinorVersion", "minor"),
        ("GetPatchVersion", "patch"),
    ):
        call, value = _call_read_only(utility_api, name)
        out[label] = call
        parts.append(value if call.get("ok") and isinstance(value, int) else None)
    if all(v is not None for v in parts):
        out["version_string"] = "%s.%s.%s" % tuple(parts)
    else:
        out["version_string"] = None
    return out


def _find_stub_candidates(executable_folder):
    if not executable_folder or not isinstance(executable_folder, str):
        return []
    roots = [
        executable_folder,
        os.path.dirname(executable_folder),
        os.path.join(executable_folder, "ApiStubFiles"),
        os.path.join(os.path.dirname(executable_folder), "ApiStubFiles"),
    ]
    seen = set()
    found = []
    for path in roots:
        norm = os.path.normpath(path)
        if norm in seen:
            continue
        seen.add(norm)
        if os.path.isdir(norm):
            if os.path.basename(norm).lower() == "apistubfiles":
                found.append(norm)
                continue
            try:
                for child in os.listdir(norm):
                    child_path = os.path.join(norm, child)
                    if child.lower() == "apistubfiles" and os.path.isdir(child_path):
                        found.append(os.path.normpath(child_path))
            except Exception:
                pass
    return sorted(set(found))


def main():
    os.makedirs(STATE_DIR, exist_ok=True)
    modules, module_report = _import_modules()
    pat = modules.get("pattern_api")
    util = modules.get("utility_api")

    report = {
        "probe_schema_version": "0.1.0",
        "project_period": "Year 2 Summer Project — August 2026",
        "generated_utc": _utc_now(),
        "policy": {
            "read_only": True,
            "mutating_calls_invoked": [],
            "note": (
                "Mutating API candidates are inspected for presence/signature only. "
                "The probe does not sew, mirror, import, export, simulate, set, or delete."
            ),
        },
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
        },
        "modules": module_report,
        "clo_version": _version_probe(util),
        "api_surface": {},
        "read_only_observations": {},
        "capability_evidence": {},
        "gates": {},
    }

    exe_call, exe_value = _call_read_only(util, "GetCLOExecutableFolderPath", True)
    report["read_only_observations"]["clo_executable_folder"] = exe_call
    if exe_call.get("ok") and isinstance(exe_value, str):
        report["read_only_observations"]["clo_executable_folder"]["value"] = exe_value
        report["read_only_observations"]["api_stub_candidates"] = _find_stub_candidates(exe_value)
    else:
        report["read_only_observations"]["api_stub_candidates"] = []

    inspect_targets = {
        "pattern_api": (
            "GetPatternCount",
            "GetPatternInputInformation",
            "GetLineLength",
            "GetAllStitchProperty",
            "GetSeamlinePairGroupCount",
            "AddSeamlinePairGroup",
            "AddSeamlinePair",
            "SymmetryPatternPiece",
        ),
        "export_api": ("ExportZPrj",),
        "import_api": ("ImportFile",),
        "utility_api": (
            "GetMajorVersion",
            "GetMinorVersion",
            "GetPatchVersion",
            "GetCLOExecutableFolderPath",
            "Simulate",
        ),
    }
    for module_name, names in inspect_targets.items():
        module = modules.get(module_name)
        report["api_surface"][module_name] = {
            name: _function_info(module, name) for name in names
        }

    report["policy"]["mutating_api_candidates"] = MUTATING_API_CANDIDATES

    pattern_count_call, pattern_count = _call_read_only(pat, "GetPatternCount")
    report["read_only_observations"]["pattern_count"] = pattern_count_call

    stitch_call, stitch_value = _call_read_only(pat, "GetAllStitchProperty")
    if stitch_call.get("ok"):
        stitch_call["json_shape"] = _json_shape(stitch_value)
    report["read_only_observations"]["all_stitch_property"] = stitch_call

    if pattern_count_call.get("ok") and isinstance(pattern_count, int) and pattern_count > 0:
        info_call, info_value = _call_read_only(pat, "GetPatternInputInformation", 0)
        if info_call.get("ok"):
            info_call["json_shape"] = _json_shape(info_value)
        report["read_only_observations"]["pattern_input_information_0"] = info_call
        line_call, _ = _call_read_only(pat, "GetLineLength", 0, 0)
        report["read_only_observations"]["line_length_0_0"] = line_call
    else:
        reason = "no_pattern_available_or_pattern_count_failed"
        report["read_only_observations"]["pattern_input_information_0"] = {
            "called": False,
            "ok": False,
            "reason": reason,
        }
        report["read_only_observations"]["line_length_0_0"] = {
            "called": False,
            "ok": False,
            "reason": reason,
        }

    get_line = report["api_surface"]["pattern_api"]["GetLineLength"]
    add_seam = report["api_surface"]["pattern_api"]["AddSeamlinePairGroup"]
    get_line_doc = (get_line.get("doc_excerpt") or "").lower()
    add_seam_doc = (add_seam.get("doc_excerpt") or "").lower()

    report["capability_evidence"]["inner_shape_line_length"] = {
        "status": "evidence_present" if ("child" in get_line_doc or "inner" in get_line_doc) else "unknown",
        "basis": "installed_runtime_docstring_only",
    }
    report["capability_evidence"]["inner_shape_sewing"] = {
        "status": "evidence_present" if ("child" in add_seam_doc or "inner" in add_seam_doc) else "unknown",
        "basis": "installed_runtime_docstring_only",
    }

    pattern_info_obs = report["read_only_observations"]["pattern_input_information_0"]
    if pattern_info_obs.get("called") and pattern_info_obs.get("ok"):
        shape = pattern_info_obs.get("json_shape", {})
        report["gates"]["pattern_info_json_contract"] = (
            "pass" if shape.get("python_type") == "str" and shape.get("valid_json") else "fail"
        )
    else:
        report["gates"]["pattern_info_json_contract"] = "not_tested"

    report["gates"]["direct_sewing_api_present"] = "pass" if add_seam.get("available") else "fail"
    report["gates"]["stitch_inspection_api_present"] = (
        "pass" if report["api_surface"]["pattern_api"]["GetAllStitchProperty"].get("available") else "fail"
    )
    report["gates"]["export_zprj_on_export_api"] = (
        "pass" if report["api_surface"]["export_api"]["ExportZPrj"].get("available") else "fail"
    )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2, sort_keys=True)

    print("CLO contract probe complete.")
    print("Read-only: YES")
    print("Mutating API calls invoked: 0")
    print("Report:", OUTPUT_PATH)
    print("CLO version:", report["clo_version"].get("version_string"))
    print("Gates:", json.dumps(report["gates"], ensure_ascii=False, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
