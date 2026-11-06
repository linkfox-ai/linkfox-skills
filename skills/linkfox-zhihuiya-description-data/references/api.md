# 智慧芽专利说明书查询 接口说明

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

## 接口：查询专利说明书

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/descriptionData`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利ID（专利ID和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利ID）。多个用英文逗号隔开，上限100条。最大长度60000字符。 |
| patentNumber | string | 条件必填 | 公开公告号（专利ID和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利ID）。多个用英文逗号隔开，上限100条。最大长度60000字符。 |
| replaceByRelated | string | 否 | 当前专利说明书无法获取时是否用同族专利的说明书替代：`1` 是，`0` 否。最大长度1000字符。 |

#### 参数约定与使用限制

- 单项查询直接传标识字符串；批量输入示例为 `CN115099012A,US20230012345A1,EP4123456A1`。同时提供两种标识不表示合并查询两组专利。
- `replaceByRelated` 的缺省行为未明确，不推定省略时一定启用或禁用替代。
- 仅支持按专利标识查询，不能使用关键词、申请人名称或分类号搜索。并非每项专利都有可用说明书；启用同族替代也不保证有结果。
- 标识选择、批量拼接和同族替代由调用方按以上约定准备；脚本透传 JSON，不自动拆分批次、重试或追加同族查询。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON | 是 | 第一个位置参数，对应以上 POST Body。 |
| --inline | CLI flag | 否 | 默认关闭；强制完整打印响应，同时保存文件。 |
| --no-cache | CLI flag | 否 | 默认关闭；启用时不读取或写入响应缓存，仍保存本次完整响应。 |

- 命令：`python scripts/zhihuiya_description_data.py '<JSON 参数>' [--inline] [--no-cache]`。缺少参数或 JSON 解析失败时以退出码 1 结束，不发起请求。
- 只使用 `scripts/call_api.py` 的一层 24 小时缓存，目录为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-description-data/`；以排序后的 JSON 计算 SHA-256 前 16 位的缓存键，文件名为 `linkfox-zhihuiya-description-data-<缓存键>.json`。未过期的同参数结果可跨进程复用，空结果或错误对象也会缓存；不自动变更参数重试。
- 缓存命中时仍保存完整响应，并通过 `_cache.hit` 和终端提示标注命中；`--no-cache` 不会删除已存在的缓存。
- 网关使用 `LINKFOX_TOOL_GATEWAY`，去掉尾部 `/`；未配置时使用公共规则默认地址。密钥优先取 `LINKFOX_AGENT_API_KEY`，其次取兼容变量 `LINKFOXAGENT_API_KEY`；缺失时提示 `API Key 未配置` 并以退出码 1 结束。
- 请求头 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 透传对应环境变量；未设置时传空字符串。
- 完整响应按 UTF-8 保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-description-data-<timestamp>.json`，并维护会话 `_meta.json` 与 `index.jsonl`。同秒多次查询或缓存命中时，业务入口独占创建文件；若文件名已存在，递增时间戳，避免覆盖先前响应。`SESSION_ID` 缺省时在进程内生成稳定会话标识。
- 业务入口在请求前检查当前工作目录下 `linkfox/` 可写，并固定数据根目录；不采用 `ACPX_WORKSPACES`、家目录或临时目录的回退。目录不可写时直接报错，不继续请求。
- 标准输出先给出保存路径；格式化响应不超过 8000 UTF-8 字节时全量输出，否则显示顶层字段、常见计数和最大列表的前 3 条样本。`--inline` 可强制全量输出。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 返回的专利记录数 |
| data | array | 专利列表，每个元素包含说明书数据；每条对应一条专利说明书结果。 |
| data[].patentId | string | 专利ID |
| data[].pn | string | 公开（公告）号 |
| data[].pnRelated | string | 替代专利的公开号（仅当使用同族专利替代时提供） |
| data[].description | array | 说明书内容章节 |
| columns | array | 渲染的列定义 |
| costToken | integer | 消耗token；按返回原值保留，用户算力以网关实际扣费记录为准，不按记录条数自行换算。 |
| type | string | 渲染的样式 |

说明书章节数组和列定义数组的元素结构未明确；保留实际返回的嵌套数据，不推定字段或补造章节。

#### 状态及兼容字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断；认证失败示例返回 401。 |
| errmsg | string | 网关消息或具体错误原因，如 `authorized error`。 |
| errorCode | 未明确 | 兼容状态字段，`200` 表示成功、`401` 表示未授权；响应也可能使用 `errcode`。若实际返回则原样保留用于诊断，响应判断仍遵循公共规则，不推定两者必然同时返回或具有固定对应关系。 |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅本地缓存元信息，不是服务端业务字段。 |
| _cache.hit | boolean | 缓存命中时为 true。 |
| error | string | HTTP 错误无可解析 JSON 时的错误提示，或连接失败原因。 |
| details | string | HTTP 错误正文无法解析为 JSON 时保留的原始正文。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应但 `total=0`、`data` 为空或说明书章节不可用时，说明本次未取得目标说明书，不直接判定为系统错误；建议核对专利标识或按用户意愿尝试同族版本。

### 响应示例

认证失败响应示例：

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/descriptionData" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "CN115099012A", "replaceByRelated": "1"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-description-data",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```