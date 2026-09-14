"""
stretch.py — Tier 3 (🔴 Stretch)
ENPM 611 · Exercise 2 · Requirements Traceability

Goal: Extend the intermediate report to include merge-commit details, a Mermaid
Issue → PR → Commit flowchart, a gap-analysis section, and a console summary.

How to run:
    source .venv/bin/activate          # macOS / Linux  (.venv\Scripts\activate.bat on Windows)
    export GITHUB_TOKEN="your_token_here"
    python stretch.py

There are FOUR places in this file where you need to make a change.
Search for "# TODO" to find them.

Note: This file starts with the Intermediate tier already completed. The new
scaffolding is at the bottom of the main loop and in the final summary block.
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

TIMELINE_HEADERS = {
    **HEADERS,
    "Accept": "application/vnd.github.mockingbird-preview+json",
}

if not TOKEN:
    print("⚠  GITHUB_TOKEN not set — rate limits will apply.\n")

# ---------------------------------------------------------------------------
# Helper — fetch timeline  (Intermediate solution, already complete)
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
# Helper — fetch Pull Request details  (pre-wired — no TODO inside)
# ---------------------------------------------------------------------------

def fetch_pr(pr_number: int) -> dict:
    """Return the raw PR object from the GitHub API."""
    url = f"{API_URL}/repos/{REPO}/pulls/{pr_number}"
    resp = req.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"  ⚠  PR fetch failed for #{pr_number}: {resp.status_code}")
        return {}
    return resp.json()

# ---------------------------------------------------------------------------
# Helper — fetch commit message  (pre-wired — no TODO inside)
# ---------------------------------------------------------------------------

def fetch_commit_message(sha: str) -> str:
    """Return the first line of the commit message for the given SHA."""
    if not sha:
        return ""
    url = f"{API_URL}/repos/{REPO}/commits/{sha}"
    resp = req.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return ""
    data = resp.json()
    full_msg = data.get("commit", {}).get("message", "")
    return full_msg.splitlines()[0] if full_msg else ""

# ---------------------------------------------------------------------------
# Step 1 — Fetch the 20 most recently closed Issues
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
# Step 2 — Parse issues  (already complete)
# ---------------------------------------------------------------------------

issues = []
for item in raw_items:
    if "pull_request" in item:
        continue
    issues.append({
        "number": item["number"],
        "title":  item["title"],
        "state":  item["state"],
        "pr":     None,
    })

# ---------------------------------------------------------------------------
# Step 3 — Fetch timelines and link PRs + commits
# ---------------------------------------------------------------------------

print(f"Fetching timelines for {len(issues)} issues …")

# We'll accumulate Mermaid diagram lines here. Each traced issue adds two lines:
#   Issue node  →  PR node
#   PR node     →  Commit node
mermaid_lines = ["graph TD"]

for issue in issues:
    events = fetch_timeline(issue["number"])
    linked_pr = None

    # Find the first cross-referenced PR in the timeline  (Intermediate solution)
    for event in events:
        if (
            event.get("event") == "cross-referenced"
            and "pull_request" in event.get("source", {}).get("issue", {})
        ):
            pr_number = event["source"]["issue"]["number"]
            pr_title  = event["source"]["issue"]["title"]
            linked_pr = {
                "number":     pr_number,
                "title":      pr_title,
                "commit_sha": None,   # filled in below (TODO 1)
                "commit_msg": None,   # filled in below (TODO 1)
            }
            break

    if linked_pr:
        # ------------------------------------------------------------------
        # TODO (1 of 4) — Fetch the merge commit SHA and message
        # ------------------------------------------------------------------
        # Now that we have a PR number, fetch the full PR object by calling
        #   fetch_pr(linked_pr["number"])
        # The PR object has a field called  "merge_commit_sha"  which is the
        # Git SHA of the merge commit (or None if not yet merged).
        #
        # 1. Call fetch_pr() and store the result in a variable (e.g. `pr_obj`).
        # 2. Extract "merge_commit_sha" from pr_obj. Take only the first 7
        #    characters so the SHA is short (use Python slice  [:7] ).
        # 3. Call fetch_commit_message(sha) to get the first line of the message.
        # 4. Store both values in linked_pr["commit_sha"] and linked_pr["commit_msg"].
        #
        # HINT:
        #   pr_obj     = fetch_pr(linked_pr["number"])
        #   full_sha   = pr_obj.get("merge_commit_sha")   # may be None
        #   short_sha  = full_sha[:7] if full_sha else None
        #   ...
        # ------------------------------------------------------------------

        pr_obj = fetch_pr(linked_pr["number"])

        full_sha   = pr_obj.get("merge_commit_sha")   # may be None
        short_sha  = full_sha[:7] if full_sha else None

        commit_msg = fetch_commit_message(full_sha) if full_sha else None

        commit_sha = short_sha if short_sha else None
        commit_msg = commit_msg if commit_msg else None

        linked_pr["commit_sha"] = commit_sha
        linked_pr["commit_msg"] = commit_msg

        # ------------------------------------------------------------------
        # TODO (2 of 4) — Append Mermaid diagram nodes for this chain
        # ------------------------------------------------------------------
        # A Mermaid flowchart node looks like:
        #   NodeId["display label"]
        # An arrow between two nodes looks like:
        #   NodeId1 --> NodeId2
        #
        # For each traced issue, add TWO lines to  mermaid_lines:
        #
        #   Line 1 — Issue → PR arrow:
        #     f'  I{issue_number}["Issue #{issue_number} — {issue_title}"] --> PR{pr_number}["PR #{pr_number}"]'
        #
        #   Line 2 — PR → Commit arrow (only if commit_sha is not None):
        #     f'  PR{pr_number} --> C{short_sha}["commit {short_sha}"]'
        #
        # Replace the placeholder below with those two  mermaid_lines.append(...)
        # calls. Use real variable names (issue["number"], issue["title"], etc.).
        #
        # HINT: Mermaid node IDs must not contain spaces or special chars —
        #   using  I{number}  and  PR{number}  and  C{sha}  is safe.
        # ------------------------------------------------------------------

        mermaid_lines.append(f'  I{issue["number"]}["Issue #{issue["number"]} — {issue["title"]}"] --> PR{pr_number}["PR #{pr_number}"]')  # ← replace this
        if commit_sha:
            mermaid_lines.append(f'  PR{pr_number} --> C{short_sha}["commit {short_sha}"]')

    issue["pr"] = linked_pr

# ---------------------------------------------------------------------------
# Step 4 — Build gap analysis
# ---------------------------------------------------------------------------

traced   = sum(1 for i in issues if i["pr"] is not None)
untraced = len(issues) - traced

# ------------------------------------------------------------------
# TODO (3 of 4) — Collect untraced issues for the gap analysis
# ------------------------------------------------------------------
# Build a list called  untraced_issues  that contains only the issue
# dicts where  issue["pr"]  is None.
#
# The easiest way is a list comprehension:
#   untraced_issues = [i for i in issues if ...]
#
# Also build a list called  no_commit_prs  that contains the PR dicts
# (i.e. issue["pr"]) for traced issues where commit_sha is None or "???".
#   no_commit_prs = [i["pr"] for i in issues if i["pr"] and not i["pr"]["commit_sha"]]
#
# Replace the two empty lists below with those expressions.
# ------------------------------------------------------------------

untraced_issues = [i for i in issues if i["pr"] is None]  # ← replace with list comprehension
no_commit_prs   = [i["pr"] for i in issues if i["pr"] and not i["pr"]["commit_sha"]]  # ← replace with list comprehension

gap_rate = round((untraced / len(issues) * 100) if issues else 0)

# ---------------------------------------------------------------------------
# Step 5 — Console summary line
# ---------------------------------------------------------------------------

# ------------------------------------------------------------------
# TODO (4 of 4) — Print the summary line
# ------------------------------------------------------------------
# The README specifies this exact format:
#
#   Analyzed 20 issues: 14 traced, 6 untraced.
#   Gap rate: 30%. See trace_report.md for full report.
#
# (We write to report.html, not trace_report.md, so adjust the filename.)
#
# Use an f-string and the variables  len(issues), traced, untraced,
# gap_rate  that are already defined above.
# ------------------------------------------------------------------

print(f"Analyzed {len(issues)} issues: {traced} traced, {untraced} untraced.")
print(f"Gap rate: {gap_rate}%. See report.html for full report.")

# ---------------------------------------------------------------------------
# Step 6 — Render the full report
# ---------------------------------------------------------------------------

mermaid_graph = "\n".join(mermaid_lines) if traced > 0 else None

data = {
    "title":    "Requirements Traceability — Stretch Report",
    "analyzed": len(issues),
    "traced":   traced,
    "untraced": untraced,
    "issues":   issues,
    "mermaid":  mermaid_graph,
    "warning":  None,
}

renderer.render(data)
