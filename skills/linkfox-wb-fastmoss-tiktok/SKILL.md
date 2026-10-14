---
name: linkfox-wb-fastmoss-tiktok
display_name: LinkFox FastMoss TikTok选品
display_name_en: LinkFox FastMoss TikTok Product Selection
description: 面向 TikTok Shop 的 FastMoss 商品搜索与热销榜选品数据能力。
description_zh: 面向 TikTok Shop 选品与市场研究，使用 FastMoss 按关键词、市场、类目、店铺类型、销量、GMV、佣金率和达人带货等条件搜索商品，并按日、周、月查看热销榜。
description_en: FastMoss data for TikTok Shop product search, filtering, and daily, weekly, or monthly top-selling rankings.
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


# LinkFox FastMoss TikTok选品

通过 WorkBuddy 的 `LinkFox` 查询 FastMoss 商品搜索与热销榜数据。完整请求、响应字段和展示规则见对应 reference。

## 能力边界

- 商品搜索：按关键词、市场、类目、店铺类型、销量、佣金和达人带货等条件筛选商品。
- 热销榜：按市场、日/周/月、类目以及销量、GMV 或增长率查看榜单。
- 不提供达人画像、视频详情、广告、Listing 编辑、订单、库存、物流或利润与法律结论。
- 商品搜索支持 15 个市场；热销榜支持 9 个市场且存在 T+1 统计延迟。具体枚举以 reference 为准。

## 路由

| 需求 | reference | `toolName` |
|---|---|---|
| 关键词搜索、多维筛选、排序与分页 | `references/linkfox-fastmoss-product-search.md` | `fastmoss/productSearch` |
| 日/周/月热销榜、类目榜与趋势排序 | `references/linkfox-fastmoss-product-rank-top-selling.md` | `fastmoss/productRankTopSelling` |

质量反馈是独立能力，规则见 `references/feedback.md`，不得与上述 MCP 端点混用。

## MCP 调用契约

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- MCP Tool：`proxy_call`
- `toolName` 必须严格使用路由表中的值。
- `arguments` 必须直接放业务请求对象，禁止增加 `body`、`data` 或 `params` 包装层。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 每次只调用选定端点一次。失败、空结果或字段缺失时，不得自动改参数、翻页、切换端点或以相同参数重试。

调用形态：

```json
{
  "toolName": "fastmoss/productSearch",
  "arguments": {
    "keyword": "phone case",
    "region": "US",
    "page": 1,
    "pageSize": 10
  }
}
```

## 响应处理

1. 先检查 MCP 调用是否成功。
2. 再检查代理层返回；若承载业务结果的 `text` 是 JSON 字符串，只解析一次。
3. 最后按业务响应中的状态字段、消息字段和数据字段判断结果。
4. 保留原始字段名、数值单位、市场、时间窗口和分页信息；缺失值标记为 N/A，不跨端点补齐。
5. `total` 是符合条件的记录数，不等于当前页条数；展示价格与 GMV 时保留货币。

## 使用纪律

- 商品搜索至少提供 `keyword` 或 `category` 才有明确语义；热销榜必须提供 `region` 和格式匹配的 `dateInfo`。
- 两个端点的 `pageSize` 最大为 `10`，页码从 `1` 开始。
- 搜索响应的佣金率为小数，`0.10` 表示 10%；榜单响应的佣金率为基点，`1000` 表示 10%。
- 调用会产生积分消耗。翻页、改参数或联查另一个端点前说明额外消耗，由用户决定是否继续。
- 不使用旧网关、本地调用脚本、本地缓存或落盘结果作为替代路径。

## 异常与反馈

授权、计费与权限异常按 `references/onboarding.md` 处理。能力行为异常、结果偏离用户意图或用户明确反馈时，按 `references/feedback.md` 上报；反馈失败不得影响当前查询。

## 积分消耗说明

> 用户会因积分消耗而支付费用。高频调用或用户对消耗预期不明确时，先说明可能的额外消耗，由用户决定是否继续。
