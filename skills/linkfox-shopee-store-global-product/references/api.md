# Shopee 全球商品 接口说明

## 接口索引

全球商品 34 个转发操作分别定义于下表文档；每份文档独立列出请求、响应、限制及示例。上游 GET/POST 均经网关 POST 转发。

| 操作 | 接口文档 |
|---|---|
| `add_global_item` | [apis/add-global-item.md](apis/add-global-item.md) |
| `add_global_model` | [apis/add-global-model.md](apis/add-global-model.md) |
| `category_recommend` | [apis/category-recommend.md](apis/category-recommend.md) |
| `create_publish_task` | [apis/create-publish-task.md](apis/create-publish-task.md) |
| `delete_global_item` | [apis/delete-global-item.md](apis/delete-global-item.md) |
| `delete_global_model` | [apis/delete-global-model.md](apis/delete-global-model.md) |
| `get_attribute_tree` | [apis/get-attribute-tree.md](apis/get-attribute-tree.md) |
| `get_brand_list` | [apis/get-brand-list.md](apis/get-brand-list.md) |
| `get_category` | [apis/get-category.md](apis/get-category.md) |
| `get_global_item_id` | [apis/get-global-item-id.md](apis/get-global-item-id.md) |
| `get_global_item_info` | [apis/get-global-item-info.md](apis/get-global-item-info.md) |
| `get_global_item_limit` | [apis/get-global-item-limit.md](apis/get-global-item-limit.md) |
| `get_global_item_list` | [apis/get-global-item-list.md](apis/get-global-item-list.md) |
| `get_global_model_list` | [apis/get-global-model-list.md](apis/get-global-model-list.md) |
| `get_local_adjustment_rate` | [apis/get-local-adjustment-rate.md](apis/get-local-adjustment-rate.md) |
| `get_publish_task_result` | [apis/get-publish-task-result.md](apis/get-publish-task-result.md) |
| `get_publishable_shop` | [apis/get-publishable-shop.md](apis/get-publishable-shop.md) |
| `get_published_list` | [apis/get-published-list.md](apis/get-published-list.md) |
| `get_recommend_attribute` | [apis/get-recommend-attribute.md](apis/get-recommend-attribute.md) |
| `get_shop_publishable_status` | [apis/get-shop-publishable-status.md](apis/get-shop-publishable-status.md) |
| `get_size_chart_detail` | [apis/get-size-chart-detail.md](apis/get-size-chart-detail.md) |
| `get_size_chart_list` | [apis/get-size-chart-list.md](apis/get-size-chart-list.md) |
| `get_variations` | [apis/get-variations.md](apis/get-variations.md) |
| `init_tier_variation` | [apis/init-tier-variation.md](apis/init-tier-variation.md) |
| `search_global_attribute_value_list` | [apis/search-global-attribute-value-list.md](apis/search-global-attribute-value-list.md) |
| `set_sync_field` | [apis/set-sync-field.md](apis/set-sync-field.md) |
| `support_size_chart` | [apis/support-size-chart.md](apis/support-size-chart.md) |
| `update_global_item` | [apis/update-global-item.md](apis/update-global-item.md) |
| `update_global_model` | [apis/update-global-model.md](apis/update-global-model.md) |
| `update_local_adjustment_rate` | [apis/update-local-adjustment-rate.md](apis/update-local-adjustment-rate.md) |
| `update_price` | [apis/update-price.md](apis/update-price.md) |
| `update_size_chart` | [apis/update-size-chart.md](apis/update-size-chart.md) |
| `update_stock` | [apis/update-stock.md](apis/update-stock.md) |
| `update_tier_variation` | [apis/update-tier-variation.md](apis/update-tier-variation.md) |

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

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| api | string | 仅通用入口必填 | `scripts/global_product_api.py` 选择注册表中的操作；独立脚本固定操作。 |
| skipDepCheck | boolean | 否 | 默认 false；已由外部流程完成依赖检查时可跳过本地检查，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务脚本不启用响应缓存；调用公共 run 时始终添加此选项，重复运行会重新请求接口。 |

依赖检查返回 0 表示找到授权技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-shopee-store-auth`。不在本技能重做授权。
基础地址优先使用 `LINKFOX_TOOL_GATEWAY`，其次兼容 `SHOPEE_API_BASE_URL`；API Key 兼容两个公共变量。
保存路径限定当前工作目录的 `linkfox/`，请求前检查可写；不回退家目录或临时目录。先保存原始网关响应，再保存含解析结果的业务响应，均无响应缓存。
独立脚本与通用入口接受 JSON 位置参数及 `--inline`、`--no-cache`；`--help` 仅显示帮助，不发请求。

读取与写入操作均通过 `--no-cache` 调用公共运行器，不复用响应缓存；完整响应文件可供后续按需读取。
`SESSION_ID` 去除首尾空白后须为单个目录名，不接受 `.`、`..`、路径分隔符或盘符；空白值使用自动会话名。
请求前检查最终会话数据目录是否可创建、可写；业务结果保存失败时明确报错，不将未保存的业务结果登记为成功。
POST 的字符串 body / requestBody 在发送前校验为有效 JSON；保留原字符串及嵌套结构，不在发送之后才解析而中断结果保存。

## 接口：获取已授权令牌（storeTokens，辅助）

`resolve_store_tokens(params)` 提供令牌辅助查询；常规全球商品入口直接传商户 / 店铺标识，由服务端解析令牌，不自动先调用此接口。店铺授权由授权技能完成。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID；脚本转成字符串。 |
| merchantId | string | 与 shopId 至少一个 | 已授权商户 ID；可与 shopId 同时传入。 |

独立入口 `python scripts/store_tokens.py '<JSON 参数>' [--inline] [--no-cache]`；辅助函数返回完整网关 JSON。辅助函数只转发上述两个标识，不传其他业务字段。

运行选项与依赖、保存约定见上方 [脚本运行约定](#脚本运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态；可缺失，按基础规则判断。 |
| errmsg | string | 可用时原样保留消息。 |
| transportHttpStatus | integer / null | 封装补充的 LinkFox 外层 HTTP 状态；连接失败为 null。 |
| error | string | 传输错误说明；可用时保留。 |
| details | string | 传输错误的原始详情；可用时保留。 |
| 其他原始字段 | 未声明 | 返回实际 JSON，内部字段按实际响应展示，不臆造字段或令牌结构。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 这是授权后的令牌辅助查询，不执行授权，也不发布或变更商品。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "merchantId": "12345"
}
'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-global-product",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
