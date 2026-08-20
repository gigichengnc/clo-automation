# Migration Plan

## Goal

Move from the current two-folder prototype layout to the multi-project architecture without breaking working DXF and CLO scripts.

---

## Rule: additive first, moving second

Phase 1 should add architecture and contracts without relocating existing runtime code.

Keep:

```text
DXF_AUTOMATION_V2/
CLO_Agent_v0.1/
```

working while new project directories are introduced.

---

## Step 1 — Add repository-level contracts

Add:

```text
ARCHITECTURE.md
KNOWN_ISSUES.md
AGENTS.md
shared/garment-schema/
projects/*/README.md
```

No import changes.

---

## Step 2 — Map existing code to future homes

Suggested mapping:

```text
DXF_AUTOMATION_V2/*
    → projects/dxf-generator/

CLO_Agent_v0.1/core/*
    → projects/clo-autosewing/src/

CLO_Agent_v0.1/tools/*
    → projects/clo-autosewing/tools/
```

Do not execute this move until current entry points and imports are inventoried.

---

## Step 3 — Extract shared contracts, not application code

Good candidates for `shared/`:

- garment schema
- semantic ID rules
- generic topology representation
- application-neutral validation result types

Bad candidates for `shared/`:

- CLO API imports
- `bpy`
- DXF writer calls
- application-specific object indices

---

## Step 4 — Add compatibility entry points

When code eventually moves, keep thin compatibility wrappers at old paths for one migration period when practical.

This allows existing commands and AI-agent instructions to continue working while tests are updated.

---

## Step 5 — Migrate fixtures before deleting legacy folders

A garment is migrated only when:

- source data is represented by the new contract
- its expected topology is tested
- new engine reproduces the human-approved result
- old and new outputs have been compared

---

## Step 6 — Remove legacy paths

Remove old folders only after all known garment workflows no longer depend on them.
