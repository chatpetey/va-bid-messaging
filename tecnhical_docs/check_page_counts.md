# check_page_counts.py — Technical Summary

- Purpose: Scan `working_drafts` for files and, for PDFs, compute page counts.
- Key behavior:
  - Uses `pypdf` if available; if not installed, marks PDFs as `pypdf_missing` and sets pages to -1/None.
  - For each file in `working_drafts` (non-recursive), records `{file, pages, status}` where status ∈ {ok, unsupported, pypdf_missing}.
  - Produces a report with `page_counts`, `checked_at`, and `ok` flags and prints JSON to stdout.
  - Merges the report into `proposal_master_dashboard_skeleton.json` under `page_counts` (creating the JSON file if missing).
- Inputs/Outputs:
  - Input dir: `[ROOT - Technical Backend]/working_drafts`
  - Output JSON: `[ROOT - Technical Backend]/proposal_master_dashboard_skeleton.json`
  - Side effects: Updates dashboard JSON; no deletions.
- Operational notes:
  - Safe to run repeatedly; overwrites only the `page_counts` key.
  - Requires `pypdf` for page counting; without it, still runs but flags PDFs.
