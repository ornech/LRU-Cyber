# d3 Temporal Reference — Versioned Specification Data

This directory stores versioned documentation and data references for the d3
(dynamique temporelle) dimension.

Scope is strictly documentary: no runtime loader behavior, no executable
implementation, no DTW policy, no MITRE mapping policy, and no alerting policy.

## Files

- `d3_temporal_spec.v1.md`: normative specification for d3 temporal dynamics.
- `temporal_profiles.v1.yaml`: versioned profile table used as a documentary
  reference for expected temporal regimes.

## Update Rules

- Do not modify a released `v1` file in place for semantic changes.
- Create `vN` files for any structural or normative change.
- Record each new version in `CHANGELOG.md`.
- Add or update a decision entry in `DECISIONS.md` for structural choices.

## Mandatory Methodological Rule

Cold start (absence of history) must never be interpreted as low temporal
dynamics. It is an explicit state of insufficient history.

## Out of Scope

- Python code or executable implementation.
- Runtime loading or automation details.
- DTW internals, matching internals, MITRE internals, AlertEngine internals.
- Alert thresholds or operational policy decisions.
