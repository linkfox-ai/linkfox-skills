# linkfox-mercado-product-selection 子能力归档

## 功能说明

通过 `LinkFox.proxy_call` 查询 Mercado Libre 商品、官链/目录、关键词、类目、趋势、店铺、评论、站点汇率及套餐用量。原 endpoint 为 `/mercado/productSelection`，精确 MCP `toolName` 为 `mercado/productSelection`。

本子能力覆盖 24 个下游 operation：`itemInfo`、`itemHistory`、`itemSearch`、`catalogInfo`、`catalogHistory`、`catalogSearch`、`keywordDateSearch`、`keywordMonthSearch`、`keywordReverse`、`categorySearch`、`categorySmallSearch`、`trendBrandTopBrand`、`trendBrandTopItem`、`trendBrandTopSeller`、`trendNewItems`、`trendPrice`、`trendSale`、`trendSoldHis`、`trendStatistical`、`trendStoreInventoryType`、`sellerSearch`、`reviewSearch`、`rateInfo`、`myUsage`。

## 能力边界与选择规则

- 商品 operation 用于单品信息、销量历史和商品筛选；官链 operation 用于目录对象的同类查询，`itemId` 与 `productId` 不互换。
- 关键词 operation 区分按天、按月和指定商品反查；类目 operation 是免费定位入口，只有类目名称时先解析 ID。
- 趋势 operation 按品牌、商品、店铺、新品、价格、销量、历史、汇总和仓储结构选择；店铺、评论、汇率和套餐用量分别使用对应 operation。
- 站点为 `MLM`、`MLB`、`MLA`、`MLC`；`MCO` 仅限各 operation 文档明确支持的场景。
- 免费 operation 为 `categorySearch`、`categorySmallSearch`、`reviewSearch`、`rateInfo`、`myUsage`；其他 operation 当前后端通常返回 `costToken = 16000`。收费调用前应让用户知情，失败或空结果不得自动重试。
- `data` 经常是文本；使用真实返回的 `data`/`contentText`，不要套用不存在的统一业务字段。

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`mercado/productSelection`
- `arguments`：原请求体 `{"toolName":"<operation>","arguments":{...}}`。内层 `toolName` 才是 operation，业务参数放在内层 `arguments`；不得扁平化或额外包裹。
- WorkBuddy 自动注入授权；禁止传 `headers`、Authorization、API Key、token、JWT、手机号或上游凭证。
- text JSON 只解析一次，并区分 MCP/代理错误与下游 `errcode`/`code`。MCP 不可用时禁止 HTTP fallback。
- 同一任务内相同 MCP `toolName + arguments` 不得重复调用；追加收费调用前说明消耗并取得用户同意。

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {
    "toolName": "categorySearch",
    "arguments": {
      "siteId": "MLM",
      "searchText": "Auriculares"
    }
  }
}
```

## 请求参数

| 字段路径 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `toolName` | string | 是 | 固定为 MCP endpoint `mercado/productSelection`。 |
| `arguments` | object | 是 | 原下游请求体。 |
| `arguments.toolName` | string | 是 | 24 个 operation 之一。 |
| `arguments.arguments` | object | 是 | 对应 operation 的业务参数；完整字段见 `mercado-tool-reference.md`。 |

## 响应字段

响应字段来源：`skills/linkfox-mercado-product-selection/references/api.md`。来源未定义 `data` 内动态文本或 JSON 的统一子字段，不得臆造。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `code` | string | 封装层状态；成功示例为 `"200"`。 |
| `msg` | string | 封装层消息；成功示例为 `"ok"`。 |
| `errcode` | integer | 网关状态码；成功为 `200`。 |
| `errmsg` | string | 网关状态消息。 |
| `type` | string | 当前通常为 `rawMcpToolResult`。 |
| `toolName` | string | 实际执行的下游 operation。 |
| `charged` | boolean | 该 operation 是否收费。 |
| `data` | string / array / object | 解包后的业务数据；多数为文本，也可能为解析后的 JSON 数组或对象。 |
| `rawResponse` | object | 来源记载当前为空对象 `{}`，没有定义子字段。 |
| `contentText` | string | MCP text content 拼接原文。 |
| `textParsedAsJson` | boolean | `contentText` 是否成功解析为 JSON。 |
| `total` | integer / absent | 可推断时出现的记录数；文本结果中省略。 |
| `costToken` | integer | 本次 token 成本；收费 operation 16000，免费 operation 0。 |
| `costTime` | integer | 后端耗时，毫秒。 |

## 错误与成本

`errcode=1002` 表示参数、内层 operation 或参数对象不合法；`errcode=500` 表示上游异常。401、402、403 分别按 `onboarding.md` 的授权、积分和权限规则处理。免费与收费 operation 清单及完整错误码见 `api.md`，协议错误码见 `mercado-tool-reference.md`。

## 详细参考

- `api.md`：MCP 调用结构、共享响应、错误与 Feedback API。
- `mercado-tool-reference.md`：24 个 operation 的完整必填/可选参数、站点、分页和排序规则。
- `onboarding.md`：MCP、WorkBuddy 自动授权和积分异常处理。

## 原能力约束

1. 不直连 XP-MCP 或旧 HTTP 网关，不索取任何凭证。
2. 参数字段名严格遵循 `mercado-tool-reference.md`，内层 `arguments` 必须为对象。
3. 业务空结果不是系统故障，也不得作为自动追加调用的理由。
4. 反馈只上报脱敏的意图、行为和问题；Feedback API 固定 `skillName` 为 `linkfox-mercado-product-selection`。
5. 旧脚本的 24 小时缓存、自动落盘、会话元数据和 stdout 摘要已移除，MCP 不提供这些本地行为。
