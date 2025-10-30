# validate_filenames.py — Technical Summary

- Purpose: Enforce filename conventions within `working_drafts`.
- Key behavior:
  - Allowed patterns (case-insensitive):
    - `^vol1_technical_.*\.(md|docx|pdf)$`
    - `^vol2_pastperf_.*\.(md|docx|pdf)$`
    - `^RPRTech_Phase I-.*\.(pdf|xlsx)$`
  - Scans only the top level of `working_drafts` (ignores subdirectories).
  - Produces a `validation` report containing `files_seen` (with sizes), `issues` (files not matching patterns), `checked_at`, and `ok` boolean.
  - Merges the `validation` object into `proposal_master_dashboard_skeleton.json` under `filename_validation`.
  - Exits with code 0 if `ok` is true, else 1 (useful for CI).
- Inputs/Outputs:
  - Input dir: `[ROOT - Technical Backend]/working_drafts`
  - Output JSON: `[ROOT - Technical Backend]/proposal_master_dashboard_skeleton.json`
- Operational notes:
  - Idempotent merge behavior limited to `filename_validation` key.
  - Extend patterns by modifying `PATTERNS` in the script.
