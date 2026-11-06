#!/usr/bin/env python3
"""Query existing design registrations through the rewritten SIF adapter.

Usage:
  python ec_dw_design_profile.py '<JSON parameters>' [--inline] [--no-cache]
  python ec_dw_design_profile.py --params-file request.json

The current detail price is 0 credits. Inputs are either
 designRegistrationIds (1–200 IDs) or primaryIdentifier with optional
 jurisdictionIso2. Keep leading zeroes; do not send image-search parameters.
"""

import ec_dw_design_similar_search as _sif

API_PATH = "/ecDw/designProfile"


def main(argv=None):
    # Reuse common call_api.run, normalization and one cache/output layer.
    # Passing the endpoint isolates details from image-search cache entries.
    return _sif.main(argv, api_path=API_PATH, script_name="ec_dw_design_profile.py")


if __name__ == "__main__":
    main()
