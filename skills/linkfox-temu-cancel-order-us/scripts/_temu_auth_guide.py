#!/usr/bin/env python3
"""Temu 手动授权步骤，与 references/access-token.md 保持一致。"""

VALID_SHOP_TYPES = frozenset({"semi-managed", "full-managed", "local-native"})
VALID_TOKEN_PURPOSES = frozenset(
    {"product-inventory", "order-shipping", "full-managed", "local-native", "default"}
)

LOGIN_URLS = {
    "cn": "https://seller.kuajingmaihuo.com",
    "partner": "https://agentseller.temu.com",
}

APPS = {
    "kuniao-seller": "酷鸟卖家助手",
    "cyber-erp": "Cyber-ERP酷鸟助手",
    "cyber-erp-native": "Cyber-ERP",
}

def _steps(*items: str) -> list[str]:
    return list(items)

def build_guide(shop_type: str, token_purpose: str, site=None) -> dict:
    shop_type = shop_type.strip().lower()
    token_purpose = (token_purpose or "default").strip().lower()

    if shop_type not in VALID_SHOP_TYPES:
        raise ValueError(
            f"Invalid shopType '{shop_type}'. Use: semi-managed, full-managed, local-native"
        )
    if token_purpose not in VALID_TOKEN_PURPOSES:
        raise ValueError(
            "Invalid tokenPurpose. Use: product-inventory, order-shipping, "
            "full-managed, local-native, default"
        )

    guide = {
        "shopType": shop_type,
        "tokenPurpose": token_purpose,
        "note": (
            "Temu accessToken 需在卖家后台手动复制，无自动 OAuth。"
            "保存后可使用 save_temu_access_token.py / storeKey 调用 API。"
        ),
    }

    if shop_type == "semi-managed" and token_purpose == "product-inventory":
        site = site or "cn"
        login = LOGIN_URLS.get(site, LOGIN_URLS["cn"])
        guide.update(
            {
                "recommendedSite": site,
                "recommendedManagementType": "semi-managed",
                "loginUrl": login,
                "appName": APPS["kuniao-seller"],
                "menuPath": "系统管理 > 服务市场 > 授权管理",
                "steps": _steps(
                    f"登录 Temu 卖家后台：{login}",
                    "进入：系统管理 > 服务市场 > 授权管理",
                    "点击「获取授权」，选择「酷鸟卖家助手」",
                    "全选常规和特殊授权 > 确认",
                    "复制 access_token，用 save_temu_access_token.py 保存",
                ),
                "usageHint": "用于半托管商品、库存类 API；site 通常为 cn 或 partner。",
            }
        )
    elif shop_type == "semi-managed" and token_purpose == "order-shipping":
        site = site or "us"
        guide.update(
            {
                "recommendedSite": site,
                "recommendedManagementType": "semi-managed",
                "loginUrl": LOGIN_URLS["cn"],
                "appName": APPS["cyber-erp"],
                "menuPath": "Seller Central 对应站点 > 服务市场 > 授权管理",
                "steps": _steps(
                    "登录 Temu 卖家后台（seller.kuajingmaihuo.com 或 agentseller.temu.com）",
                    "右上角 Seller Central，切换到目标区域站点（美区/欧区/全球）",
                    "进入：服务市场 > 授权管理",
                    "点击「获取授权」，选择「Cyber-ERP酷鸟助手」",
                    "全选常规和特殊授权 > 确认",
                    "复制 access_token；调用 API 时 site 用 us / global / eu",
                ),
                "usageHint": "用于半托管订单、发货类 API。",
            }
        )
    elif shop_type == "full-managed" or token_purpose == "full-managed":
        site = site or "cn"
        login = LOGIN_URLS.get(site, LOGIN_URLS["cn"])
        guide.update(
            {
                "recommendedSite": site,
                "recommendedManagementType": "full-managed",
                "loginUrl": login,
                "appName": APPS["kuniao-seller"],
                "menuPath": "系统管理 > 服务市场 > 授权管理",
                "steps": _steps(
                    f"登录 Temu 平台：{login}",
                    "系统管理 > 服务市场 > 授权管理",
                    "获取授权 > 选择「酷鸟卖家助手」",
                    "全选常规和特殊授权 > 确认 > 复制 access_token",
                ),
                "usageHint": "全托管店铺通用；site 通常为 cn 或 partner。",
            }
        )
    elif shop_type == "local-native" or token_purpose == "local-native":
        guide.update(
            {
                "recommendedSite": site or "us",
                "recommendedManagementType": "semi-managed",
                "loginUrl": LOGIN_URLS["cn"],
                "appName": APPS["cyber-erp-native"],
                "menuPath": "Apps And Services > Manage Your Apps",
                "steps": _steps(
                    "登录 Temu 卖家后台",
                    "进入：Apps And Services（应用程序和服务）",
                    "Manage Your Apps（管理您的应用）",
                    "Authorize a new app（授权新应用）",
                    "搜索「Cyber-ERP」",
                    "一般权限和敏感权限全选 > 确认 > 复制 access_token",
                ),
                "usageHint": "适用于美区、欧区本土主体店铺。",
            }
        )
    else:
        guide.update(
            {
                "steps": _steps(
                    "确认店铺类型：semi-managed / full-managed / local-native",
                    "确认用途：product-inventory（商品库存）或 order-shipping（订单发货）",
                    "运行 temu_token_guide.py 获取对应步骤",
                    "复制 token 后执行 save_temu_access_token.py",
                ),
                "usageHint": "请指定 shopType 与 tokenPurpose，见 references/access-token.md",
            }
        )

    guide["cautions"] = [
        "子账号可能无法进入服务市场，需主账号授权",
        "多站点需分别登录对应后台获取 Token",
        "Token 有有效期，过期后需重新在后台复制",
        "调用网关前需联系紫鸟配置 IP 白名单",
    ]
    return guide
