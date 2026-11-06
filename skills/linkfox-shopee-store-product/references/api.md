# Shopee 店铺商品管理 接口说明

57个商品转发操作按接口拆分；另提供店铺授权状态兼容操作。

| 操作 | 接口文档 |
|---|---|
| `add_item` | [接口定义](apis/add-item.md) |
| `add_kit_item` | [接口定义](apis/add-kit-item.md) |
| `add_model` | [接口定义](apis/add-model.md) |
| `boost_item` | [接口定义](apis/boost-item.md) |
| `category_recommend` | [接口定义](apis/category-recommend.md) |
| `delete_item` | [接口定义](apis/delete-item.md) |
| `delete_model` | [接口定义](apis/delete-model.md) |
| `generate_kit_image` | [接口定义](apis/generate-kit-image.md) |
| `get_aitem_by_pitem_id` | [接口定义](apis/get-aitem-by-pitem-id.md) |
| `get_all_vehicle_list` | [接口定义](apis/get-all-vehicle-list.md) |
| `get_attribute_tree` | [接口定义](apis/get-attribute-tree.md) |
| `get_boosted_list` | [接口定义](apis/get-boosted-list.md) |
| `get_brand_list` | [接口定义](apis/get-brand-list.md) |
| `get_category` | [接口定义](apis/get-category.md) |
| `get_comment` | [接口定义](apis/get-comment.md) |
| `get_direct_item_list` | [接口定义](apis/get-direct-item-list.md) |
| `get_direct_shop_recommended_price` | [接口定义](apis/get-direct-shop-recommended-price.md) |
| `get_item_base_info` | [接口定义](apis/get-item-base-info.md) |
| `get_item_content_diagnosis_result` | [接口定义](apis/get-item-content-diagnosis-result.md) |
| `get_item_extra_info` | [接口定义](apis/get-item-extra-info.md) |
| `get_item_limit` | [接口定义](apis/get-item-limit.md) |
| `get_item_list` | [接口定义](apis/get-item-list.md) |
| `get_item_list_by_content_diagnosis` | [接口定义](apis/get-item-list-by-content-diagnosis.md) |
| `get_item_promotion` | [接口定义](apis/get-item-promotion.md) |
| `get_item_violation_info` | [接口定义](apis/get-item-violation-info.md) |
| `get_kit_item_info` | [接口定义](apis/get-kit-item-info.md) |
| `get_kit_item_limit` | [接口定义](apis/get-kit-item-limit.md) |
| `get_main_item_list` | [接口定义](apis/get-main-item-list.md) |
| `get_mart_item_by_outlet_item_id` | [接口定义](apis/get-mart-item-by-outlet-item-id.md) |
| `get_mart_item_mapping_by_id` | [接口定义](apis/get-mart-item-mapping-by-id.md) |
| `get_model_list` | [接口定义](apis/get-model-list.md) |
| `get_product_certification_rule` | [接口定义](apis/get-product-certification-rule.md) |
| `get_recommend_attribute` | [接口定义](apis/get-recommend-attribute.md) |
| `get_size_chart_detail` | [接口定义](apis/get-size-chart-detail.md) |
| `get_size_chart_list` | [接口定义](apis/get-size-chart-list.md) |
| `get_ssp_info` | [接口定义](apis/get-ssp-info.md) |
| `get_ssp_list` | [接口定义](apis/get-ssp-list.md) |
| `get_variations` | [接口定义](apis/get-variations.md) |
| `get_vehicle_list_by_compatibility_detail` | [接口定义](apis/get-vehicle-list-by-compatibility-detail.md) |
| `get_weight_recommendation` | [接口定义](apis/get-weight-recommendation.md) |
| `init_tier_variation` | [接口定义](apis/init-tier-variation.md) |
| `link_ssp` | [接口定义](apis/link-ssp.md) |
| `publish_item_to_outlet_shop` | [接口定义](apis/publish-item-to-outlet-shop.md) |
| `register_brand` | [接口定义](apis/register-brand.md) |
| `reply_comment` | [接口定义](apis/reply-comment.md) |
| `search_attribute_value_list` | [接口定义](apis/search-attribute-value-list.md) |
| `search_item` | [接口定义](apis/search-item.md) |
| `search_unpackaged_model_list` | [接口定义](apis/search-unpackaged-model-list.md) |
| `unlink_ssp` | [接口定义](apis/unlink-ssp.md) |
| `unlist_item` | [接口定义](apis/unlist-item.md) |
| `update_item` | [接口定义](apis/update-item.md) |
| `update_kit_item` | [接口定义](apis/update-kit-item.md) |
| `update_model` | [接口定义](apis/update-model.md) |
| `update_price` | [接口定义](apis/update-price.md) |
| `update_sip_item_price` | [接口定义](apis/update-sip-item-price.md) |
| `update_stock` | [接口定义](apis/update-stock.md) |
| `update_tier_variation` | [接口定义](apis/update-tier-variation.md) |

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

## 脚本运行约定

- 先运行授权依赖检查；返回 0 表示已找到认证技能，返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-shopee-store-auth`。不要在本技能内绕过授权或签发令牌。
- `skipDepCheck` 默认 false；仅用于外部流程已经确认本地依赖的情况，不绕过店铺授权。
- `LINKFOX_TOOL_GATEWAY` 优先，`SHOPEE_API_BASE_URL` 作为兼容网关地址回退；API Key 兼容两种环境变量。
- 57 个商品入口和通用入口 `product_api.py` 使用 JSON CLI；通用入口以 `api` 选择注册操作，`--inline` 强制完整打印，`--no-cache` 可显式传入。商品入口和授权状态兼容函数调用公共 `call_api.run` 时始终加入 `--no-cache`，不读取或写入响应缓存；公共调用器可能建立空 `.cache` 目录，不代表启用缓存。同一会话、同一参数组合仍应避免重复请求。
- 商品 GET 业务参数放 JSON 顶层，按值进行百分号编码并拼为不含 `?` 的 `queryString`；布尔值转为小写字符串，未列入列表转换的对象和数组忽略，null忽略。所有GET中的 `item_id_list` 支持逗号分隔字符串或数组，去掉空项后必须1–50个，再转为逗号分隔字符串。保留字段不进入上游请求。
- POST 优先使用 `body`，其次 `requestBody`，对象序列化为紧凑JSON，有效JSON字符串原样转发；字符串格式错误或为空时在请求前退出，不发送请求。均未提供时仅收集注册表的 `body_fields`。当前仅 `delete_item` 注册 `item_id`，其他 POST 应提供完整请求体。注册表的顶层必填字段检查先执行，因此 `delete_item` 即使给出 body 仍须在顶层提供 `item_id`。
- 商品入口通过 `shopId` 或 `merchantId` 选店，不主动调用 storeTokens。所有已注册的 Product 操作及兼容函数均执行选店检查，不提供省略选店的调用方式。
- 提供 `resolve_store_tokens(params)` 和 `developer_proxy_call(...)` Python 兼容函数；前者查询ERP店铺授权状态，不由商品入口自动调用；后者按选店信息由服务端解析令牌。商品操作不依赖客户端提供店铺令牌。
- 完整网关响应与加工后的商品结果均落盘到当前工作目录 `linkfox/<日期>/<session>/data/`。公共调用器保存网关原始响应，业务封装保存含解析字段的完整结果；两者均不作为响应缓存。原始响应文件的操作标识附加 `raw` 和随机串，避免公共调用器秒级时间戳在连续调用时覆盖；未设置SESSION_ID时，两层输出也使用相同自动会话编号。工作目录不可写时在请求前报错，不回退到家目录或 `/tmp`。
- 所有商品入口与通用入口提供相同的落盘及摘要行为，文件名包含技能名与操作标识；`--inline` 只控制打印方式。

### 网关业务错误

| HTTP / errcode | 含义 | 处理 |
|---|---|---|
| HTTP 400 / errcode 400 | path、method等请求参数不合法 | 按errmsg检查具体参数。 |
| HTTP 503 / errcode 503 | 代理请求发生I/O异常 | 保留响应及错误原因；按用户任务范围决定后续重试，不自动连续请求。 |
| errcode 1002 | 选店参数错误或未登录 | 检查选店字段与API Key，并按errmsg定位原因。 |
| errcode 1004 | 无授权记录或授权不属于当前用户 | 使用认证技能检查店铺授权。 |
| errcode 1005 | path未加入白名单，或授权信息已失效 | 按errmsg分流：白名单错误核对相对路径及放行情况；授权失效使用认证技能重新授权。 |

## 接口：查询店铺授权状态（resolve_store_tokens 兼容函数）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺ID；兼容函数将非空值转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户ID；两者都提供时均传递。 |
| appType | string | 否，仅直接调用网关时可指定 | 默认 `erp`；枚举 `erp` / `ad`。兼容函数只转发选店字段，使用默认 `erp`。 |

这是共享模块提供的Python兼容函数，不提供商品CLI操作，也不在商品流程中自动调用。接口查询已绑定的授权状态，不返回原始令牌；授权与令牌管理仍由认证技能和服务端负责。

### 响应结构

| 字段 / 对象 | 类型 | 说明 |
|---|---|---|
| 根对象 | object | 网关授权状态对象；兼容函数保留原始JSON。 |
| authRecordId | integer (Long) | 授权主表ID。 |
| shopId / merchantId | string | 店铺或商户ID。 |
| shopIdList / merchantIdList | string | 店铺或商户ID列表的JSON字符串。 |
| appType | string | 应用类型：`erp` / `ad`。 |
| expireIn | integer (Long) | 授权记录中的access_token有效期，单位秒。 |
| status | string | 网关授权状态：`ACTIVE` / `EXPIRED`。 |
| message | string | 授权状态说明。 |
| errcode | integer / string / null | 如返回，按公共响应码规则判断。 |
| errmsg | string | 如返回，保留网关消息。 |
| error / details | string | 连接或HTTP错误时公共调用器可能给出的错误信息及原始内容。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 按返回的授权状态及消息判断记录情况；`ACTIVE` 不保证后续商品操作必然成功。无授权记录按认证技能处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-product",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
