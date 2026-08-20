# Architecture & flow

Diagrams render natively on GitHub (Mermaid). All examples use the synthetic `demo` style.

## 1. What CLO_Agent does in one run (v0.1)

```mermaid
flowchart TD
    A[read command.json<br/>style + action] --> B[make backend<br/>REAL in CLO / MOCK off-CLO]
    B --> C[detect state<br/>pattern_count + sewing_groups]
    C -->|SAFE_CHECKPOINT| Z[report reached, do nothing]
    C -->|UNKNOWN| STOP1[SAFE STOP]
    C -->|FRESH or MIRRORED| D[scan patterns<br/>edge lengths + centroid]
    D --> E[identify by signature<br/>semantic IDs, no fixed index]
    E --> F{pieces present?}
    F -->|no| STOP2[SAFE STOP]
    F -->|yes, FRESH| G[checkpoint 00_fresh]
    G --> H[mirror BACK_* <br/>SymmetryPatternPiece]
    H --> I{count == expected?}
    I -->|no| STOP3[SAFE STOP]
    I -->|yes| J[checkpoint 01_mirrored]
    J --> K[plan safe seams<br/>closest-edge match + outer-edge guard]
    F -->|yes, MIRRORED| K
    K -->|any ambiguity / InnerShape| STOP4[SAFE STOP<br/>no seams created]
    K -->|all resolved| L[sew: AddSeamlinePairGroup + AddSeamlinePair]
    L --> M{count == expected?}
    M -->|no| STOP5[SAFE STOP]
    M -->|yes| N[checkpoint 02_safe_sewn]
    N --> O[write current_state.json]
    O --> P([SAFE CHECKPOINT])

    style P fill:#1b5e20,color:#fff
    style Z fill:#1b5e20,color:#fff
    style STOP1 fill:#b71c1c,color:#fff
    style STOP2 fill:#b71c1c,color:#fff
    style STOP3 fill:#b71c1c,color:#fff
    style STOP4 fill:#b71c1c,color:#fff
    style STOP5 fill:#b71c1c,color:#fff
```

## 2. State machine

The agent only ever moves forward one verified stage; any unexpected state is a hard stop.

```mermaid
stateDiagram-v2
    [*] --> FRESH
    FRESH: FRESH<br/>demo 4/0 · No.11 11/0
    MIRRORED: MIRRORED<br/>demo 5/0 · No.11 13/0
    SAFE_CHECKPOINT: SAFE_CHECKPOINT<br/>demo 5/3 · No.11 13/9
    UNKNOWN: UNKNOWN → SAFE STOP

    FRESH --> MIRRORED: mirror back pieces
    MIRRORED --> SAFE_CHECKPOINT: auto-sew safe seams
    SAFE_CHECKPOINT --> SAFE_CHECKPOINT: re-run = no-op
    FRESH --> UNKNOWN: counts don't match
    MIRRORED --> UNKNOWN: counts don't match
    SAFE_CHECKPOINT --> [*]
```

v0.2+ will extend the chain: `SAFE_CHECKPOINT → ARRANGED → SIMULATED → EXPORTED`.

## 3. Module architecture

```mermaid
flowchart LR
    subgraph entry
      CA[CLO_Agent.py<br/>orchestrator]
    end
    subgraph core
      API[clo_api.py<br/>ONLY CLO imports<br/>REAL + MOCK]
      SC[scanner.py]
      MA[matcher.py]
      MI[mirror.py]
      SE[sewing.py]
      VA[validator.py]
      CK[checkpoint.py]
      LO[logger.py]
    end
    subgraph data
      ST[styles/*.json]
      CMD[state/command.json]
      OUT[state/current_state.json]
    end
    CMD --> CA
    ST --> CA
    CA --> SC --> API
    CA --> MA
    CA --> MI --> API
    CA --> SE --> API
    CA --> VA
    CA --> CK --> API
    CA --> LO
    CA --> OUT
    API -.verified calls only.-> CLO[(CLO3D 2026<br/>pattern_api / import_api / export_api)]
```

Only `clo_api.py` touches CLO. Everything else is pure Python and testable off‑CLO (`selftest.py`).

## 4. How the two tools connect

```mermaid
flowchart LR
    DXF[garment DXF] --> GEN[DXF_AUTOMATION_V2<br/>patternlib: retag / segment / mirror]
    GEN --> META[metadata.json<br/>edges = endpoint identity]
    GEN --> SEAMS[seams.json]
    META --> BR[metadata_to_style.py]
    BR --> STY[CLO_Agent styles/&lt;id&gt;.json<br/>re-probe in CLO to lock]
    STY --> AG[CLO_Agent state machine]
    AG --> CLO[(CLO3D auto-sew)]
```

## 5. The InnerShape guard (why the yoke is excluded)

```mermaid
flowchart TD
    Q[want to sew edge X on pattern P] --> R{is length X in<br/>GetLineLength outer edges?}
    R -->|yes| S[sew it]
    R -->|no — only exists as InnerShape| T[SAFE STOP]
    style T fill:#b71c1c,color:#fff
    style S fill:#1b5e20,color:#fff
```

`GetLineLength` returns the **outer** boundary only. A CLO "Uniform Split" shows halves in the UI but
the API's outer edge is unchanged — the halves live in InnerShape. The agent can only sew what
`GetLineLength` reports, so it can never sew to an InnerShape edge; a missing expected outer edge is a
hard stop. This is the operationalised lesson from the failed yoke attempt.
