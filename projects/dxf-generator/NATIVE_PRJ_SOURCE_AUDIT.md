# Native PRJ Source Audit

## Purpose

Establish the provenance and observable structure of the two native garment-CAD project files delivered by the custom maker:

- `1.prj`
- `2.prj`

The PRJ binaries themselves remain private and are gitignored. This document records only reproducible metadata, hashes and pattern-record structure.

## Format identification

The uploaded files are **not CLO `.zprj` projects**. They are native garment-CAD `.prj` project files consistent with ET CAD / 布易科技 workflows.

External ET CAD documentation/tutorial material identifies `.prj` as the native pattern-making / grading project format. The binary files also contain ET-style garment metadata, material libraries, piece records and Chinese pattern annotations.

This matters because the PRJ is a richer native authoring source than a downstream DXF interchange file.

## Private-source fingerprints

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `1.prj` | 253179 | `26a4990f292d4693d9a04bbf9b38a055e08ce70cec3a6185b81d33bfc61c9c6e` |
| `2.prj` | 210943 | `95682f6c95e26c5a079a4a59c3f3bcc6017d1363c6dffeb8c1065c6dd40171d7` |

## Direct native metadata

### `1.prj`

Readable native metadata includes:

```text
season: 无季节
style: 1
creation: 2026/7/27/18/46
size: L
size count: L 总数: 1
```

Material vocabulary includes, among others:

```text
弹力面布
色丁里
粘朴
```

### `2.prj`

Readable native metadata includes:

```text
season: 无季节
style: 2
creation: 2026/7/27/18/47
size: L
size count: L 总数: 1
```

Material vocabulary includes, among others:

```text
米白色面
卡其色面
米白色里
卡其色里
粘朴
实样
```

The delivered native projects therefore contain one recorded size (`L`) each. They are not, as delivered, an independently observed multi-size graded set.

## Native pattern-record inventory

### `1.prj`

Twenty-seven actual piece/material records were recovered, representing fourteen unique piece names.

The multiplicity exactly matches the previously inspected `1.dxf` BLOCK structure.

| Piece | Native material instances |
| --- | --- |
| 后中 | 弹力面布 / 粘朴 / 色丁里 |
| 前中 | 弹力面布 / 粘朴 / 色丁里 |
| 袖子 | 弹力面布 |
| 前侧 | 弹力面布 / 粘朴 / 色丁里 |
| 后侧 | 弹力面布 / 粘朴 / 色丁里 |
| 落肩贴 | 弹力面布 / 粘朴 |
| 落肩条 | 弹力面布 |
| 绑带 | 弹力面布 |
| 飘带 | 弹力面布 |
| 后下裙 | 色丁里 / 弹力面布 |
| 前下裙 | 色丁里 / 弹力面布 |
| 口袋 | 色丁里 |
| 领子 | 弹力面布 / 粘朴 |
| 袖口 | 弹力面布 / 粘朴 |

Native symmetry flags are also present (`对称` / `不对称`) on the piece records.

### `2.prj`

Thirty-five actual piece/material records were recovered, representing twenty-one unique piece names.

Again, the multiplicity exactly matches the previously inspected `2.dxf` BLOCK structure.

| Piece | Native material instances |
| --- | --- |
| 捆条 | 米白色里 |
| 前中 | 米白色面 / 米白色里 |
| 右前侧 | 米白色面 / 米白色里 |
| 右边门襟实样 | 实样 / 实样 |
| 门襟贴 | 米白色面 / 粘朴 |
| 单杠 | 米白色面 / 米白色里 |
| 后侧 | 米白色面 / 米白色里 |
| 后中 | 米白色面 / 米白色里 |
| 袖子 | 米白色面 |
| 袖口 | 米白色面 / 粘朴 |
| 前下裙 | 卡其色里 / 卡其色面 |
| 后下裙 | 卡其色里 / 卡其色面 |
| 左前侧 | 米白色面 / 米白色里 |
| 耳仔 | 卡其色面 |
| 领坐 | 米白色面 / 粘朴 |
| 领子 | 米白色面 / 粘朴 |
| 口袋面 | 卡其色里 |
| 口袋底 | 卡其色里 |
| 口袋底层 | 卡其色面 |
| 开袋贴 | 粘朴 |
| 袋唇 | 卡其色面 / 粘朴 |

The PRJ also contains native construction annotations such as zipper and pocket-position text that were observed in the exported DXF family.

## Relationship to `1.dxf` / `2.dxf`

The native PRJ files and the previously inspected DXFs agree on all currently checked high-level identifiers:

| Property | `1.prj` ↔ `1.dxf` | `2.prj` ↔ `2.dxf` |
| --- | --- | --- |
| style ID | exact | exact |
| creation timestamp | exact | exact |
| sample size L | exact | exact |
| unique piece names | 14 / 14 | 21 / 21 |
| physical piece/material records | 27 / 27 | 35 / 35 |
| shell/lining/interfacing material variants | matching | matching |
| construction annotation family | matching | matching |

This is strong evidence that `1.dxf` and `2.dxf` are interchange exports/derivatives of the same native ET CAD projects delivered by the maker.

The exact export command/history has not yet been observed directly, so this is recorded as **strongly supported export lineage**, not a cryptographic proof of one specific export operation.

## Revised provenance hierarchy

Use this hierarchy going forward:

```text
HUMAN_CONFIRMED custom-maker delivery
        ↓
NATIVE_AUTHORING_SOURCE
  1.prj / 2.prj
        ↓
PRODUCTION_INTERCHANGE_EXPORT
  1.dxf / 2.dxf
        ↓
our forensic / semantic model
        ↓
our regenerated DXF / CLO adapters
        ↓
Claude-generated historical derivatives
```

`1.dxf` and `2.dxf` remain legitimate production-reference geometry because they represent the custom-maker patterns. They are no longer the highest-authority source when the corresponding native PRJ is available.

## Why PRJ matters for the factory-ready pilot

The factory-interchange pilot should now begin from the native maker source rather than treating the DXF as the ultimate master.

Recommended control experiment:

```text
native maker PRJ
      ├─ ET CAD official DXF export  -> control DXF
      └─ our semantic parser/model   -> our DXF export
                                      ↓
                           compare both against
                           the existing maker DXF
```

The pilot should check:

- piece count and material instances;
- geometry and scale;
- cut/sew line identity;
- grainlines;
- notches;
- internal construction marks;
- symmetry / mirror / quantity semantics;
- size identity;
- round-trip behavior in an independent garment CAD/CLO workflow.

## Current limitation

The ET PRJ binary geometry schema has not yet been fully decoded in this repository.

At this point we can directly recover:

- native metadata;
- material vocabulary;
- piece names;
- material role per piece record;
- symmetry flags;
- creation/style/size identity;
- textual construction annotations.

We have not yet claimed a complete parser for:

- all native curve records;
- grading-rule data;
- notch object types;
- grainline object records;
- sewing relationships;
- seam-allowance semantics.

Those should be recovered through ET CAD itself and/or a carefully verified binary parser, not guessed from byte patterns.

## Safety boundary

The private `.prj` files are proprietary garment-production assets and must not be committed to the repository or exposed in a future public showcase.
