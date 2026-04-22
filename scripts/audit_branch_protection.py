from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def github_get(url: str, token: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "catch-a-phish-devsecops",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit GitHub branch protection settings.")
    parser.add_argument("--repository", required=True, help="Repository in owner/name format.")
    parser.add_argument("--branch", required=True, help="Branch to audit.")
    parser.add_argument("--output", required=True, help="Path to write the JSON audit result.")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    result = {
        "repository": args.repository,
        "branch": args.branch,
        "status": "unknown",
        "protected": False,
    }

    if not token:
        result["status"] = "error"
        result["error"] = "GITHUB_TOKEN is not set."
    else:
        branch_url = f"https://api.github.com/repos/{args.repository}/branches/{args.branch}"
        try:
            branch = github_get(branch_url, token)
            result["protected"] = bool(branch.get("protected", False))
            if not result["protected"]:
                result["status"] = "missing"
            else:
                protection_url = f"{branch_url}/protection"
                protection = github_get(protection_url, token)
                result["status"] = "configured"
                result["required_pull_request_reviews"] = {
                    "enabled": protection.get("required_pull_request_reviews") is not None,
                    "required_approving_review_count": (
                        protection.get("required_pull_request_reviews") or {}
                    ).get("required_approving_review_count", 0),
                }
                result["required_status_checks"] = {
                    "enabled": protection.get("required_status_checks") is not None,
                    "strict": (protection.get("required_status_checks") or {}).get("strict", False),
                    "contexts": (protection.get("required_status_checks") or {}).get("contexts", []),
                }
                result["enforce_admins"] = bool((protection.get("enforce_admins") or {}).get("enabled", False))
                result["allow_force_pushes"] = bool((protection.get("allow_force_pushes") or {}).get("enabled", False))
                result["allow_deletions"] = bool((protection.get("allow_deletions") or {}).get("enabled", False))
                result["required_linear_history"] = bool((protection.get("required_linear_history") or {}).get("enabled", False))
        except urllib.error.HTTPError as exc:
            result["status"] = "error"
            result["error"] = f"GitHub API returned HTTP {exc.code}."
        except Exception as exc:  # pragma: no cover - defensive for CI runtime issues
            result["status"] = "error"
            result["error"] = str(exc)

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
