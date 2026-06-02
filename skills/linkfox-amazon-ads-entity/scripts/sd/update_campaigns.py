#!/usr/bin/env python3
"""
SD Campaigns Update - linkfox-amazon-ads-entity
===============================================

PUT sd/campaigns (Amazon Ads).

Usage:
  python update_campaigns.py '<JSON params>'

Required:
  profileId (number), region (NA/EU/FE), payload (Amazon-native body)

payload structure:
  [{"campaignId":123,...}]
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
)

ENTITY_PATH = "sd/campaigns"
CONTENT_TYPE = "application/json"
METHOD = "PUT"


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

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(
        f"\n\u2713 {METHOD} {ENTITY_PATH} \u2014 HTTP {result.get('httpStatus', '?')}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
