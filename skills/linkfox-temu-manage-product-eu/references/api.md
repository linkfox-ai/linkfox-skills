# Temu 欧洲站商品管理 接口说明

本技能定义 24 个商品操作及 1 个加签文件下载操作，共 25 个接口。通用转发和认证探测复用同一网关，不另计操作。

| 操作 | 文档 |
|---|---|
| `bg.local.compliance.goods.list.query` | [合规商品列表](apis/bg-local-compliance-goods-list-query.md) |
| `bg.local.goods.category.check` | [类目预检](apis/bg-local-goods-category-check.md) |
| `bg.local.goods.compliance.edit` | [合规编辑](apis/bg-local-goods-compliance-edit.md) |
| `bg.local.goods.detail.query` | [商品详情](apis/bg-local-goods-detail-query.md) |
| `bg.local.goods.list.query` | [商品列表](apis/bg-local-goods-list-query.md) |
| `bg.local.goods.out.sn.set` | [商品外部编码（Contribution SKU）](apis/bg-local-goods-out-sn-set.md) |
| `bg.local.goods.partial.update` | [部分字段编辑](apis/bg-local-goods-partial-update.md) |
| `bg.local.goods.property.get` | [商品属性获取](apis/bg-local-goods-property-get.md) |
| `bg.local.goods.property.relations.level.template` | [车型库层级模板](apis/bg-local-goods-property-relations-level-template.md) |
| `bg.local.goods.property.relations.template` | [关系属性值查询](apis/bg-local-goods-property-relations-template.md) |
| `bg.local.goods.property.relations` | [商品属性关联数据查询](apis/bg-local-goods-property-relations.md) |
| `bg.local.goods.publish.status.get` | [批量查发布状态](apis/bg-local-goods-publish-status-get.md) |
| `bg.local.goods.sale.status.set` | [商品上下架](apis/bg-local-goods-sale-status-set.md) |
| `bg.local.goods.sku.list.query` | [SKU 列表 / 变体](apis/bg-local-goods-sku-list-query.md) |
| `bg.local.goods.sku.out.sn.set` | [SKU 外部编码（Contribution SKU）](apis/bg-local-goods-sku-out-sn-set.md) |
| `bg.local.goods.stock.edit` | [库存编辑](apis/bg-local-goods-stock-edit.md) |
| `bg.local.goods.update` | [全量编辑](apis/bg-local-goods-update.md) |
| `bg.local.goods.videocoverimage.get` | [视频封面](apis/bg-local-goods-videocoverimage-get.md) |
| `temu.local.goods.delete` | [删除商品](apis/temu-local-goods-delete.md) |
| `temu.local.goods.list.retrieve` | [商品列表搜索（Retrieve）](apis/temu-local-goods-list-retrieve.md) |
| `temu.local.goods.pre.sale.status.edit` | [预售状态编辑](apis/temu-local-goods-pre-sale-status-edit.md) |
| `temu.local.goods.sku.stock.query` | [SKU 库存查询](apis/temu-local-goods-sku-stock-query.md) |
| `temu.local.goods.spec.info.get` | [规格信息查询](apis/temu-local-goods-spec-info-get.md) |
| `temu.local.sku.list.retrieve` | [SKU 列表搜索（Retrieve）](apis/temu-local-sku-list-retrieve.md) |

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

## 运行与授权约定

商品操作统一经 `/temu/proxy`，由 Body type 识别，上游为 `https://openapi-b-eu.temu.com/openapi/router`。加签文件下载单独使用 `/temu/fileDownload`。Partner EU 菜单及来源见 [partner-eu-catalog.md](partner-eu-catalog.md)。各商品接口文档独立包含网关、业务字段、脚本参数、响应和使用限制。

本技能未启用响应缓存，业务封装固定传 `--no-cache`，不会写入或读取响应缓存，保留同一任务内复用已保存响应的方式。公共 run 的空缓存目录不代表启用缓存。封装要求当前工作目录可写，运行前检查并固定输出目录，完整结果保存至 `<cwd>/linkfox/<日期>/<session>/data/`；微秒文件名避免同秒覆盖。

LinkFox 用户密钥支持 JSON 的 token、linkfoxToken、linkfox_token，依次优先于 LINKFOX_AGENT_API_KEY、LINKFOXAGENT_API_KEY；同时保留 Authorization 与 Token 请求头。Temu 令牌支持直接 accessToken 或按 storeKey、site、managementType、tokenPurpose 读取本地库。默认库为 `~/.linkfox/temu-access-tokens.json`，可用 TEMU_TOKEN_STORE_PATH 覆盖，详细 CLI 与授权要求见 [access-token.md](access-token.md)。

`check_linkfox_token.py` 使用 `/temu/proxy` 最小参数探测，支持 CLI 参数并提供脱敏输出；连接失败、HTTP/errcode 异常、无法识别用户或要求重新登录均不能报为密钥已接受。不自动探测或重试收费接口。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

转发 path：`/temu/fileDownload`；本操作没有 Temu type。EU 脚本为 `scripts/temu_eu_file_download.py`，多站点兼容脚本为 `scripts/temu_file_download.py`。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | EU 脚本默认 `eu`，通用脚本显式传入；可选 `cn`、`partner`、`us`、`global`、`eu`，须小写。 |
| managementType | string | 是 | EU 脚本默认 `semi-managed`；通用脚本显式传入，可选 `full-managed`、`semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，直接传入优先。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌库店铺键，由脚本解析为 accessToken，不发送到网关。 |
| tokenPurpose | string | 否 | EU 脚本默认 `product-inventory`，通用脚本默认 `default`，用于本地按站点与托管类型查找。 |
| url | string | 是 | 待下载的 Temu 加签文件 URL，脚本按原值传递，不自行改写签名或 URL 编码。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥，按此顺序优先于两个 API Key 环境变量，不发送到业务 Body。 |
| --inline | CLI flag | 否 | 强制打印完整响应，同时保存。 |
| --no-cache | CLI flag | 否 | 兼容选项；封装始终传入 run，关闭响应缓存。 |

HTTP 超时 150 秒。双请求头 Authorization 与 Token 同值，保留会话请求头。基础地址依次取 LINKFOX_TOOL_GATEWAY、TEMU_API_BASE_URL、STORE_API_BASE_URL，默认正式网关。完整响应写入当前工作目录，禁止临时目录回退。EU 入口补齐站点和托管类型后再解析本地 storeKey。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关响应码，按基础规则判断。 |
| errmsg | string | 网关错误信息，以实际返回为准。 |
| code | integer | 网关业务错误码：1002 为参数或 Token 问题，1003 为转发失败。 |
| body | string | 若网关返回则保留原文；内容结构与编码以实际返回为准，不假定存在下载链接或本地文件。 |
| transportHttpStatus | integer / null | 脚本追加的 LinkFox HTTP 状态，连接失败时为 null。 |
| error | string | 连接失败或无法解析的 HTTP 错误消息，仅出现时返回。 |
| details | string | 无法解析的 HTTP 错误原文，仅出现时返回。 |

脚本返回网关 JSON，不自动解码文件、不自行落盘二进制；完整下载业务字段以真实返回为准，不补造文件内容。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 基础规则通过后检查网关 code；1002 时核对参数及 LinkFox Token，1003 时核对 Temu token、IP 白名单及网络。结合返回内容判断文件下载结果，不能仅凭请求已完成声称文件已下载到本地。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"eu","managementType":"semi-managed","accessToken":"TEMU_EU_TOKEN","url":"https://example.com/signed-file-url"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-manage-product-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
