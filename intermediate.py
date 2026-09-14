"""
intermediate.py — Tier 2 (🟡 Intermediate)
ENPM 611 · Exercise 2 · Requirements Traceability

Goal: For each of the 20 closed Issues, search its timeline for a linked Pull
Request and produce a traced / untraced report.

How to run:
    source .venv/bin/activate          # macOS / Linux  (.venv\Scripts\activate.bat on Windows)
    export GITHUB_TOKEN="your_token_here"
    python intermediate.py

There are THREE places in this file where you need to make a change.
Search for "# TODO" to find them.

Note: This file starts with the Starter tier already completed so you can focus
entirely on the new traceability logic.
"""

import os
import requests as req
import renderer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO    = "psf/requests"
API_URL = "https://api.github.com"

TOKEN   = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

if not TOKEN:
    print("⚠  GITHUB_TOKEN not set — rate limits will apply.\n")

# ---------------------------------------------------------------------------
# Timeline headers
# The GitHub timeline API requires a special "Accept" header to be enabled.
# ---------------------------------------------------------------------------

TIMELINE_HEADERS = {
    **HEADERS,  # include the Authorization header from above

    # ------------------------------------------------------------------
    # TODO (1 of 3) — Add the required Accept header
    # ------------------------------------------------------------------
    # The timeline API is a GitHub preview feature. Without the correct
    # Accept header the response will be empty or an error.
    #
    # Add this key-value pair inside this dict:
    #   "Accept": "application/vnd.github.mockingbird-preview+json"
    #
    # HINT: dictionary syntax is  "key": "value"  — add it after the
    # **HEADERS line above, separated by a comma.
    # ------------------------------------------------------------------
    
    "Accept": "application/vnd.github.mockingbird-preview+json"
}

# ---------------------------------------------------------------------------
# Helper — fetch the timeline for a single issue
# ---------------------------------------------------------------------------

def fetch_timeline(issue_number: int) -> list:
    """Return the raw list of timeline events for the given issue number."""
    url = f"{API_URL}/repos/{REPO}/issues/{issue_number}/timeline"
    resp = req.get(url, headers=TIMELINE_HEADERS)
    if resp.status_code != 200:
        print(f"  ⚠  Timeline fetch failed for #{issue_number}: {resp.status_code}")
        return []
    return resp.json()

# ---------------------------------------------------------------------------
# Step 1 — Fetch the 20 most recently closed Issues  (same as Starter tier)
# ---------------------------------------------------------------------------

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
# Step 2 — Parse issues (Starter solution, already complete)
# ---------------------------------------------------------------------------

issues = []
for item in raw_items:
    if "pull_request" in item:
        continue
    issues.append({
        "number": item["number"],
        "title":  item["title"],
        "state":  item["state"],
        "pr":     None,   # will be filled in below
    })

# ---------------------------------------------------------------------------
# Step 3 — For each Issue, search its timeline for a linked PR
# ---------------------------------------------------------------------------

print(f"Fetching timelines for {len(issues)} issues — this may take ~{len(issues)*2}s …")

for issue in issues:
    events = fetch_timeline(issue["number"])
    linked_pr = None  # default: no PR found

    for event in events:

        # ------------------------------------------------------------------
        # TODO (2 of 3) — Identify a cross-referenced Pull Request event
        # ------------------------------------------------------------------
        # Timeline events come in many types. We only care about events
        # where:
        #   - event["event"]  equals  "cross-referenced"   AND
        #   - the source of the cross-reference is a Pull Request, which
        #     means  event["source"]["issue"]["pull_request"]  exists
        #
        # Write an `if` condition that checks BOTH of those things.
        # If true, set  linked_pr  (defined just above this loop) to the
        # result of TODO 3 and then `break` out of the loop.
        #
        # HINT skeleton:
        #   if event.get("event") == "..." and "..." in event["source"]["issue"]:
        # ------------------------------------------------------------------
        if event.get("event") == "cross-referenced" and "pull_request" in event["source"]["issue"]:
            linked_pr = event["source"]["issue"]

            # --------------------------------------------------------------
            # TODO (3 of 3) — Extract the PR number and title
            # --------------------------------------------------------------
            # Inside event["source"]["issue"] you will find the same
            # structure as a regular issue dict, including "number" and
            # "title". Pull Requests also have a "pull_request" key there.
            #
            # Set linked_pr to a dict with keys "number", "title", and
            # leave "commit_sha" and "commit_msg" as None (those are for
            # the Stretch tier).
            #
            # HINT: the PR number lives at
            #   event["source"]["issue"]["number"]
            # and the title at
            #   event["source"]["issue"]["title"]
            # --------------------------------------------------------------
            linked_pr = {
                "number":     event["source"]["issue"]["number"],
                "title":      event["source"]["issue"]["title"],
                "commit_sha": None,
                "commit_msg": None,
            }
            break

    issue["pr"] = linked_pr

# ---------------------------------------------------------------------------
# Step 4 — Tally and render
# ---------------------------------------------------------------------------

traced   = sum(1 for i in issues if i["pr"] is not None)
untraced = len(issues) - traced

print(f"\nAnalyzed {len(issues)} issues: {traced} traced, {untraced} untraced.")

data = {
    "title":    "Requirements Traceability — Intermediate Report",
    "analyzed": len(issues),
    "traced":   traced,
    "untraced": untraced,
    "issues":   issues,
    "mermaid":  None,
    "warning":  (
        "All issues show as UNTRACED — complete the three TODOs to link PRs."
    ) if traced == 0 else None,
}

renderer.render(data)
