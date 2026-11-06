# 智慧芽专利全文附图 接口说明

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

## 接口：专利全文附图

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/fulltextImage`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 否* | 专利 ID，内部专利标识。 |
| patentNumber | string | 否* | 公开（公告）号，例如 `US20230012345A1`、`CN115000000A`。 |
| limit | string | 否 | 返回图片总量，每次最多 100 张，默认 `"100"`。 |
| offset | string | 否 | 图片结果的分页偏移量，例如 `"0"`、`"20"`；未传入时按服务端行为处理。 |

*`patentId` 和 `patentNumber` 至少需提供其中一个。所有参数值均为字符串类型，最大长度 1000 字符。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | 位置参数，内容为上表请求体；CLI 直接透传 JSON 请求体。 |
| --inline | CLI flag | 否 | 强制完整打印响应，同时仍保存完整响应文件。 |
| --no-cache | CLI flag | 否 | 禁用本次缓存读取和写入。默认使用 24 小时本地缓存。 |
| --help / -h | CLI flag | 否 | 显示中文用法，不发起请求。 |

- 入口：`python scripts/zhihuiya_fulltext_image.py '<JSON 参数>' [--inline] [--no-cache]`。
- 缓存路径为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-fulltext-image/linkfox-zhihuiya-fulltext-image-<参数哈希>.json`；参数经 `ensure_ascii=False`、`sort_keys=True` 的 JSON 序列化后计算 SHA-256，取前 16 位十六进制。文件修改时间在 24 小时内有效；缓存文件直接保存响应 JSON，不叠加第二层缓存。
- 命中缓存时在字典响应中标注 `_cache.hit=true`，仍保存本次完整响应并提示命中。缓存不区分业务成功、错误或空结果；认证、充值后需要新请求时，可显式用 `--no-cache` 跳过已缓存响应，并遵守成本约束。
- `LINKFOX_TOOL_GATEWAY` 优先覆盖默认网关，去掉结尾 `/`；密钥优先取 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头，HTTP 超时保持 150 秒。
- 完整响应及会话索引保存在当前工作目录的 `linkfox/` 下，按 `SESSION_ID` 聚合；未设置时生成进程内稳定的会话 ID。响应以 UTF-8 保存，文件名采用微秒时间戳并通过独占创建避免同一会话的多次响应相互覆盖。禁止将附图查询响应写入 `/tmp`；实际数据目录不可写时在请求前报错，不回退到家目录或临时目录。
- 输出大小阈值、摘要及全量打印行为见 [输出策略](../SKILL.md#输出策略)。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数，即该专利可用的附图总数；用于说明是否仍有更多图片。 |
| data | array | 专利附图列表。 |
| data[].patentId | string | 专利 ID。 |
| data[].pn | string | 公开（公告）号。 |
| data[].fulltextImagePath | string | 图片路径，可用于查看或下载。 |
| data[].imageType | string | 图片类型或类别。 |
| columns | array | 渲染的列，元素结构以实际返回为准。 |
| costToken | integer | 消耗 token。 |
| type | string | 渲染的样式。 |
| errcode | integer / string / null | 网关业务状态码，按公共响应码基本规则判断。认证错误响应示例为 `401`。 |
| errmsg | string | 网关错误消息，例如 `authorized error`；用于解释失败原因。 |
| errorCode | 以实际返回为准 | 若返回此业务状态字段，需结合其值和 `errmsg` 解释业务状态；不得仅因缺少 `errcode` 就忽略 `errorCode` 明确指示的业务错误。基础响应判断仍遵循公共规则。 |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache.hit | boolean | 仅脚本命中字典缓存时附加为 true，不是接口原始业务字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本接口的业务错误依据实际返回的状态码及错误消息解释。正常响应中的 `total=0`、`data=[]` 表示本次未返回附图。
- 若 `errorCode` 或错误消息明确指示业务失败，应解释失败原因，不将缺少图片列表的错误响应当作“该专利没有附图”；认证或算力错误按 onboarding.md 处理。

### 响应示例

认证错误响应示例：

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/fulltextImage" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "US20230012345A1", "limit": "100", "offset": "0"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-fulltext-image",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```