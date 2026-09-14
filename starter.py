"""
starter.py — Tier 1 (🟢 Starter)
ENPM 611 · Exercise 2 · Requirements Traceability

Goal: Fetch the 20 most recently closed Issues from psf/requests and display
them in an HTML report.

How to run:
    1. Activate the virtual environment:
           source .venv/bin/activate          # macOS / Linux
           .venv\Scripts\activate.bat         # Windows CMD
    2. Set your GitHub token (see README.md § Setup):
           export GITHUB_TOKEN="your_token_here"
    3. Run this script:
           python starter.py
    4. A browser window will open automatically with the report.

There are TWO places in this file where you need to make a change.
Search for "# TODO" to find them.
"""

import os
import renderer  # our shared HTML renderer — no need to modify it

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO    = "psf/requests"
API_URL = "https://api.github.com"

# Read the GitHub token from the environment so it is never hard-coded.
TOKEN   = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

if not TOKEN:
    print("⚠  GITHUB_TOKEN not set — you will hit the 60 req/hour rate limit quickly.")
    print("   See README.md § Setup for instructions.\n")

# ---------------------------------------------------------------------------
# Step 1 — Fetch the 20 most recently closed Issues
# ---------------------------------------------------------------------------

import requests as req  # the pip package, not our repo variable

response = req.get(
    f"{API_URL}/repos/{REPO}/issues",
    params={"state": "closed", "per_page": 20},
    headers=HEADERS,
)

if response.status_code != 200:
    print(f"❌  GitHub API returned {response.status_code}: {response.text}")
    raise SystemExit(1)

raw_items = response.json()

# ---------------------------------------------------------------------------
# Step 2 — Parse the response into our issue list
# ---------------------------------------------------------------------------
# The GitHub API mixes Issues AND Pull Requests in the same endpoint.
# We need to keep only real Issues.

issues = []

for item in raw_items:

    # ------------------------------------------------------------------
    # TODO (1 of 2) — Filter out Pull Requests
    # ------------------------------------------------------------------
    # The GitHub API returns both Issues AND Pull Requests from this
    # endpoint. Pull Requests have an extra key called "pull_request"
    # in the response dict. Add a check here to skip any item that has
    # that key so only real Issues end up in our list.
    #
    # HINT: use  `if "pull_request" in item:`  and then `continue`
    # ------------------------------------------------------------------

    if "pull_request" in item:
        continue

    # Build a dict for this issue.
    # The "state" field is currently hardcoded to "?" — fix that in TODO 2.
    issue = {
        "number": item["number"],
        "title":  item["title"],

        # ------------------------------------------------------------------
        # TODO (2 of 2) — Fill in the correct state
        # ------------------------------------------------------------------
        # Right now every issue shows "?" as its state. The API response
        # includes the real state ("open" or "closed") in the item dict.
        #
        # HINT: the key is just called  "state"  — same name as our field.
        # Replace the "?" below with the correct expression.
        # ------------------------------------------------------------------
        "state": item["state"],

        "pr": None,  # No PR info at this tier — leave this as None
    }
    issues.append(issue)

# ---------------------------------------------------------------------------
# Step 3 — Render the HTML report
# ---------------------------------------------------------------------------

data = {
    "title":    "Requirements Traceability — Starter Report",
    "analyzed": len(issues),
    "traced":   0,      # No tracing at this tier
    "untraced": len(issues),
    "issues":   issues,
    "mermaid":  None,   # No diagram at this tier

    # This warning banner disappears once both TODOs are complete because:
    #   - TODO 1 removes PRs from the list (reducing the count)
    #   - TODO 2 fixes the "?" state labels
    # Once the numbers look right and states show "closed", you're done!
    "warning": (
        "PRs may be mixed into this list and state labels show '?' — "
        "complete the two TODOs in starter.py to fix this."
    ),
}

renderer.render(data)
