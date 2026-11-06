# Shopee 套装优惠 Bundle Deal 接口说明

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

## 接口索引

| 接口 | 接口文档 |
|---|---|
| 创建套装优惠（`add_bundle_deal`） | [apis/add-bundle-deal.md](apis/add-bundle-deal.md) |
| 添加活动商品（`add_bundle_deal_item`） | [apis/add-bundle-deal-item.md](apis/add-bundle-deal-item.md) |
| 查询套装优惠列表（`get_bundle_deal_list`） | [apis/get-bundle-deal-list.md](apis/get-bundle-deal-list.md) |
| 查询套装优惠详情（`get_bundle_deal`） | [apis/get-bundle-deal.md](apis/get-bundle-deal.md) |
| 查询活动商品（`get_bundle_deal_item`） | [apis/get-bundle-deal-item.md](apis/get-bundle-deal-item.md) |
| 更新套装优惠（`update_bundle_deal`） | [apis/update-bundle-deal.md](apis/update-bundle-deal.md) |
| 更新活动商品（`update_bundle_deal_item`） | [apis/update-bundle-deal-item.md](apis/update-bundle-deal-item.md) |
| 提前结束套装优惠（`end_bundle_deal`） | [apis/end-bundle-deal.md](apis/end-bundle-deal.md) |
| 删除套装优惠（`delete_bundle_deal`） | [apis/delete-bundle-deal.md](apis/delete-bundle-deal.md) |
| 移除活动商品（`delete_bundle_deal_item`） | [apis/delete-bundle-deal-item.md](apis/delete-bundle-deal-item.md) |
| 获取店铺令牌（兼容辅助） | [api.md](api.md) |

### 脚本运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| api | string | 通用入口必填 | 使用接口清单中精确的 API 名；专用脚本自动选择该操作。 |
| skipDepCheck | boolean | 否 | 默认 false；外部流程已确认依赖时可跳过本地安装检查，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容通用调用器选项；业务封装始终传入此选项，不读取或写入响应缓存。调用器仍可能创建空缓存目录。 |

依赖检查退出码 0 表示找到 `linkfox-shopee-store-auth`；退出码 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示依赖缺失，先安装依赖。检测支持环境变量和常见安装路径。

`LINKFOX_TOOL_GATEWAY` 优先，其次兼容 `SHOPEE_API_BASE_URL`，缺省为 `https://tool-gateway.linkfox.com`；API key 按公共规则支持两种环境变量。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。

各业务入口始终关闭响应缓存，不读取或写入响应缓存文件；完整响应落盘用于按需读取，不作为后续请求的缓存。

业务响应及加工结果仅保存到当前工作目录的 `linkfox/`；当前目录不可写时，在发送请求前报错，不回退到用户目录或临时目录。响应按接口标识命名，`--inline` 同样保留文件。店铺令牌响应仅在内存返回，公共调用器落盘的是脱敏占位对象。

专用入口：`python scripts/<api>.py '<JSON 参数>' [--inline] [--no-cache]`；通用入口：`python scripts/bundle_deal_api.py '<含 api 的 JSON 参数>' [--inline] [--no-cache]`。`--help` 展示用法。JSON 参数须为对象。

## 接口：获取店铺令牌（兼容辅助）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐使用；兼容辅助函数将其转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；同时提供两者时均原样保留，不由脚本擅自选店。 |

对应 `scripts/_shopee_bundle_deal_common.py` 中的 `resolve_store_tokens(params)`，可通过 Python 调用该辅助函数。该函数不属于通用入口的 api 枚举；常规 Bundle Deal 入口只传店铺标识给 developerProxy，由服务端解析令牌，不先请求 storeTokens。

### 响应结构

| 字段 / 对象 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断。 |
| errmsg | string | 网关返回消息。 |
| 完整响应对象 | object | 辅助函数在内存原样返回；令牌对象的字段以实际响应为准。 |
| accessToken | string（若返回） | 辅助调用可用的店铺令牌；本技能不缓存、打印或持久化令牌响应原文。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

令牌仅供辅助调用在内存使用；授权失效或权限不足交由授权技能处理，不在本技能实现授权或自动刷新。

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
  "skillName": "linkfox-shopee-store-bundle-deal",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
