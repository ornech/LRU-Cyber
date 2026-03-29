# d2 Entropy Reference - Versioned Documentary Reference

This directory stores versioned documentary references for the d2 (entropy)
dimension.

Scope is strictly documentary: no runtime loader behavior, no executable code,
no threshold policy, no DTW logic, no MITRE mapping logic, and no alerting
policy.

## Files

- `d2_entropy_spec.v1.md`: normative documentary specification for d2.
- `payload_field_rules.v1.yaml`: versioned tabular rules for `payload_bytes`
  composition by source family.

## Update Rules

- Do not modify released `v1` files in place for semantic changes.
- Create `vN` files for any normative or structural change.
- Record each new version in `CHANGELOG.md`.
- Add or update a decision entry in `DECISIONS.md` when semantic closure changes.

## Mandatory Methodological Rules

- d2 must remain deterministic and based only on observable cleartext fields.
- `payload_bytes` must remain an ordered concatenation of explicitly allowed
  fields.
- If useful content is not observable in cleartext, d2 is non calculable.
- No implicit decoding, decompression, or decryption is allowed.
- d2 is not sufficient by itself to conclude an attack.

## Out of Scope

- Python implementation details.
- Runtime parsing/loading automation.
- DTW internals, matching internals, MITRE internals, AlertEngine internals.
- Alert thresholds or operational policy decisions.
