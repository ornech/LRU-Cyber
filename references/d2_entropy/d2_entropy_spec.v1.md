# d2 Entropy Specification v1

- `spec_id`: `d2_entropy_spec.v1`
- `version`: `v1`
- `status`: `accepted`
- `scope`: `CYBER-VPT d2 entropy`
- `owner`: `CYBER-VPT`

## 1. Role of d2 in 5D Vectorization

`d2` measures the information disorder of observed content for one event source,
normalized in `[0,1]`.

`d2` is one dimension among five and must not be treated as a standalone
verdict.

## 2. Canonical Formula

Canonical form retained:

`d2 = H(payload_bytes) / 8`

where `H` is Shannon entropy computed on bytes.

## 3. Strict Definition of `payload_bytes`

`payload_bytes` is an ordered concatenation of explicitly authorized fields,
selected by source family rules.

Only fields observed in cleartext in the source are eligible.

## 4. Documentary Determinism Rule

d2 must be derived only from explicit and versioned documentary rules.

No implicit protocol intuition is allowed when the required information is not
actually observable in the source.

## 5. Non-Calculability Cases

d2 is non calculable when useful content is not observable in cleartext in the
source.

If no included field is observable in cleartext for the source family rule, d2
is non calculable.

## 6. Explicit Prohibitions

The following operations are prohibited for d2 computation:

- implicit decoding
- implicit decompression
- implicit decryption

## 7. Interpretation Limits

A high d2 value indicates high information density in observed form only.

High entropy can come from benign binary or encoded content and is not a proof
of malicious behavior by itself.

Short or partial content reduces interpretation strength.

## 8. What d2 Does Not Measure

d2 does not measure:

- danger level
- attacker intent
- criticality (`d1`)
- rarity (`d5`)

d2 alone is not sufficient to conclude an attack.

## 9. Traceability Link to `payload_field_rules.v1.yaml`

The authoritative tabular rules for source families, included/excluded fields,
concatenation order, and observable non-calculability conditions are versioned
in `references/d2_entropy/payload_field_rules.v1.yaml`.
