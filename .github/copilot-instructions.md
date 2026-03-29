# Copilot Instructions — CYBER-VPT

## Project overview

**CYBER-VPT** (Cyber Vector Predictive Trajectory) detects cyber attacks predictively by:

1. Projecting raw security events into a 5-dimensional vector space `[0,1]^5`.
2. Chaining those vectors into per-fingerprint trajectories.
3. Comparing live trajectories against MITRE ATT&CK reference models using DTW.
4. Raising an alert when the convergence score exceeds a threshold — _before_ the final malicious step occurs.

The project is currently in an **early implementation phase** with domain contracts and
core data structures already in place. Foundational architecture remains documented in
`README.md`, `projet.plantuml`, `vecteurs.md`,
`specification_homogeneisation.md`, `explication_convergence.md`, and `lexique.md`.

---

## Build & test commands

```bash
# Install dependencies (always run first)
pip install -r requirements.txt

# Run all tests
pytest -q

# Lint
pip install flake8
flake8 src/
```

No custom pytest markers exist yet. The CI workflow (`.github/workflows/copilot-setup-steps.yml`) also uses `pytest -q`.

---

## Repository structure

```
README.md                         # Functional & technical specification (CdCFT)
requirements.txt                  # numpy, scipy, scikit-learn, pandas, pytest
projet.plantuml                   # Full UML class diagram of planned architecture
vecteurs.md                       # 5D vector dimension formulas
specification_homogeneisation.md  # Symmetry and normalisation rules for all 5 dims
explication_convergence.md        # DTW matching, scoring, and alert logic
lexique.md                        # Domain glossary
src/                              # Python source (domain contracts + base implementations)
tests/                            # Unit tests (contracts for implemented baseline)
.github/
  copilot-instructions.md         # This file
  pyproject.toml                  # Package metadata (cyber-vpt)
  workflows/copilot-setup-steps.yml
```

Current implemented baseline includes:

- `src/cyber_vpt/vector5d.py` with contract tests in `tests/test_vector5d.py`
- `src/cyber_vpt/match_result.py` with contract tests in `tests/test_match_result.py`
- `src/cyber_vpt/archived_profile.py` with contract tests in
  `tests/test_archived_profile.py`
- Versioned `d1` reference table in
  `references/criticality/criticality_weights.v1.yaml`

---

## Planned module architecture

All modules live under `src/`. Implement in this order to respect dependencies:

| Layer                 | Classes                                                                                               | Responsibility                                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **1 · Ingestion**     | `RawEvent`, `Fingerprint`, `FingerprintResolver`, `FingerprintIndex`, `BloomFilter`, `CountMinSketch` | Parse raw events; produce stable, hash-based fingerprints                                                |
| **2 · Vectorisation** | `ActionSemantics`, `Vector5D`, `Vectorizer`                                                           | Map any event to a point in `[0,1]^5`                                                                    |
| **3 · Trajectories**  | `Commit`, `Trajectory`, `TrajectoryStore`                                                             | Maintain ordered, hash-chained sequences per fingerprint (LRU two-tier: RAM <-> archive)                 |
| **4 · Matching**      | `TechniqueModel`, `MitreRepository`, `DTWMatcher`, `MatchResult`                                      | DTW distance against MITRE ATT&CK sequences; output `normalized_distance` in `[0,1]`                     |
| **5 · Alerting**      | `AlertEngine`, `AlertLevel`                                                                           | Apply threshold policy to `MatchResult`; emit alerts                                                     |
| **6 · Archive**       | `ArchivedProfile`, `ArchiveManager`                                                                   | Summarize inactive trajectories as statistical archived profiles `(mu, Sigma, n, first_seen, last_seen)` |

**Cross-cutting rule:** `DTWMatcher` is pure computation (no policy). `AlertEngine` is pure policy (no arithmetic). Never merge the two.

---

## Non-negotiable invariants

These must be preserved by every function, test, and data class:

1. **`Vector5D` unit cube:** every component `d1...d5` must be in `[0.0, 1.0]`. Raise `ValueError` on construction if any component is outside this range or non-finite.
2. **Normalized distance:** `DTWMatcher` always returns `normalized_distance` in `[0.0, 1.0]`, clamped as `min(raw / d_max, 1.0)`.
3. **Match score:** `match_score = 1.0 - normalized_distance` — never computed independently.
4. **`ArchivedProfile` structure:** exactly `(mu: ndarray shape (5,), Sigma: ndarray shape (5,5), n: int, first_seen: datetime, last_seen: datetime)`.
5. **`Commit` hash chain:** each commit stores `previous_hash`; chain integrity must be verifiable.
6. **Alert thresholds:** `match_score < 0.50` -> `NONE`; `0.50 <= score < 0.80` -> `WATCH`; `score >= 0.80` -> `CRITICAL`.
7. **Symmetry rule:** `d_i` for input events and the corresponding `d_i` in a `TechniqueModel` must use identical scales, tables, and normalisation methods (see `specification_homogeneisation.md`).

---

## 5D vector dimension reference

| Dim  | Name        | Formula                                          | Bounds   |
| ---- | ----------- | ------------------------------------------------ | -------- |
| `d1` | Criticality | `W(resource) / W_max`                            | `[0, 1]` |
| `d2` | Entropy     | `H(payload) / 8` (Shannon, byte distribution)    | `[0, 1]` |
| `d3` | Frequency   | sigmoid of `1/delta_t` relative to local history | `[0, 1]` |
| `d4` | Intensity   | weight of HTTP method / protocol                 | `[0, 1]` |
| `d5` | Rarity      | bounded score via Count-Min Sketch               | `[0, 1]` |

---

## Design decisions

- **DTW over Euclidean distance:** handles "low and slow" attacks where timing varies significantly across replays.
- **Bloom filter fast-path:** O(1) fingerprint existence check before accessing `FingerprintIndex`.
- **Count-Min Sketch for `d5`:** gives a bounded, probabilistic estimate of fingerprint frequency without unbounded memory growth.
- **LRU two-tier storage:** active trajectories in RAM at full resolution; inactive ones summarized into `ArchivedProfile` statistical objects `(mu, Sigma, n, first_seen, last_seen)`.
- **`completion_probability` caveat:** this field in `MatchResult` is an _advance fraction estimate_, not a legal proof of attack intent. Document this wherever the field is used.

---

## Coding conventions

- **PEP 8** strictly enforced (`flake8 src/`). Max line length 99 chars.
- **Commit messages in English.** Code comments and docstrings may be in French (team convention).
- **Unit tests required** for every new or modified function.
- **MITRE ATT&CK data** must include `source_version` (e.g. `"ATT&CK v15.1"`) in any `TechniqueModel` or related fixture.
- **No ML model in baseline:** all matching must be deterministic (DTW + thresholds) before any learned component is introduced.

---

## Known open questions — do not silently invent values

- `d3` sigmoid parameters (`k` slope, `f0` midpoint): not calibrated yet; add a `TODO` comment and document assumptions when implementing.
- `W` criticality calibration for `d1`: a first versioned table exists in
  `references/criticality/criticality_weights.v1.yaml`; update by introducing
  a new versioned reference file when recalibration is required.
- `d_max` for distance normalisation: derive empirically from a representative run or document the chosen constant with a justification comment.
- `ArchiveManager.restore_or_split` semantics: undefined; do not implement until explicitly specified.
