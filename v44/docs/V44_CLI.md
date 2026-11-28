# V44 CLI reference

The CLI uses Python 3.10+ and the Python standard library. Install the pinned test dependency only when running the test suite.

## Install and test

    python -m pip install -r .\v44\tests\requirements-test.txt
    python -m unittest discover -s .\v44\tests -v

All file arguments are project-root-relative. Absolute paths, parent traversal, backslash-separated paths, symlink escapes, duplicate JSON keys, non-standard JSON constants, and inputs larger than 1 MiB are rejected.

## Commands

    python .\v44\tools\v44.py doctor --root C:\Path\To\YourGame
    python .\v44\tools\v44.py validate-study --root C:\Path\To\YourGame --study .codex\feedback\study.json
    python .\v44\tools\v44.py validate-data --root C:\Path\To\YourGame --study .codex\feedback\study.json --data .codex\feedback\coded-data.json
    python .\v44\tools\v44.py audit --root C:\Path\To\YourGame --study .codex\feedback\study.json --output .codex\reports\feedback-study-audit.json
    python .\v44\tools\v44.py summarize --root C:\Path\To\YourGame --study .codex\feedback\study.json --data .codex\feedback\coded-data.json --output .codex\reports\feedback-summary.json

## Output and limitations

- validate-study checks the declared plan and its research/privacy gates.
- validate-data checks the coded dataset against the plan, vocabulary, time window, and unique study-scoped references.
- audit writes a study-readiness report and neutral-prompt warnings.
- summarize emits descriptive category counts and suppresses groups smaller than the study's threshold. Overall sample size is shown only as a broad band.
- 0 means validation/report generation succeeded; 1 means invalid content; 2 means path, input, or runtime error.

V44 does not collect feedback, inspect raw text, detect PII, contact Roblox, authenticate evidence references, verify consent, prove deletion, infer population sentiment, calculate statistical confidence, create external backlog tasks, or approve a change. It only checks supplied local metadata. Do not copy raw feedback into the coded dataset. Human review and the original authorized evidence remain necessary.
