# Criticality Weights (d1) — Versioned Data Reference

This directory stores versioned data for the d1 criticality dimension.
The content is documentary and data-only: no runtime loading, no code, and no policy thresholds.

## Files

- `criticality_weights.v1.yaml`: first version of the criticality category table.

## Table Structure

The YAML table contains four parts:

- `table_id`, `version`, `status`, `scope`, `owner`, `created_at`
- `review_policy`
- `rules`
- `categories`

Each item in `categories` must include:

- `category_id`
- `label`
- `weight`
- `justification`
- `examples`

## Data Rules

- `weight` is mandatory and must stay in `[0.0, 1.0]`.
- `category_id` must be unique within a table version.
- `justification` must be explicit and technical, not generic.
- `examples` must illustrate realistic resource families.
- `fallback.category_id` must point to an existing category in the same file.

## Update Rules

- Do not modify `criticality_weights.v1.yaml` in place once released.
- Create a new file for any semantic or numerical change (for example: `criticality_weights.v2.yaml`).
- Record every new version in `CHANGELOG.md`.
- Add or update a decision entry in `DECISIONS.md` explaining why the change is needed.
- Keep this reference independent from matching, DTW, alert logic, and MITRE mapping logic.

## Out of Scope

The following are intentionally excluded from this directory:

- runtime parser/loader behavior
- Python implementation details
- alerting thresholds
- DTW or matching algorithm decisions
- MITRE-specific mapping rules
