# Shopee 店铺站内广告 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 认证与转发约定

- 依赖 `linkfox-shopee-store-auth`。`python scripts/check_auth_dependency.py [--json]` 返回 0 表示找到依赖；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`，须先安装依赖，不在本技能中重新实现授权。
- 每次任务开始，由认证技能的 `authorized_stores.py` 确认目标 `shopId` 存在 `appType=ad`。只有 `appType=erp` 或历史空值不能代替；使用其 `authorize_url.py` 且传 `appType=ad` 完成广告授权，授权链接 1 小时有效。用户只需要广告时可以只开通 AD。
- Ads 还要求 Shopee 侧开通广告能力，并非所有店铺、站点均可用。
- 网关只需 `shopId` 或 `merchantId` 及 `api/v2/ads/...`。服务端注入 AD Token，转发链路为 `developerProxy` → 紫鸟 `shopee-proxy/ad/...` → Shopee API。
- 禁止在 `developerProxy` 传 `accessToken` 或 `appType`；不要先调用 `storeTokens` 获取 raw token。脚本也拒绝这两个字段，且不获取店铺 Token。
- 业务 HTTP 始终由 `scripts/call_api.py` 的 `run` 执行。`LINKFOX_TOOL_GATEWAY` 优先，其次兼容 `SHOPEE_API_BASE_URL`，最后使用公共规则的默认网关；API Key 保留两种环境变量兼容。
- 业务封装始终传 `--no-cache`，不读取或写入响应缓存，也无第二层响应缓存。公共调用器仍可能创建空的 `.cache` 目录。会话内仍应避免重复调用。
- `python scripts/<操作>.py '<JSON 参数>' [--inline] [--no-cache]` 使用 JSON CLI；`python scripts/ads_api.py '<含 api 的 JSON 参数>' [--inline] [--no-cache]` 为通用入口。`skipDepCheck` 仅跳过依赖安装检查，不代表已经获得 AD 授权。
- 完整输出保存在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-ads-<接口标识>-<timestamp>.json`；保留完整网关响应与加工后的业务字段。当前目录不可写时在请求前报错，不回退到家目录或临时目录。
- POST 创建、编辑推荐传唯一 `reference_id` 防重复。请求结果不确定时先核对已执行结果，不自动重放写入。日期格式常为 `DD-MM-YYYY`，各操作以官方定义为准。
- 自动商品广告 `create_auto_product_ads`、`edit_auto_product_ads` 因官方标注 coming offline soon 而未纳入；AMS（module=127）不在本模块范围。

## 接口文档索引

23 个独立操作共用 `POST /shopee/developerProxy`，上游 Method 与 path 由各操作定义；通用入口的 `api` 值为下表标识。

| 接口标识 | 上游 Method / path | 接口文档 | 对应脚本 |
|------|------|------|------|
| `check_create_gms_product_campaign_eligibility` | GET `api/v2/ads/check_create_gms_product_campaign_eligibility` | [apis/check-create-gms-product-campaign-eligibility.md](apis/check-create-gms-product-campaign-eligibility.md) | `scripts/check_create_gms_product_campaign_eligibility.py` |
| `create_gms_product_campaign` | POST `api/v2/ads/create_gms_product_campaign` | [apis/create-gms-product-campaign.md](apis/create-gms-product-campaign.md) | `scripts/create_gms_product_campaign.py` |
| `create_manual_product_ads` | POST `api/v2/ads/create_manual_product_ads` | [apis/create-manual-product-ads.md](apis/create-manual-product-ads.md) | `scripts/create_manual_product_ads.py` |
| `edit_gms_item_product_campaign` | POST `api/v2/ads/edit_gms_item_product_campaign` | [apis/edit-gms-item-product-campaign.md](apis/edit-gms-item-product-campaign.md) | `scripts/edit_gms_item_product_campaign.py` |
| `edit_gms_product_campaign` | POST `api/v2/ads/edit_gms_product_campaign` | [apis/edit-gms-product-campaign.md](apis/edit-gms-product-campaign.md) | `scripts/edit_gms_product_campaign.py` |
| `edit_manual_product_ad_keywords` | POST `api/v2/ads/edit_manual_product_ad_keywords` | [apis/edit-manual-product-ad-keywords.md](apis/edit-manual-product-ad-keywords.md) | `scripts/edit_manual_product_ad_keywords.py` |
| `edit_manual_product_ads` | POST `api/v2/ads/edit_manual_product_ads` | [apis/edit-manual-product-ads.md](apis/edit-manual-product-ads.md) | `scripts/edit_manual_product_ads.py` |
| `get_ads_facil_shop_rate` | GET `api/v2/ads/get_ads_facil_shop_rate` | [apis/get-ads-facil-shop-rate.md](apis/get-ads-facil-shop-rate.md) | `scripts/get_ads_facil_shop_rate.py` |
| `get_all_cpc_ads_daily_performance` | GET `api/v2/ads/get_all_cpc_ads_daily_performance` | [apis/get-all-cpc-ads-daily-performance.md](apis/get-all-cpc-ads-daily-performance.md) | `scripts/get_all_cpc_ads_daily_performance.py` |
| `get_all_cpc_ads_hourly_performance` | GET `api/v2/ads/get_all_cpc_ads_hourly_performance` | [apis/get-all-cpc-ads-hourly-performance.md](apis/get-all-cpc-ads-hourly-performance.md) | `scripts/get_all_cpc_ads_hourly_performance.py` |
| `get_create_product_ad_budget_suggestion` | GET `api/v2/ads/get_create_product_ad_budget_suggestion` | [apis/get-create-product-ad-budget-suggestion.md](apis/get-create-product-ad-budget-suggestion.md) | `scripts/get_create_product_ad_budget_suggestion.py` |
| `get_gms_campaign_performance` | GET `api/v2/ads/get_gms_campaign_performance` | [apis/get-gms-campaign-performance.md](apis/get-gms-campaign-performance.md) | `scripts/get_gms_campaign_performance.py` |
| `get_gms_item_performance` | GET `api/v2/ads/get_gms_item_performance` | [apis/get-gms-item-performance.md](apis/get-gms-item-performance.md) | `scripts/get_gms_item_performance.py` |
| `get_product_campaign_daily_performance` | GET `api/v2/ads/get_product_campaign_daily_performance` | [apis/get-product-campaign-daily-performance.md](apis/get-product-campaign-daily-performance.md) | `scripts/get_product_campaign_daily_performance.py` |
| `get_product_campaign_hourly_performance` | GET `api/v2/ads/get_product_campaign_hourly_performance` | [apis/get-product-campaign-hourly-performance.md](apis/get-product-campaign-hourly-performance.md) | `scripts/get_product_campaign_hourly_performance.py` |
| `get_product_level_campaign_id_list` | GET `api/v2/ads/get_product_level_campaign_id_list` | [apis/get-product-level-campaign-id-list.md](apis/get-product-level-campaign-id-list.md) | `scripts/get_product_level_campaign_id_list.py` |
| `get_product_level_campaign_setting_info` | GET `api/v2/ads/get_product_level_campaign_setting_info` | [apis/get-product-level-campaign-setting-info.md](apis/get-product-level-campaign-setting-info.md) | `scripts/get_product_level_campaign_setting_info.py` |
| `get_product_recommended_roi_target` | GET `api/v2/ads/get_product_recommended_roi_target` | [apis/get-product-recommended-roi-target.md](apis/get-product-recommended-roi-target.md) | `scripts/get_product_recommended_roi_target.py` |
| `get_recommended_item_list` | GET `api/v2/ads/get_recommended_item_list` | [apis/get-recommended-item-list.md](apis/get-recommended-item-list.md) | `scripts/get_recommended_item_list.py` |
| `get_recommended_keyword_list` | GET `api/v2/ads/get_recommended_keyword_list` | [apis/get-recommended-keyword-list.md](apis/get-recommended-keyword-list.md) | `scripts/get_recommended_keyword_list.py` |
| `get_shop_toggle_info` | GET `api/v2/ads/get_shop_toggle_info` | [apis/get-shop-toggle-info.md](apis/get-shop-toggle-info.md) | `scripts/get_shop_toggle_info.py` |
| `get_total_balance` | GET `api/v2/ads/get_total_balance` | [apis/get-total-balance.md](apis/get-total-balance.md) | `scripts/get_total_balance.py` |
| `list_gms_user_deleted_item` | GET `api/v2/ads/list_gms_user_deleted_item` | [apis/list-gms-user-deleted-item.md](apis/list-gms-user-deleted-item.md) | `scripts/list_gms_user_deleted_item.py` |

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-ads",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
