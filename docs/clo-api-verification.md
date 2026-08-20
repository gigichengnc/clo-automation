# CLO API Verification

## Purpose

The real CLO adapter must match the exact CLO installation used to run automation.

Online documentation changes over time. Local shipped API stubs should be treated as the final runtime reference for the installed build.

---

## Current public documentation checkpoint

Checked: 2026-08-20

CLO's public API site lists:

- API/SDK v10.0.3
- CLO 2026.0.356 Official Release
- changelog entry `V10.0.3, July 2026`

This checkpoint is informative only. Record the actual local installation below before modifying the real backend.

---

## Local runtime record

```text
CLO application version: TODO
CLO build:               TODO
SDK/API version:         TODO
ApiStubFiles path:       TODO
Operating system:        TODO
Python/runtime mode:     TODO
Verified on:             TODO
```

---

## Contract checklist

### Pattern inspection

- [ ] pattern count method/signature
- [ ] pattern name method/signature
- [ ] pattern input information return type
- [ ] outer-line enumeration
- [ ] internal-line enumeration
- [ ] line length query
- [ ] pattern position / centroid information

### Sewing

- [ ] create sewing pair/group signature
- [ ] direction/orientation representation
- [ ] internal-line sewing support
- [ ] sewing-group enumeration
- [ ] retrieve sewing partners
- [ ] delete/rollback sewing operation if verification fails

### Pattern manipulation

- [ ] symmetry/mirror signature
- [ ] returned new pattern identity/index
- [ ] position/move signature

### Project/export

- [ ] save/export project signature
- [ ] mesh export formats required for Blender
- [ ] headless/UI behavior if relevant

---

## Non-destructive contract probe

Before executing sewing automation, build a probe that:

1. loads/imports nothing destructive
2. prints the detected CLO/API version if available
3. checks required API methods exist
4. calls read-only representative methods on a known test project
5. records Python return types
6. exits without changing seams or geometry

Expected output should be machine-readable so it can be compared after CLO upgrades.

Example shape:

```json
{
  "clo_version": "...",
  "checks": {
    "pattern_information": {
      "available": true,
      "return_type": "..."
    },
    "sewing_create": {
      "available": true,
      "signature_verified_from_stub": true
    }
  }
}
```

---

## Upgrade rule

When CLO is upgraded:

1. run contract probe
2. diff results
3. inspect new shipped stubs/changelog
4. update adapter if necessary
5. run regression fixtures before running production garments
