# linkfox-shopee-store-ads — 参数与字段参考

Shopee **Ads 模块**全部 23 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.ads.get_total_balance](https://open.shopee.com/documents/v2/v2.ads.get_total_balance?module=117&type=1)

> 未纳入：`create_auto_product_ads`、`edit_auto_product_ads`（官方标注 coming offline soon）

## 通用约定

- **Base URL**：`${LINKFOX_TOOL_GATEWAY}`
- **Method**：POST（网关），上游 Method 见各接口
- **Auth**：Header `Authorization: <api_key>`（`LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY`）（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **流程**：`POST /shopee/storeTokens` → `POST /shopee/developerProxy`
- **path**：须 `api/v2/ads/...`
- **标识**：店铺级广告 API，通常传 **`shopId`**
- **权限**：Ads API 需 Shopee 额外开通广告权限；并非所有站点可用
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.ads.{api}?module=117&type=1`
- **复杂 POST**（如 `create_manual_product_ads`）：推荐传完整 `body`；日期格式常为 DD-MM-YYYY

---

## Ads 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | check_create_gms_product_campaign_eligibility | GET | `api/v2/ads/check_create_gms_product_campaign_eligibility` | `check_create_gms_product_campaign_eligibility.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.check_create_gms_product_campaign_eligibility?module=117&type=1) |
| 2 | create_gms_product_campaign | POST | `api/v2/ads/create_gms_product_campaign` | `create_gms_product_campaign.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.create_gms_product_campaign?module=117&type=1) |
| 3 | create_manual_product_ads | POST | `api/v2/ads/create_manual_product_ads` | `create_manual_product_ads.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.create_manual_product_ads?module=117&type=1) |
| 4 | edit_gms_item_product_campaign | POST | `api/v2/ads/edit_gms_item_product_campaign` | `edit_gms_item_product_campaign.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.edit_gms_item_product_campaign?module=117&type=1) |
| 5 | edit_gms_product_campaign | POST | `api/v2/ads/edit_gms_product_campaign` | `edit_gms_product_campaign.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.edit_gms_product_campaign?module=117&type=1) |
| 6 | edit_manual_product_ad_keywords | POST | `api/v2/ads/edit_manual_product_ad_keywords` | `edit_manual_product_ad_keywords.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.edit_manual_product_ad_keywords?module=117&type=1) |
| 7 | edit_manual_product_ads | POST | `api/v2/ads/edit_manual_product_ads` | `edit_manual_product_ads.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.edit_manual_product_ads?module=117&type=1) |
| 8 | get_ads_facil_shop_rate | GET | `api/v2/ads/get_ads_facil_shop_rate` | `get_ads_facil_shop_rate.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_ads_facil_shop_rate?module=117&type=1) |
| 9 | get_all_cpc_ads_daily_performance | GET | `api/v2/ads/get_all_cpc_ads_daily_performance` | `get_all_cpc_ads_daily_performance.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_all_cpc_ads_daily_performance?module=117&type=1) |
| 10 | get_all_cpc_ads_hourly_performance | GET | `api/v2/ads/get_all_cpc_ads_hourly_performance` | `get_all_cpc_ads_hourly_performance.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_all_cpc_ads_hourly_performance?module=117&type=1) |
| 11 | get_create_product_ad_budget_suggestion | GET | `api/v2/ads/get_create_product_ad_budget_suggestion` | `get_create_product_ad_budget_suggestion.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_create_product_ad_budget_suggestion?module=117&type=1) |
| 12 | get_gms_campaign_performance | GET | `api/v2/ads/get_gms_campaign_performance` | `get_gms_campaign_performance.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_gms_campaign_performance?module=117&type=1) |
| 13 | get_gms_item_performance | GET | `api/v2/ads/get_gms_item_performance` | `get_gms_item_performance.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_gms_item_performance?module=117&type=1) |
| 14 | get_product_campaign_daily_performance | GET | `api/v2/ads/get_product_campaign_daily_performance` | `get_product_campaign_daily_performance.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_product_campaign_daily_performance?module=117&type=1) |
| 15 | get_product_campaign_hourly_performance | GET | `api/v2/ads/get_product_campaign_hourly_performance` | `get_product_campaign_hourly_performance.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_product_campaign_hourly_performance?module=117&type=1) |
| 16 | get_product_level_campaign_id_list | GET | `api/v2/ads/get_product_level_campaign_id_list` | `get_product_level_campaign_id_list.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_product_level_campaign_id_list?module=117&type=1) |
| 17 | get_product_level_campaign_setting_info | GET | `api/v2/ads/get_product_level_campaign_setting_info` | `get_product_level_campaign_setting_info.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_product_level_campaign_setting_info?module=117&type=1) |
| 18 | get_product_recommended_roi_target | GET | `api/v2/ads/get_product_recommended_roi_target` | `get_product_recommended_roi_target.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_product_recommended_roi_target?module=117&type=1) |
| 19 | get_recommended_item_list | GET | `api/v2/ads/get_recommended_item_list` | `get_recommended_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_recommended_item_list?module=117&type=1) |
| 20 | get_recommended_keyword_list | GET | `api/v2/ads/get_recommended_keyword_list` | `get_recommended_keyword_list.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_recommended_keyword_list?module=117&type=1) |
| 21 | get_shop_toggle_info | GET | `api/v2/ads/get_shop_toggle_info` | `get_shop_toggle_info.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_shop_toggle_info?module=117&type=1) |
| 22 | get_total_balance | GET | `api/v2/ads/get_total_balance` | `get_total_balance.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.get_total_balance?module=117&type=1) |
| 23 | list_gms_user_deleted_item | GET | `api/v2/ads/list_gms_user_deleted_item` | `list_gms_user_deleted_item.py` | [doc](https://open.shopee.com/documents/v2/v2.ads.list_gms_user_deleted_item?module=117&type=1) |
通用入口：`ads_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

### 账户与推荐

| API | 要点 |
|-----|------|
| `get_total_balance` | 广告账户余额 |
| `get_shop_toggle_info` | 自动充值、Campaign Surge 开关 |
| `get_recommended_keyword_list` | 推荐关键词 |
| `get_recommended_item_list` | 推荐推广商品 |

### 效果报表

| API | 要点 |
|-----|------|
| `get_all_cpc_ads_daily_performance` / `hourly` | 全部 CPC 广告效果 |
| `get_product_campaign_daily_performance` / `hourly` | 商品广告活动效果 |
| `get_gms_campaign_performance` / `get_gms_item_performance` | GMS 广告效果 |

### 手动商品广告

| API | 要点 |
|-----|------|
| `get_product_level_campaign_id_list` | 商品级 campaign ID 列表 |
| `get_product_level_campaign_setting_info` | campaign 设置详情 |
| `create_manual_product_ads` | 创建手动选品广告 |
| `edit_manual_product_ads` / `edit_manual_product_ad_keywords` | 编辑广告/关键词 |
| `get_create_product_ad_budget_suggestion` | 预算建议 |
| `get_product_recommended_roi_target` | 推荐 ROI |

### GMS 广告

| API | 要点 |
|-----|------|
| `check_create_gms_product_campaign_eligibility` | 创建资格检查 |
| `create_gms_product_campaign` / `edit_gms_product_campaign` | 创建/编辑 GMS campaign |
| `edit_gms_item_product_campaign` | 编辑 GMS 商品 campaign |
| `list_gms_user_deleted_item` | 用户删除商品列表 |

---

## 网关错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 shopId 与 API Key |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/ads/...` |
| HTTP 402 | 计费/积分不足 | 按 SKILL.md 的 **## 解决认证和积分问题** 处理 |

---

## curl 示例

```bash
export KEY=${LINKFOX_AGENT_API_KEY}
BASE=${LINKFOX_TOOL_GATEWAY}

curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/ads/get_total_balance",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-ads","sentiment":"POSITIVE",
       "category":"OTHER","content":"广告余额查询正常"}'
```
