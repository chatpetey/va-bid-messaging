# update_status.py — Technical Summary

- Purpose: Generate lightweight HTML status dashboards from a set of JSON sources.
- Key behavior:
  - Reads multiple JSON files in the project root; for each, shows last modified time, size, and a short summary (`object · N keys`, `array · N items`, or error message).
  - Writes `dashboard.html` with a table of files and a timestamp.
  - Reads `proposal_master_dashboard_skeleton.json.status` and writes `volumes_status.html` showing Overall, Volume 1, and Volume 2 status.
  - CLI:
    - `--regen`: Regenerate both HTML files.
    - `--open`: Open `dashboard.html` in the default browser.
- Inputs/Outputs:
  - Inputs: the listed `*_skeleton*.json` files in `[ROOT - Technical Backend]`.
  - Outputs: `[ROOT - Technical Backend]/dashboard.html`, `[ROOT - Technical Backend]/volumes_status.html`.
- Operational notes:
  - Tolerant to missing/invalid JSON (shows error summary instead of crashing).
  - Non-destructive; regenerates HTML only.
