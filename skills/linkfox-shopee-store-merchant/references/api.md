# Shopee 商户信息与资源查询 接口说明

包含 6 个 Merchant 转发操作和 1 个授权状态查询兼容辅助接口；不含公共 onboarding 与 Feedback。

- [查询商户资料（get_merchant_info）](apis/get-merchant-info.md)
- [查询商户下属店铺（get_shop_list_by_merchant）](apis/get-shop-list-by-merchant.md)
- [查询商户仓库位置（get_merchant_warehouse_location_list）](apis/get-merchant-warehouse-location-list.md)
- [查询商户仓库列表（get_merchant_warehouse_list）](apis/get-merchant-warehouse-list.md)
- [查询可使用仓库的店铺（get_warehouse_eligible_shop_list）](apis/get-warehouse-eligible-shop-list.md)
- [查询商户预付账户（get_merchant_prepaid_account_list）](apis/get-merchant-prepaid-account-list.md)
- [查询已授权店铺或商户状态（兼容辅助接口）](apis/store-tokens.md)

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

| 项目 | 约定 |
|---|---|
| 商户范围 | Merchant 为商户级 API，应通过授权技能取得 `merchantId`，主要用于 CNSC/CBSC 跨境卖家；本地卖家通常不需要。 |
| 标识兼容 | 网关与脚本支持 `shopId` 或 `merchantId` 至少一项的输入方式；Merchant 查询应明确传入 `merchantId`。两者同时传入时不丢弃任何一项，应属于同一授权目标。 |
| 上游商户公共参数 | 网关将显式传入的 `merchantId` / `shopId` 分别转发为上游 `merchant_id` / `shop_id`；仅传 `shopId` 不会自动补出 `merchant_id`。不在本技能内实现签名或令牌逻辑。 |
| 授权分工 | `/shopee/storeTokens` 查询已绑定授权状态，不返回原始令牌；兼容辅助函数只传标识，使用默认 `appType=erp`。六项 Merchant 脚本直接交由 developerProxy 服务端解析令牌，不额外查询授权状态。 |
| 依赖检测 | `python scripts/check_auth_dependency.py [--json]`；退出码 0 表示找到认证技能，42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得自行实现授权。 |
| 依赖路径 | 保留 `LINKFOX_SKILLS_DIR`、`SKILLS_DIR`、`CURSOR_SKILLS_DIR`、`HERMES_SKILLS_EXTERNAL_DIRS`、OpenClaw 环境、当前目录、相邻技能目录及用户安装路径检测。 |
| 基础地址兼容 | `LINKFOX_TOOL_GATEWAY` 优先，其次 `SHOPEE_API_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。 |
| 调用元信息 | 环境变量 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 继续以同名请求头传递；未设置时为空字符串。 |
| 命令入口 | `python scripts/<操作名>.py '<JSON 参数>' [--inline] [--no-cache]`；通用入口 `python scripts/merchant_api.py '<含 api 字段的 JSON>' [--inline] [--no-cache]`。 |
| 响应缓存 | 业务封装始终向公共 `call_api.run` 传入 `--no-cache`，不读写响应缓存、不引入第二层缓存。公共调用器可能创建空 `.cache` 目录。 |
| 输出 | 六项 Merchant 脚本不使用响应缓存。所有业务入口将加工后完整结果保存至当前工作目录的会话数据目录；小响应完整输出，大响应摘要，`--inline` 强制全量。 |
| 文件保护 | 请求前检查 `<cwd>/linkfox` 及实际会话数据目录可写，失败即报错，不回退到家目录或临时目录；连续调用使用高精度时间避免同秒覆盖。请求后核验完整落盘内容，写入失败或不完整时抛出文件错误，不作为正常返回。 |
| 商户保护 | 六项 Merchant 操作均为读取；不替用户切换商户，不自动翻页或重试，不通过跳过依赖检查绕过店铺授权。 |
| 官方文档 | 每个操作文件及脚本保留 `https://open.shopee.com/documents/v2/v2.merchant.<api>?module=93&type=1`。 |

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-merchant",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
