#!/usr/bin/env python3
"""
SB Ad Groups Create - linkfox-amazon-ads-manager
===============================================

POST sb/v4/adGroups (Amazon Ads).

Usage:
  python create_ad_groups.py '<JSON params>'

Required:
  profileId (number), region (NA/EU/FE), payload (Amazon-native body)

payload structure:
  {"adGroups":[{...}]}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import (  # noqa: E402
    ensure_auth_skill_available,
    get_access_token,
    mutate_entity,
    parse_argv_params,
    require_fields,
    emit_result,
    lf_inline_flag,
)

ENTITY_PATH = "sb/v4/adGroups"
CONTENT_TYPE = "application/vnd.sbadgroupresource.v4+json"
METHOD = "POST"


def main() -> None:
    params = parse_argv_params(__doc__)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    require_fields(params, ["profileId", "region", "payload"])

    profile_id = int(params["profileId"])
    region = params["region"]

    access_token = get_access_token(profile_id)
    result = mutate_entity(
        region=region,
        profile_id=profile_id,
        access_token=access_token,
        path=ENTITY_PATH,
        method=METHOD,
        content_type=CONTENT_TYPE,
        payload=params["payload"],
    )

    if "error" in result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    inline = lf_inline_flag()
    emit_result(result, inline)
    print(
        f"\n\u2713 {METHOD} {ENTITY_PATH} \u2014 HTTP {result.get('httpStatus', '?')}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
