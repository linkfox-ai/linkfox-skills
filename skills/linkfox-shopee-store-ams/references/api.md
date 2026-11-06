# Shopee 联盟营销 AMS 接口说明

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

## 脚本兼容与使用限制

- 授权依赖检测成功返回 0；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`。`skipDepCheck` 默认为 false，仅跳过本地安装检测，不绕过店铺授权。检测脚本探测安装目录与环境变量。
- 网关地址优先 `LINKFOX_TOOL_GATEWAY`，其次兼容变量 `SHOPEE_API_BASE_URL`，最后为公共默认地址；API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。
- 业务入口使用 `python scripts/<操作>.py '<JSON 参数>' [--inline] [--no-cache]`；通用入口 `scripts/ams_api.py` 还要求 JSON 的 `api` 字段为 36 个 AMS 操作名之一。`--help` 展示本地用法，不触发请求。
- 本技能不提供响应缓存。业务封装调用公共 `call_api.run` 时始终加入 `--no-cache`，不会读写响应缓存，也没有第二层缓存；公共脚本可能建立空缓存目录。
- 所有 AMS 操作必须提供 `shopId` 或 `merchantId`，店铺级操作通常推荐 `shopId`；两者同时提供时保留两者。本技能没有无店铺 AMS 入口。
- AMS 主流程由服务端根据选定店铺解析令牌，不自动调用 `/shopee/storeTokens`；辅助函数 `resolve_store_tokens` 提供独立兼容查询。不要在本技能中另行实现授权或刷新令牌。
- GET 业务字段放脚本 JSON 顶层；除 null 外的标量按原键名生成不带 `?` 的 `queryString`，空字符串、0 和 false 均保留，值做 URL 编码，布尔值转小写；对象或数组不进入查询串。当前注册表 `LIST_QUERY_FIELDS` 为空，不自行假设列表参数支持方式。
- POST 优先使用 `body`，其次 `requestBody`；对象序列化为 JSON 字符串，字符串原样转发。仅注册表列明的 `body_fields` 可由顶层收集，当前 36 项均未定义该清单，故 POST 需显式提供请求体。空对象可被本地接受，但不代表满足上游要求；非空字符串必须为合法 JSON，提前校验以免写入后才发现无法解析。空字符串保留原样，上游是否接受以业务要求为准；加工结果的 requestBody 为 null。
- `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 为保留键，不进入脚本生成的 GET 业务查询；网关会另行添加 `shop_id` / `merchant_id` 查询参数。选店字段不由封装自动注入业务 body，显式请求体内容由调用者按上游要求准备。
- AMS 入口使用注册表中的固定 `api/v2/ams/...` 路径；共享兼容函数要求路径以 `api/v2` 开头。`contentType` 默认 `application/json`，只在传 body 时发送。
- 完整原始网关响应和加工结果均保存在当前工作目录的 `linkfox/<YYYY-MM-DD>/<session>/data/`；原始文件带操作名与 `raw` 标记，加工文件带操作名，`SESSION_ID` 优先。保存失败应报错；业务封装在请求前验证当前目录可写，不回退到家目录或临时目录。请求完成后若原始响应或加工结果保存失败，报错不表示操作未执行，应先核对店铺实际状态，不自动重复提交。小于等于 8000 UTF-8 字节全量打印，较大响应展示摘要，`--inline` 强制完整打印。
- 各分文档说明网关与脚本契约；完整 Shopee 业务字段、必填项、枚举或分页限制按对应官方文档准备，不能把占位请求体或通用示例当作可直接执行的业务请求。

### 透传上下文请求头

| 请求头 | 类型 | 来源与默认值 | 说明 |
|---|---|---|---|
| SESSION_ID | string | 同名环境变量，默认空字符串 | 业务请求会话上下文；本地会话目录优先使用该变量，未配置时自动生成目录会话号。 |
| MESSAGE_ID | string | 同名环境变量，默认空字符串 | 调用链路的消息上下文。 |
| MODE_ID | string | 同名环境变量，默认空字符串 | 调用链路的模式上下文。 |
| APP_NAME | string | 同名环境变量，默认空字符串 | 调用链路的应用上下文。 |

## AMS 操作文档索引

网关统一使用 POST `/shopee/developerProxy`，上游 GET / POST、完整 path 与字段见各接口文档。官方 AMS 模块为 127，与站内 CPC Ads 模块 117 不同。

| 操作 | 上游方法 | path | 接口文档 |
|---|---|---|---|
| `add_all_products_to_open_campaign` | POST | `api/v2/ams/add_all_products_to_open_campaign` | [apis/add-all-products-to-open-campaign.md](apis/add-all-products-to-open-campaign.md) |
| `batch_add_products_to_open_campaign` | POST | `api/v2/ams/batch_add_products_to_open_campaign` | [apis/batch-add-products-to-open-campaign.md](apis/batch-add-products-to-open-campaign.md) |
| `batch_edit_products_open_campaign_setting` | POST | `api/v2/ams/batch_edit_products_open_campaign_setting` | [apis/batch-edit-products-open-campaign-setting.md](apis/batch-edit-products-open-campaign-setting.md) |
| `batch_get_products_suggested_rate` | POST | `api/v2/ams/batch_get_products_suggested_rate` | [apis/batch-get-products-suggested-rate.md](apis/batch-get-products-suggested-rate.md) |
| `batch_remove_products_open_campaign_setting` | POST | `api/v2/ams/batch_remove_products_open_campaign_setting` | [apis/batch-remove-products-open-campaign-setting.md](apis/batch-remove-products-open-campaign-setting.md) |
| `create_new_targeted_campaign` | POST | `api/v2/ams/create_new_targeted_campaign` | [apis/create-new-targeted-campaign.md](apis/create-new-targeted-campaign.md) |
| `edit_affiliate_list_of_targeted_campaign` | POST | `api/v2/ams/edit_affiliate_list_of_targeted_campaign` | [apis/edit-affiliate-list-of-targeted-campaign.md](apis/edit-affiliate-list-of-targeted-campaign.md) |
| `edit_all_products_open_campaign_setting` | POST | `api/v2/ams/edit_all_products_open_campaign_setting` | [apis/edit-all-products-open-campaign-setting.md](apis/edit-all-products-open-campaign-setting.md) |
| `edit_product_list_of_targeted_campaign` | POST | `api/v2/ams/edit_product_list_of_targeted_campaign` | [apis/edit-product-list-of-targeted-campaign.md](apis/edit-product-list-of-targeted-campaign.md) |
| `get_affiliate_performance` | GET | `api/v2/ams/get_affiliate_performance` | [apis/get-affiliate-performance.md](apis/get-affiliate-performance.md) |
| `get_auto_add_new_product_toggle_status` | GET | `api/v2/ams/get_auto_add_new_product_toggle_status` | [apis/get-auto-add-new-product-toggle-status.md](apis/get-auto-add-new-product-toggle-status.md) |
| `get_campaign_key_metrics_performance` | GET | `api/v2/ams/get_campaign_key_metrics_performance` | [apis/get-campaign-key-metrics-performance.md](apis/get-campaign-key-metrics-performance.md) |
| `get_content_performance` | GET | `api/v2/ams/get_content_performance` | [apis/get-content-performance.md](apis/get-content-performance.md) |
| `get_conversion_report` | GET | `api/v2/ams/get_conversion_report` | [apis/get-conversion-report.md](apis/get-conversion-report.md) |
| `get_managed_affiliate_list` | GET | `api/v2/ams/get_managed_affiliate_list` | [apis/get-managed-affiliate-list.md](apis/get-managed-affiliate-list.md) |
| `get_open_campaign_added_product` | GET | `api/v2/ams/get_open_campaign_added_product` | [apis/get-open-campaign-added-product.md](apis/get-open-campaign-added-product.md) |
| `get_open_campaign_batch_task_result` | GET | `api/v2/ams/get_open_campaign_batch_task_result` | [apis/get-open-campaign-batch-task-result.md](apis/get-open-campaign-batch-task-result.md) |
| `get_open_campaign_not_added_product` | GET | `api/v2/ams/get_open_campaign_not_added_product` | [apis/get-open-campaign-not-added-product.md](apis/get-open-campaign-not-added-product.md) |
| `get_open_campaign_performance` | GET | `api/v2/ams/get_open_campaign_performance` | [apis/get-open-campaign-performance.md](apis/get-open-campaign-performance.md) |
| `get_optimization_suggestion_product` | GET | `api/v2/ams/get_optimization_suggestion_product` | [apis/get-optimization-suggestion-product.md](apis/get-optimization-suggestion-product.md) |
| `get_performance_data_update_time` | GET | `api/v2/ams/get_performance_data_update_time` | [apis/get-performance-data-update-time.md](apis/get-performance-data-update-time.md) |
| `get_product_performance` | GET | `api/v2/ams/get_product_performance` | [apis/get-product-performance.md](apis/get-product-performance.md) |
| `get_recommended_affiliate_list` | GET | `api/v2/ams/get_recommended_affiliate_list` | [apis/get-recommended-affiliate-list.md](apis/get-recommended-affiliate-list.md) |
| `get_shop_performance` | GET | `api/v2/ams/get_shop_performance` | [apis/get-shop-performance.md](apis/get-shop-performance.md) |
| `get_shop_suggested_rate` | GET | `api/v2/ams/get_shop_suggested_rate` | [apis/get-shop-suggested-rate.md](apis/get-shop-suggested-rate.md) |
| `get_targeted_campaign_addable_product_list` | GET | `api/v2/ams/get_targeted_campaign_addable_product_list` | [apis/get-targeted-campaign-addable-product-list.md](apis/get-targeted-campaign-addable-product-list.md) |
| `get_targeted_campaign_list` | GET | `api/v2/ams/get_targeted_campaign_list` | [apis/get-targeted-campaign-list.md](apis/get-targeted-campaign-list.md) |
| `get_targeted_campaign_performance` | GET | `api/v2/ams/get_targeted_campaign_performance` | [apis/get-targeted-campaign-performance.md](apis/get-targeted-campaign-performance.md) |
| `get_targeted_campaign_settings` | GET | `api/v2/ams/get_targeted_campaign_settings` | [apis/get-targeted-campaign-settings.md](apis/get-targeted-campaign-settings.md) |
| `get_validation_list` | GET | `api/v2/ams/get_validation_list` | [apis/get-validation-list.md](apis/get-validation-list.md) |
| `get_validation_report` | GET | `api/v2/ams/get_validation_report` | [apis/get-validation-report.md](apis/get-validation-report.md) |
| `query_affiliate_list` | GET | `api/v2/ams/query_affiliate_list` | [apis/query-affiliate-list.md](apis/query-affiliate-list.md) |
| `remove_all_products_open_campaign_setting` | POST | `api/v2/ams/remove_all_products_open_campaign_setting` | [apis/remove-all-products-open-campaign-setting.md](apis/remove-all-products-open-campaign-setting.md) |
| `terminate_targeted_campaign` | POST | `api/v2/ams/terminate_targeted_campaign` | [apis/terminate-targeted-campaign.md](apis/terminate-targeted-campaign.md) |
| `update_auto_add_new_product_setting` | POST | `api/v2/ams/update_auto_add_new_product_setting` | [apis/update-auto-add-new-product-setting.md](apis/update-auto-add-new-product-setting.md) |
| `update_basic_info_of_targeted_campaign` | POST | `api/v2/ams/update_basic_info_of_targeted_campaign` | [apis/update-basic-info-of-targeted-campaign.md](apis/update-basic-info-of-targeted-campaign.md) |

## 接口：兼容查询店铺令牌（storeTokens）

共享函数 `resolve_store_tokens(params)` 提供此调用，不属于 36 个 AMS 操作；正常 AMS 流程由服务端解析令牌，不自动执行此辅助调用。授权和令牌管理仍交由授权技能。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少提供一个 | 函数将非空值转为字符串。 |
| merchantId | string | 与 shopId 至少提供一个 | 函数将非空值转为字符串；同时提供时保留两者。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 若存在，按公共规则判断。 |
| errmsg | string | 若存在，用于解释网关结果。 |
| 其他返回字段 | 以实际响应为准 | 辅助函数透传完整响应；令牌字段及嵌套结构以实际响应为准，不补造字段。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

无授权记录时交由 `linkfox-shopee-store-auth`；不要通过重复获取令牌绕过授权问题。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-ams",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
