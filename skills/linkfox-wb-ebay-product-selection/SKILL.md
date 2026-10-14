---
name: linkfox-wb-ebay-product-selection
display_name: LinkFox eBay选品
display_name_en: LinkFox eBay Product Selection
description: 面向跨境卖家的 eBay 商品选品与市场浏览能力，支持按关键词、站点、价格、成色、购买形式和卖家位置检索当前 listing，并用于价格、已售商品与拍卖机会研究。
description_zh: 面向跨境卖家的 eBay 商品选品与市场浏览能力。当用户需要在 eBay 搜索商品、发现竞品、比较价格、研究已售或已结束 listing、查看拍卖、按站点和筛选条件评估市场机会时触发；返回商品标题、价格、货币、成色、运费、卖家、销量、竞拍数、推广标识和详情链接等前台数据。仅覆盖 eBay 当前 listing 搜索，不覆盖卖家账户、刊登编辑、订单、广告或跨平台比价；完整参数见 references/linkfox-ebay-search.md，认证与引导见 references/onboarding.md。
description_en: eBay product selection and marketplace browsing for cross-border sellers. Search current listings by keyword, site, price, condition, buying format, seller location, and other filters for competitor, sold-item, and auction research. It does not manage seller accounts, listings, orders, or ads.
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


# LinkFox eBay选品

通过 WorkBuddy 的 `LinkFox` 搜索 eBay 当前前台 listing，用于商品发现、竞品浏览、价格对照、已售/已结束 listing 参考、拍卖浏览和区域市场观察。

## 能力边界

- 支持关键词、eBay 站点、价格、成色、购买形式、排序、商品位置、配送范围、类目和展示条件筛选。
- `showOnly: "Sold,Complete"` 用于已售/已结束商品研究；`buyingFormat: "Auction"` 配合 `orderBy: "1"` 可查看即将结束的拍卖。
- 单页上限 200；价格按搜索站点的本地货币返回。
- 数据是当前查询结果，不提供完整历史价格、长期销量序列或未来预测。
- 不管理卖家账户、刊登、订单或广告，也不提供跨平台比价。

## 路由与工具选择

| 子能力 | 适用需求 | reference | `toolName` | 本地辅助脚本 |
|---|---|---|---|---|
| `linkfox-ebay-search` | 当前 listing、已售/已结束商品、拍卖、价格、成色、站点、位置、类目和分页搜索 | `references/linkfox-ebay-search.md` | `ebay/search` | 无 |

只有上述 `toolName` 在本 skill 的业务 allowlist 中。它区分大小写，必须精确匹配。超出 eBay 商品搜索边界时直接说明，不猜测其他端点。

## MCP 调用契约

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- `arguments` 直接使用业务请求对象，不增加 `body`、`params`、`data` 或嵌套 `arguments`。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 禁止使用 curl、`urllib`、`requests`、`httpx` 或其他方式直连工具网关；MCP 缺失时禁止静默 HTTP fallback。
- 收费调用失败、空结果或不理想时不得自动重试、放宽条件或换页。同一任务内相同 `toolName + arguments` 不得重复调用。

```json
{
  "toolName": "ebay/search",
  "arguments": {
    "keyword": "wireless earbuds",
    "ebayDomain": "ebay.com",
    "page": 1,
    "pageSize": 50,
    "orderBy": "12"
  }
}
```

## 响应处理

1. 检查 MCP 连接、工具可用性、schema 错误和 `isError`。
2. 代理成功后读取 text 或 structured content；text 是 JSON 字符串时只解析一次。
3. 再检查下游 `errcode`、`errorCode`、`errmsg` 或其他消息字段。
4. 最后按 reference 读取 `total`、`products`、渲染信息和消耗字段。
5. 不把 MCP 外层对象当作业务响应，不循环解析字符串化 JSON，不在错误后猜测另一个 `toolName`。

## 使用纪律

- 优先使用最少参数满足需求。多成色用 `|` 连接，多个 `showOnly` 值用逗号连接。
- 只有用户明确需要更多结果、绕过下游缓存或调整筛选时才发起新请求。
- 当 `total` 大于当前页条数时可说明还有后续结果，但不得自动翻页。
- `noCache: true` 会要求下游获取新结果，应谨慎使用并说明可能产生额外消耗。
- 新 MCP 链路不提供旧脚本的本地 24 小时缓存、响应落盘或 stdout 摘要；需要追溯时保留本次参数、查询时间和原始 MCP 结果。

## 展示规则

1. 默认以表格展示标题、价格或区间、货币、成色、配送、卖家、销量/竞拍数、推广标识和详情链接。
2. 始终注明站点和货币；不同站点的数值不得直接相加比较。
3. 已售查询注明其为当前接口返回的已售/已结束 listing 参考，不等同完整历史成交数据。
4. 好评率不是平台担保；拍卖当前价不是最终成交价；缺失字段标记 N/A，不补猜。
5. `sponsored=true` 时明确标记赞助/推广商品。
6. 说明 `total`、当前页和 `pageSize`，不要把当前页条数当成总量。

## 异常、反馈与成本

MCP、授权、计费和权限异常按 `references/onboarding.md` 分层处理。质量反馈规则位于业务 reference 的独立 Feedback 章节，反馈调用不得与 eBay 搜索端点混用，也不得中断当前流程。

> 用户会因积分消耗而支付费用。高频调用、翻页、改条件或启用 `noCache` 前说明可能的额外消耗，由用户决定是否继续。
