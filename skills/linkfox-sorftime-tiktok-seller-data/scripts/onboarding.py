#!/usr/bin/env python3
"""Report configuration presence without displaying credentials or making requests."""
import json
import os

if __name__ == "__main__":
    print(json.dumps({
        "configured": bool(os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")),
        "key_setup": "https://skill.linkfox.com/linkfoxskills/guide.htm",
        "account": "https://agent.linkfox.com/",
    }))
