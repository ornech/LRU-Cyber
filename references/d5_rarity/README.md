# d5 Rarity Reference — Versioned Documentary Reference

This directory is the authoritative documentary reference for `d5` in CYBER-VPT.

The scope is documentary only.
No runtime estimator, no benchmark procedure, no DTW behavior, and no alerting
policy is defined in this folder.

`d5` remains a scalar rarity value in `[0,1]`.
`never_seen` remains inside this same continuum and maps to the maximum anchor.
Projection remains ordinal and documentary with fixed anchors.

This reference does not define a full transverse `Fingerprint` model.
It only documents the minimal relation: rarity of an observed fingerprint for
dimension `d5`.

Temporal horizon and forgetting/aging policy remain out of `v1`.

## Files

- `references/d5_rarity/d5_rarity_spec.v1.md`
  Normative documentary specification for `d5`.
- `references/d5_rarity/rarity_projection.v1.yaml`
  Versioned documentary table for classes, anchors, and semantic
  input/MITRE correspondence.

## Update Rules

- Do not rewrite released `v1` files for semantic changes.
- Create a new `vN` file for any structural or normative update.
- Record each new version in `CHANGELOG.md`.
- Add or update the associated decision entry in `DECISIONS.md`.

## Mandatory Methodological Rules

- `d5` stays scalar and bounded in `[0,1]`.
- `never_seen` stays within the same scalar continuum and maps to the maximum
  anchor.
- Projection stays ordinal, documentary, bounded, and fixed-anchor.
- Counting universe for `v1` stays explicit: by source family or protocol.
- Counting granularity for `v1` stays explicit: observed action occurrence.
- Input/MITRE symmetry for `d5` stays semantic and documentary.
- `d5` alone is never sufficient to conclude an attack.

## Out of Scope

- Full transverse definition of `Fingerprint`.
- Runtime estimator design or implementation.
- Empirical calibration workflow and benchmark methodology.
- Execution-time validation procedures.
- DTW internals, matching internals, or AlertEngine internals.
- Temporal horizon policy details (out of `v1`).
- Forgetting/aging policy details (out of `v1`).
