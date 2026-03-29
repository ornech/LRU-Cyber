# d3 Temporal Specification v1

- `spec_id`: `d3_temporal_spec.v1`
- `version`: `v1`
- `status`: `provisional`
- `scope`: `CYBER-VPT d3 temporal dynamics`
- `owner`: `CYBER-VPT`

## 1. Objective and Invariant

`d3` represents temporal dynamics for a single fingerprint and is normalized in
`[0,1]`.

Interpretation rule:
- lower values indicate slower or less dense local dynamics,
- higher values indicate faster or denser local dynamics,
- this interpretation does not prove malicious intent on its own.

## 2. Normative Definitions

- `event`: one observable action record with a timestamp.
- `fingerprint`: stable identifier used to build local event history.
- `delta_t`: elapsed time between two consecutive events of the same
  fingerprint in ordered history.
- `local_window`: bounded recent history segment for the same fingerprint.
- `local_frequency`: density indicator derived from `delta_t` values over the
  local window.
- `insufficient_history`: explicit state where history is not sufficient to
  compute a stable temporal dynamic.

## 3. Measurement Convention

The retained convention is **hybrid**:
- primary signal from consecutive `delta_t` values,
- stabilization from a local sliding window for the same fingerprint.

Rationale:
- `delta_t` captures immediate acceleration/deceleration,
- windowing reduces single-point noise and transient spikes.

## 4. Required Inputs and Preconditions

Required inputs:
- timestamped events,
- fingerprint key,
- ordered local history for that fingerprint.

Preconditions:
- timestamps must be comparable,
- history ordering must be deterministic,
- history scope must remain fingerprint-local.

## 5. Calculation Rules

### 5.1 Nominal Case

When local history is sufficient:
- derive `delta_t` values from ordered consecutive events,
- derive a local frequency indicator from the configured local window,
- feed the indicator into the normalization function.

### 5.2 Cold Start and Insufficient History

Methodological rule:
- absence of history (`cold start`) must not be interpreted as low temporal
  dynamics.

Normative handling:
- represent this case as `insufficient_history` (or equivalent explicit label),
- do not assign a synthetic low-dynamics interpretation to this state,
- document downstream handling outside this specification scope.

### 5.3 Invalid or Unusable Temporal Input

- if timestamps are missing, non comparable, or inconsistent, the computation is
  not valid for `d3` under this specification,
- late or out-of-order events must be handled by explicit ordering rules before
  computing `d3`,
- `delta_t` equal to zero or near zero is allowed as an observable condition and
  must not be discarded silently.

## 6. Normalization Rule in [0,1]

`d3` is obtained through a bounded monotonic normalization of the local
frequency indicator.

Canonical form retained for v1 documentation:

`d3 = 1 / (1 + exp(-k * (f - f0)))`

with:
- `f`: local frequency indicator from hybrid measurement,
- `k`: slope parameter,
- `f0`: midpoint parameter.

Normative constraints:
- output must remain in `[0,1]`,
- function must be monotonic with respect to the retained frequency indicator,
- saturation behavior at extremes must be documented.

Parameter status:
- numeric values for `k`, `f0`, and any window-size constants are
  **provisional** in v1,
- they are not calibrated yet on an observed corpus.

## 7. Covered Temporal Profiles

This v1 specification covers:
- burst behavior,
- scripted regular execution,
- low-and-slow progression,
- legitimate periodic activity,
- sparse background activity.

Profile details are versioned in `temporal_profiles.v1.yaml`.

## 8. Limits and Non-Objectives

This specification does not define:
- runtime implementation details,
- DTW behavior,
- MITRE mapping behavior,
- alert thresholds or alerting policy,
- matching policy decisions.

`d3` is one dimension among five and must not be treated as a standalone
verdict.

## 9. Open Ambiguities (Intentionally Unresolved in v1)

- exact window parameterization strategy (time-based, count-based, or mixed
  configuration details),
- transition policy from `insufficient_history` to normal computation,
- precise handling policy for delayed ingestion and clock skew,
- operational boundary for "near-zero" `delta_t`,
- calibrated numeric values for normalization parameters.

These points remain open until corpus-based calibration is documented.
