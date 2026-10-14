---
name: linkfox-wb-shopify-data
display_name: LinkFox Shopify选品数据
display_name_en: LinkFox Shopify Product Selection Data
description: 面向独立站卖家的 Shopify 商品与店铺选品和市场研究能力。
description_zh: 面向独立站卖家的 Shopify 商品与店铺选品和市场研究能力。当用户需要按关键词、URL、价格、周销量、上架时间、广告、竞争度、货源、发货国家，或按店名、域名、国家、店铺年限、产品数、广告数、月访问量、月订单量和社媒指标筛选 Shopify 市场数据时触发；返回可审计的商品/店铺列表、指标和链接。仅覆盖 Shopify 市场数据查询，不执行店铺后台管理、刊登编辑、订单库存、广告投放或跨平台结论；完整参数见 references/。
description_en: Shopify product and store selection and market research for independent-site sellers, covering product and store filters, public metrics, and links without backend management.
icon: icons/logo.png
version: 2.1.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox Shopify选品数据

通过 WorkBuddy 的 `LinkFox` 查询 Shopify 商品或店铺市场数据。

## 能力边界

- 商品查询：按关键词或 URL、价格、周销量、上架日期、Facebook 广告、竞争度、货源、下架状态、发货国家和排序筛选商品。
- 店铺查询：按名称或域名、国家、创建年限、产品数、广告数、月访问量、月订单量和排序筛选店铺。
- 返回当前可用的市场快照，不提供 Shopify 后台管理、刊登、订单、库存、广告投放、历史趋势或经营结果保证。
- 商品与店铺是不同粒度；从商品转向店铺研究属于第二次收费调用，需由用户决定。

## 路由与 allowlist

| 子能力 | reference | `toolName` | 本地辅助脚本 |
|---|---|---|---|
| Shopify 商品查询 | `references/linkfox-shopify-product-query.md` | `ehunt/shopify/productQuery` | 无 |
| Shopify 店铺查询 | `references/linkfox-shopify-store-query.md` | `ehunt/shopify/storeQuery` | 无 |

只允许以上两个精确且区分大小写的 `toolName`。商品级需求使用商品查询，店铺级需求使用店铺查询，不用另一类结果补猜。

## MCP 调用契约

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- 原业务请求对象直接放入 `arguments`，不得增加 `body`、`params`、`data` 或嵌套 `arguments`。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 禁止 curl、`urllib`、`requests`、`httpx` 或其他方式直连工具网关；MCP 缺失时禁止静默 HTTP fallback。
- 收费调用失败、空结果或不理想时不得自动重试、改词、换 URL、放宽条件或翻页。同一任务内相同 `toolName + arguments` 不得重复调用。

```json
{
  "toolName": "ehunt/shopify/productQuery",
  "arguments": {
    "searchKey": "phone case",
    "country": "US",
    "sortBy": 14,
    "page": 1,
    "pageSize": 20
  }
}
```

## 响应处理

1. 检查 MCP 连接、工具可用性、schema 错误和 `isError`。
2. 代理成功后读取 text 或 structured content；text 是 JSON 字符串时只解析一次。
3. 再检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或消息字段。
4. 最后按对应 reference 读取商品或店铺列表，不把 MCP 外层对象当作业务响应。
5. 错误后不得猜测另一个 `toolName`，不得循环解析字符串化 JSON。

## 使用与展示纪律

- 两类查询的 `page` 从 1 开始，`pageSize` 默认 20、最大 100；范围条件只填一侧时由上游解释为开放区间。
- 商品 `sortBy` 默认 14；未知编码不得猜测。店铺排序枚举与方向见对应 reference。
- 展示查询范围、本页条数、总数、当前页和消耗；商品价格以 USD 口径展示，格式化指标按返回值保留。
- 区分估算、格式化值与明确数值；缺失字段标记 N/A，不推导销量保证、利润或经营结论。
- 新 MCP 链路不提供旧脚本的本地缓存、响应落盘或 stdout 摘要；追溯时保留本次参数、查询时间和原始 MCP 结果。

## 成本、异常与反馈

商品与店铺查询的动态计费均为“本页返回数 × 1.8 积分”，实际以响应和当前计费规则为准。翻页、增大页数或第二次联查前说明额外消耗，由用户决定。

MCP、授权、计费和权限异常按 `references/onboarding.md` 分层处理。Feedback 是独立端点，规则见业务 references；不得与业务 MCP 混用或阻断当前结果。
