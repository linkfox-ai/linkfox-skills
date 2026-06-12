#!/usr/bin/env python3
"""Local Temu accessToken storage (manual authorization from seller console)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

DEFAULT_STORE_PATH = os.path.expanduser("~/.linkfox/temu-access-tokens.json")

def store_path() -> str:
    return os.environ.get("TEMU_TOKEN_STORE_PATH", DEFAULT_STORE_PATH)

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _load_store() -> dict:
    path = store_path()
    if not os.path.isfile(path):
        return {"stores": []}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "stores" not in data or not isinstance(data["stores"], list):
        return {"stores": []}
    return data

def _save_store(data: dict) -> None:
    path = store_path()
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

def _find_store(data: dict, store_key: str):
    for store in data["stores"]:
        if store.get("storeKey") == store_key:
            return store
    return None

def _token_key(site: str, management_type: str, token_purpose: str) -> tuple:
    return site, management_type, token_purpose or "default"

def save_token(
    store_key: str,
    site: str,
    management_type: str,
    access_token: str,
    token_purpose: str = "default",
    label: str | None = None,
) -> dict:
    data = _load_store()
    store = _find_store(data, store_key)
    if store is None:
        store = {"storeKey": store_key, "label": label or store_key, "tokens": []}
        data["stores"].append(store)
    elif label:
        store["label"] = label

    key = _token_key(site, management_type, token_purpose)
    entry = {
        "site": site,
        "managementType": management_type,
        "tokenPurpose": token_purpose,
        "accessToken": access_token,
        "updatedAt": _utc_now(),
    }
    replaced = False
    for i, item in enumerate(store["tokens"]):
        if _token_key(
            item.get("site", ""),
            item.get("managementType", ""),
            item.get("tokenPurpose", "default"),
        ) == key:
            store["tokens"][i] = entry
            replaced = True
            break
    if not replaced:
        store["tokens"].append(entry)

    _save_store(data)
    return {
        "storeKey": store_key,
        "site": site,
        "managementType": management_type,
        "tokenPurpose": token_purpose,
        "storePath": store_path(),
        "updatedAt": entry["updatedAt"],
        "replaced": replaced,
    }

def get_token(
    store_key: str,
    site: str,
    management_type: str,
    token_purpose: str = "default",
):
    data = _load_store()
    store = _find_store(data, store_key)
    if not store:
        return None
    key = _token_key(site, management_type, token_purpose)
    for item in store.get("tokens", []):
        if _token_key(
            item.get("site", ""),
            item.get("managementType", ""),
            item.get("tokenPurpose", "default"),
        ) == key:
            return item.get("accessToken")
    return None

def list_stores(mask: bool = True) -> dict:
    data = _load_store()
    stores = []
    for store in data.get("stores", []):
        tokens = []
        for item in store.get("tokens", []):
            token = item.get("accessToken", "")
            if mask and token:
                shown = token[:6] + "..." + token[-4:] if len(token) > 12 else "***"
            else:
                shown = token
            tokens.append(
                {
                    "site": item.get("site"),
                    "managementType": item.get("managementType"),
                    "tokenPurpose": item.get("tokenPurpose", "default"),
                    "accessToken": shown,
                    "updatedAt": item.get("updatedAt"),
                }
            )
        stores.append(
            {
                "storeKey": store.get("storeKey"),
                "label": store.get("label"),
                "tokens": tokens,
            }
        )
    return {"storePath": store_path(), "stores": stores}
