# d5 Rarity Specification v1

- `spec_id`: `d5_rarity_spec.v1`
- `version`: `v1`
- `status`: `accepted`
- `scope`: `CYBER-VPT d5 rarity`
- `owner`: `CYBER-VPT`

## 1. Role of d5 in 5D vectorization

`d5` represents the rarity of an observed fingerprint in the 5D vector.
Its value is scalar and bounded in `[0,1]`.

`d5` remains one dimension among five.
It must not be interpreted as a standalone verdict.

## 2. Normative minimal definition

For `v1`, the retained normative definition is:

- `d5` measures rarity of an observed fingerprint relative to a documentary
  counting universe.
- Full transverse definition and construction of `Fingerprint` are out of
  scope for this specification.

## 3. Counting universe

For `v1`, the counting universe is fixed as:

- by source family or protocol.

Rarity must always be interpreted relative to that universe.

## 4. Counting granularity

For `v1`, counting granularity is fixed as:

- observed action occurrence.

## 5. Treatment of `never_seen`

For `v1`, `never_seen` is represented by the maximum value of the scalar
rarity continuum in `[0,1]`.

No hidden flag, side channel, or out-of-range state is introduced.

## 6. Canonical projection

The canonical retained projection is:

- ordinal documentary projection with fixed anchors.

This defines a bounded documentary mapping in `[0,1]`.
It does not impose a runtime estimator law.

## 7. Input / MITRE symmetry

For `d5`, retained symmetry is semantic and documentary:

- input and MITRE must use the same rarity vocabulary and class table,
- this does not require empirical frequency symmetry between input and MITRE.

## 8. Interpretation limits

Methodological limits for `v1`:

- `d5` alone is not sufficient to conclude an attack,
- rarity can have legitimate fingerprint renewal causes, including:
  - browser change,
  - system update,
  - legitimate new equipment,
  - other observable legitimate renewals.

## 9. What d5 does not measure

`d5` does not measure:

- attacker intent,
- legal legitimacy,
- business criticality,
- attack certainty,
- alert policy decisions.

## 10. Out of v1

The following items are intentionally out of `v1`:

- temporal horizon policy,
- forgetting/aging policy,
- runtime estimator selection,
- implementation and execution behavior.

## 11. YAML traceability

The authoritative documentary table for classes, anchors, `never_seen` policy,
and semantic input/MITRE correspondence is versioned in:

`references/d5_rarity/rarity_projection.v1.yaml`
