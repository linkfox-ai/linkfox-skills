# Temu 美国站价格管理 接口说明

本文定义加签文件下载；四个价格操作分别见下列文档，每个文档含独立请求、响应与业务规则。

- [推荐基础价/供货价估算（`temu.local.goods.baseprice.recommend`）](apis/temu-local-goods-baseprice-recommend.md)
- [推荐供货价查询（`temu.local.goods.recommendedprice.query`）](apis/temu-local-goods-recommendedprice-query.md)
- [定价单列表查询（`bg.local.goods.priceorder.query`）](apis/bg-local-goods-priceorder-query.md)
- [批量修改 SKU 基础价（`bg.local.goods.priceorder.change.sku.price`）](apis/bg-local-goods-priceorder-change-sku-price.md)

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

所有业务脚本调用公共 `call_api.run` 时始终传 `--no-cache`，不读取或保存响应缓存。调用器可能创建空缓存目录，但不会保存缓存响应。没有第二层缓存。

| 项目 | 约定 |
|---|---|
| 网关兼容 | `LINKFOX_TOOL_GATEWAY` 优先，其次 `TEMU_API_BASE_URL`、`STORE_API_BASE_URL`，最后默认网关；末尾斜线去除。 |
| LinkFox 认证 | JSON `token` → `linkfoxToken` → `linkfox_token` 的首个非空值优先，其次 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY`；请求头 `Authorization` 与 `Token` 同值。另保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。 |
| Temu 认证 | 直接 `accessToken` 优先；否则使用 `storeKey` + `site` + `managementType` + `tokenPurpose` 从本地精确匹配。美国站包装默认 `us` / `semi-managed` / `product-inventory`；通用入口要求显式 site 和 managementType，tokenPurpose 默认 default。 |
| 本地存储 | `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖；列表默认脱敏。获取授权步骤、保存、列出、读取入口见 [access-token.md](access-token.md)。 |
| JSON 封装 | 美国站价格入口优先取对象类型的 `params`，否则把顶层非控制字段作为业务参数，保留 `request` 嵌套。认证和控制字段不混入业务参数。 |
| 通用入口 | `temu_us_proxy.py` 接受显式 type；`temu_proxy.py` 兼容多站点显式参数。它们不代表另行定义无限数量的业务接口。超出当前四项价格操作时先取得对应完整接口定义。 |
| 输出 | 保存外层 transportHttpStatus 与原始 body，合法 JSON 字符串额外解析为 temuBody。公共调用器仅保存一次完整响应；业务入口只展示该已保存结果。`--inline` 强制全量打印，否则超过 8000 字节显示摘要和最大列表前三条样本。 |
| 输出目录 | `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-price-us-<接口标识>-<timestamp>.json`；SESSION_ID 聚合同一任务；未设置时同一进程复用自动会话标识。业务封装在请求前检查根目录和实际会话 data 目录可写，禁止转存 `/tmp` 或其他目录，不自动回退到其他目录。实际保存失败时明确报错，先核对操作状态，不自动重放请求。 |
| 认证检查 | `check_linkfox_token.py` 使用最小探测请求；它会请求网关，不应为测试自动执行。不能把 401、402、连接失败或服务异常报告为认证成功。 |
| 扩展文档 | [partner-us-catalog.md](partner-us-catalog.md) 列出 Partner 商品菜单和已定义操作；未提供的 sub_menu_code 与估算结果子字段保持未知，不伪造。 |

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 美国站包装默认 us；多站点通用入口显式传 cn / partner / us / global / eu。 |
| managementType | string | 是 | 美国站包装默认 semi-managed；通用入口显式传 full-managed / semi-managed。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本可用 storeKey 精确读取后填入。 |
| url | string | 是 | 需加签下载的资源 URL，原样传入，不提前下载或重写。 |
| storeKey | string | 脚本与 accessToken 二选一 | 本地店铺键，不直接发给网关。 |
| tokenPurpose | string | 否 | 美国站包装默认 product-inventory；通用入口默认 default；仅用于本地查令牌。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户密钥；优先级见脚本运行约定。 |
| --inline | CLI flag | 否 | 全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 兼容选项，业务包装始终禁用缓存。 |

脚本：`scripts/temu_us_file_download.py`、`scripts/temu_file_download.py`。site 与 managementType 须小写；直接下载入口不把认证控制字段发往业务载荷。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| transportHttpStatus | integer / null | 脚本追加的 LinkFox 外层 HTTP 状态码，连接失败时为 null；与网关 code、errcode 和内层 Temu errorCode 分别判断。直接调用网关时从 HTTP 响应读取。 |
| errcode | integer / string / null | 若存在，按公共响应码基本规则判断。 |
| errmsg | string | 若存在，保留网关消息。 |
| code | integer | 网关错误码：1002 参数或 Token 问题，1003 转发失败。 |
| body | string | 网关原始返回体，完整下载结果按实际网关 JSON 保留。 |

文件内容、编码或下载链接等结果字段按实际网关 JSON 说明，不预设字段结构。下载脚本保留完整 JSON，不额外生成 temuBody 或擅自将 body 解码为文件。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `code=1002` 时检查参数与 LinkFox 用户密钥；`code=1003` 时检查 Temu 令牌、IP 白名单和转发网络。
- 返回中没有实际下载结果时不宣称文件已下载；下载脚本请求网关并保存 JSON。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"us","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-file-url"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-price-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
