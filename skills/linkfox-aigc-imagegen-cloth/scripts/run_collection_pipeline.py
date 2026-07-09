#!/usr/bin/env python3
"""服饰套图 pipeline 薄入口：plan / dispatch。"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)  # 本地 collection_pipeline 包，不再外引 _shared

from collection_pipeline.runner import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(variant="cloth", skill_root=SKILL_ROOT))
