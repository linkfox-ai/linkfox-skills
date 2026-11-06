# Shopee 店铺退货退款管理 接口说明

业务接口按操作拆分；每份文档包含独立的调用、参数、响应和业务规则。

| 操作 | 接口文档 |
|---|---|
| `get_return_list` | [查询退货退款列表](apis/get-return-list.md) |
| `get_return_detail` | [查询退货退款详情](apis/get-return-detail.md) |
| `confirm` | [确认退货](apis/confirm.md) |
| `dispute` | [发起退货争议](apis/dispute.md) |
| `get_available_solutions` | [查询可用解决方案](apis/get-available-solutions.md) |
| `offer` | [提出解决方案](apis/offer.md) |
| `accept_offer` | [接受解决方案](apis/accept-offer.md) |
| `convert_image` | [转换凭证图片](apis/convert-image.md) |
| `upload_proof` | [上传退货凭证](apis/upload-proof.md) |
| `query_proof` | [查询退货凭证](apis/query-proof.md) |
| `get_return_dispute_reason` | [查询争议原因](apis/get-return-dispute-reason.md) |
| `cancel_dispute` | [取消退货争议](apis/cancel-dispute.md) |
| `get_shipping_carrier` | [查询退货承运商](apis/get-shipping-carrier.md) |
| `upload_shipping_proof` | [上传退货运单凭证](apis/upload-shipping-proof.md) |
| `get_reverse_tracking_info` | [查询逆向物流轨迹](apis/get-reverse-tracking-info.md) |
| 店铺授权状态辅助 | [查询店铺授权状态](apis/store-tokens.md) |

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

## 运行约定

| 项目 | 约定 |
|---|---|
| 认证依赖 | `scripts/check_auth_dependency.py` 找到 `linkfox-shopee-store-auth` 返回 0；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`。不得在本技能内另行实现授权或令牌逻辑。 |
| 网关地址兼容 | `LINKFOX_TOOL_GATEWAY` 优先，其次 `SHOPEE_API_BASE_URL`，最后默认正式网关；去掉末尾斜杠。 |
| API Key 兼容 | `LINKFOX_AGENT_API_KEY` 优先，其次 `LINKFOXAGENT_API_KEY`；不添加 Bearer 前缀。 |
| 转发与选店 | Returns 经 POST `/shopee/developerProxy` 转发；`path` 为 `api/v2/returns/...`，通常传 `shopId`，也保留 `merchantId`。至少提供一个；服务端解析令牌。 |
| 授权状态辅助查询 | `/shopee/storeTokens` 返回授权状态，不返回原始令牌；辅助函数沿用 `resolve_store_tokens` 名称。Returns 入口直接按店铺/商户选店，不自动调用此辅助接口，也不需要客户端取令牌再转发。 |
| 通用 CLI | `python scripts/returns_api.py '<含 api 的 JSON>' [--inline] [--no-cache]`；`api` 为上表 15 个 Returns 名称之一。独立脚本无需传 `api`。`--help` 只显示本地帮助。 |
| 实际缓存行为 | 所有业务封装调用公共 `call_api.run` 时始终传 `--no-cache`，不读写响应缓存，也不另建缓存层。公共调用器可能创建空缓存目录。 |
| 输出 | 所有操作保存完整业务封装响应，按接口标识命名；保留 `--inline` 与 8 KB 摘要行为。通用入口与独立脚本均按操作名保存，--inline 不改变文件标识。 |
| 保存位置 | 业务封装在请求前检查当前工作目录可写，固定保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`；不回退家目录或临时目录。微秒时间戳避免同秒重复调用覆盖文件。 |
| 会话标识 | `SESSION_ID` 优先；未配置时进程内生成并复用。请求继续携带 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。 |
| 重试 | 不自动重试或切换店铺、参数；1003 等错误也须遵守 SKILL.md 调用约束。写入结果不确定时先核对状态，避免重复提交。 |
| 官方文档 | 各操作提供 `https://open.shopee.com/documents/v2/v2.returns.{api}?module=102&type=1` 链接及脚本文档字符串。上游业务嵌套字段以实际响应与官方定义为准，不假设未列明的类型、必填项、默认值或枚举。 |

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-returns",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
