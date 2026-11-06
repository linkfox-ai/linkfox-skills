#!/usr/bin/env python3
"""
SP Budget Rules List - linkfox-amazon-ads-manager
================================================

GET sp/budgetRules (Amazon Ads).

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
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import (  # noqa: E402
    ensure_auth_skill_available,
    parse_argv_params,
    require_fields,
    _developer_proxy_call,
    emit_result,
    DEFAULT_MAX_PAGES,
    lf_inline_flag,
)

ENTITY_PATH = "sp/budgetRules"


def main() -> None:
    params = parse_argv_params(__doc__)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    require_fields(params, ["profileId", "region"])

    profile_id = int(params["profileId"])
    region = params["region"]
    fetch_all = bool(params.get("fetchAll", True))


    all_rules = []
    next_token = params.get("nextToken")
    pages = 0
    failure = None
    truncated = False
    max_pages = int(params.get("maxPages") or DEFAULT_MAX_PAGES)

    while True:
        qs = urlencode({"nextToken": next_token}) if next_token else None

        resp = _developer_proxy_call(
            region=region,
            path=ENTITY_PATH,
            method="GET",
            profile_id=profile_id,
            body=None,
            content_type=None,
            query_string=qs,
        )

        status = resp.get("httpStatus")
        if "error" in resp or type(status) is not int or not 200 <= status < 300:
            failure = dict(resp)
            failure.setdefault("error", f"Upstream HTTP {status}")
            truncated = True
            break

        body_raw = resp.get("body") or "{}"
        try:
            parsed = json.loads(body_raw)
        except (json.JSONDecodeError, TypeError) as exc:
            failure = {**resp, "error": f"Failed to parse upstream body: {exc}", "body": body_raw}
            truncated = True
            break
        if not isinstance(parsed, dict):
            failure = {**resp, "error": "预算规则响应不是对象", "body": body_raw}
            truncated = True
            break

        # SP budget rules response: {"budgetRules": [...], "nextToken": "..."}
        invalid = any(value is not None and not isinstance(value, list)
                      for value in (parsed.get("budgetRules"), parsed.get("budgetRulesDetails")))
        if invalid:
            failure = {**resp, "error": "上游预算规则字段必须是数组"}
            truncated = True
            break
        rules = parsed.get("budgetRules") or parsed.get("budgetRulesDetails") or []
        all_rules.extend(rules)
        pages += 1

        next_token = parsed.get("nextToken")
        if not next_token or not fetch_all:
            break
        if pages >= max_pages:
            truncated = True
            break

    output = {
        "success": failure is None,
        "truncated": truncated,
        "budgetRules": all_rules,
        "total": len(all_rules),
        "pagesFetched": pages,
    }
    if failure:
        output.update(failure)
        output["success"] = False
    inline = lf_inline_flag()
    emit_result(output, inline=inline)
    if failure:
        sys.exit(1)
    print(f"\n✓ Fetched {len(all_rules)} budget rules across {pages} page(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
