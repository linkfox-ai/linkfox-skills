#!/usr/bin/env python3
"""
SB Budget Rules List - linkfox-amazon-ads-manager
================================================

GET sb/budgetRules (Amazon Ads).

Usage:
  python list_budget_rules.py '<JSON params>'

Required:
  profileId (number), region (NA/EU/FE)

Optional:
  nextToken    (string) pagination token
  fetchAll     (bool) default true, auto-follow nextToken

Example:
  python list_budget_rules.py '{"profileId":123,"region":"NA"}'
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import (  # noqa: E402
    ensure_auth_skill_available,
    get_access_token,
    parse_argv_params,
    require_fields,
    _developer_proxy_call,
    emit_result,
    lf_inline_flag,
)

ENTITY_PATH = "sb/budgetRules"


def main() -> None:
    params = parse_argv_params(__doc__)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    require_fields(params, ["profileId", "region"])

    profile_id = int(params["profileId"])
    region = params["region"]
    fetch_all = bool(params.get("fetchAll", True))

    access_token = get_access_token(profile_id)

    all_rules = []
    next_token = params.get("nextToken")
    pages = 0

    while True:
        qs = f"nextToken={next_token}" if next_token else None

        resp = _developer_proxy_call(
            region=region,
            path=ENTITY_PATH,
            method="GET",
            access_token=access_token,
            profile_id=profile_id,
            body=None,
            content_type=None,
            query_string=qs,
        )

        if "error" in resp:
            if all_rules:
                break
            print(json.dumps(resp, indent=2, ensure_ascii=False))
            sys.exit(1)

        body_raw = resp.get("body") or "{}"
        try:
            parsed = json.loads(body_raw)
        except (json.JSONDecodeError, TypeError):
            parsed = {}

        # SP budget rules response: {"budgetRules": [...], "nextToken": "..."}
        rules = parsed.get("budgetRules") or parsed.get("budgetRulesDetails") or []
        if isinstance(rules, list):
            all_rules.extend(rules)
        pages += 1

        next_token = parsed.get("nextToken")
        if not next_token or not fetch_all:
            break

    output = {
        "success": True,
        "budgetRules": all_rules,
        "total": len(all_rules),
        "pagesFetched": pages,
    }
    inline = lf_inline_flag()
    emit_result(output, inline)
    print(f"\n✓ Fetched {len(all_rules)} budget rules across {pages} page(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
