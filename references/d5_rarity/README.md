# d5 Rarity Reference — Versioned Documentary Reference

This directory contains the authoritative versioned documentary reference for
the `d5` rarity dimension.

Scope is strictly documentary. No runtime behavior, benchmark logic,
calibration workflow, test execution policy, DTW internals, or alerting policy
is defined here.

`d5` remains a scalar in `[0,1]`. The `never_seen` case remains inside the
same scalar continuum and is represented by the maximum anchor. Projection is
ordinal, documentary, and bounded with fixed anchors.

This reference does not define `Fingerprint` as a transverse object. It only
covers the minimal relation "rarity of an observed fingerprint" for `d5`.

Temporal horizon and forgetting/aging policy are explicitly out of `v1`.

## Files

- `references/d5_rarity/d5_rarity_spec.v1.md`: normative documentary
  specification for `d5`.
- `references/d5_rarity/rarity_projection.v1.yaml`: versioned documentary table
  for ordinal classes, fixed anchors, and semantic input/MITRE correspondence.

## Update Rules

- Do not modify released `v1` files in place for semantic changes.
- Create `vN` files for any structural or normative change.
- Record each new version in `CHANGELOG.md`.
- Add or update a decision entry in `DECISIONS.md` for structural choices.

## Mandatory Methodological Rules

- `d5` remains scalar and bounded in `[0,1]`.
- `never_seen` remains in the same scalar continuum and maps to the maximum
  anchor.
- Projection remains ordinal, documentary, bounded, and fixed-anchor.
- Counting universe remains explicit and unique in `v1`: by source family or
  protocol.
- Counting granularity remains explicit and unique in `v1`: observed action
  occurrence.
- Input/MITRE symmetry for `d5` remains semantic and documentary.
- `d5` alone is not sufficient to conclude an attack.

## Out of Scope

- Full transverse definition of `Fingerprint`.
- Runtime estimator design or implementation.
- Empirical calibration workflow and benchmark logic.
- Execution-time validation or test procedures.
- DTW internals, matching internals, or AlertEngine internals.
- Temporal horizon policy details (out of `v1`).
- Forgetting/aging policy details (out of `v1`).
