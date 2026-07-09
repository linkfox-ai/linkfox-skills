#!/usr/bin/env python3
"""
SB Ads Create - linkfox-amazon-ads-manager
=========================================

POST sb/v4/ads/<adType> (Amazon Ads).

SB ad creation requires specifying adType - each type has a dedicated endpoint:
  autoCollection, manualCollection, brandVideo, video,
  productCollection, productCollectionExtended, storeSpotlight

Usage:
  python create_ads.py '<JSON params>'

Required:
  profileId (number), region (NA/EU/FE), adType (string), payload (Amazon-native body)

adType values:
  autoCollection | manualCollection | brandVideo | video |
  productCollection | productCollectionExtended | storeSpotlight

payload structure:
  {"ads":[{...}]}
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

VALID_AD_TYPES = [
    "autoCollection",
    "manualCollection",
    "brandVideo",
    "video",
    "productCollection",
    "productCollectionExtended",
    "storeSpotlight",
]

CONTENT_TYPE = "application/vnd.sbadresource.v4+json"
METHOD = "POST"


def main() -> None:
    params = parse_argv_params(__doc__)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    require_fields(params, ["profileId", "region", "adType", "payload"])

    ad_type = params["adType"]
    if ad_type not in VALID_AD_TYPES:
        print(
            f"'adType' must be one of: {', '.join(VALID_AD_TYPES)}",
            file=sys.stderr,
        )
        sys.exit(1)

    entity_path = f"sb/v4/ads/{ad_type}"
    profile_id = int(params["profileId"])
    region = params["region"]

    access_token = get_access_token(profile_id)
    result = mutate_entity(
        region=region,
        profile_id=profile_id,
        payload=params["payload"],
    )

    if "error" in result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    inline = lf_inline_flag()
    emit_result(result, inline)
    print(
        f"\n✓ {METHOD} {entity_path} — HTTP {result.get('httpStatus', '?')}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()