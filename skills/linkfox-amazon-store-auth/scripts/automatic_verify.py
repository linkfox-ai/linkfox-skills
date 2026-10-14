#!/usr/bin/env python3
"""Return the current seller authorization list as one JSON document."""

import json
import sys

from authorized_stores import call_api


def main():
    result = call_api()
    print(json.dumps(result, ensure_ascii=False))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
