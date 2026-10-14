# Get Video Performances

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-analytics/references/apis/get_video_performances.md`；只按其响应契约核对字段表 |

```json
{
  "toolName": "tiktokShop/developerProxy",
  "arguments": {"appType": "erp", "openId": "<openId>", "path": "analytics/202403/shop_videos/performance", "method": "GET"}
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

> 官方文档：https://partner.tiktokshop.com/docv2/page/get-video-performances-202403

## LinkFox 转发映射（本 skill）

| 项 | 值 |
|----|----|
| 具名 api | `get_video_performances` |
| 脚本 | `proxy_call` |
| 网关 | `POST tiktokShop/developerProxy` |
| appType | **`erp`（固定）** |
| 上游 path | `analytics/202403/shop_videos/performance` |
| method | `GET` |
| shop_cipher | 是 |
| 令牌 | 网关按 `openId` + `appType=erp` 从库取 token（401/过期自动刷新并重试一次） |

### developerProxy 示例

```json
{
  "appType": "erp",
  "openId": "7010...",
  "path": "analytics/202403/shop_videos/performance",
  "method": "GET",
  "queryString": "shop_cipher=GCP_...&start_date=20240301&end_date=20240331&page_size=20"
}
```

### 脚本示例

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

---

## 官方接口原文（整理）

> Partner Center 需登录；以下按官方 Open API 约定与公开 SDK（Analytics / shop_videos/performance）整理。完整字段以 Partner Center 为准。

# Path: /analytics/202403/shop_videos/performance
# Method: [GET]
# Function Description
Get performance metrics for shop videos within a date range (views, engagement, GMV/orders related to videos, etc.).

# Common Parameters
| Properties | Location | Type | Require | Sample | Properties description |
| --- | --- | --- | --- | --- | --- |
| shop_cipher | query | string | Y | GCP_... | Shop cipher from Get Authorized Shops |
| content-type | header | string | Y | application/json | Allowed type: application/json |

# Request Query Parameters
| Properties | Type | Require | Sample | Properties description |
| --- | --- | --- | --- | --- |
| start_date | string | Y | 20240301 | Start date (`YYYYMMDD`) |
| end_date | string | Y | 20240331 | End date (`YYYYMMDD`) |
| page_size | int | N | 20 | Page size |
| page_token | string | N |  | Pagination token from previous response |
| currency | string | N | USD | Currency for monetary metrics |
| sort_field | string | N |  | Sort field (as documented by Partner Center) |
| sort_order | string | N | DESC | Sort order |
| granularity | string | N | DAY | Optional time granularity when supported |

> `app_key` / `sign` / `timestamp` 由紫鸟注入，调用方不要传。

# Request Sample
```PlainText
https://open-api.tiktokglobalshop.com/analytics/202403/shop_videos/performance?shop_cipher=ROW_...&start_date=20240301&end_date=20240331&page_size=20&app_key=...&timestamp=...&sign=...
```

# Response Parameters
| Properties | Type | Sample | Properties description |
| --- | --- | --- | --- |
| code | int | 0 | Status code |
| message | string | Success | Message |
| request_id | string | ... | Request id |
| data | object |  | Payload |
| ^videos / ^performances | []object |  | Video performance rows（字段名以线上为准） |
| ^^video_id | string |  | Video ID |
| ^^metrics | object |  | Views / clicks / orders / GMV 等指标 |
| ^next_page_token | string |  | Next page token |

# Response Sample
```json
{
  "code": 0,
  "data": {
    "videos": [],
    "next_page_token": ""
  },
  "message": "Success",
  "request_id": "20240301094500123456789ABCDE"
}
```

## Agent 注意事项

1. 必须传 `start_date` / `end_date`；时间格式优先 `YYYYMMDD`。
2. 展示时按视频维度汇总关键指标（浏览、成交、GMV 等，以响应字段为准）。
3. 若 path 未放行返回网关 `1005`，联系运维放行 `analytics/`。
4. 达人侧发视频请用 `linkfox-tiktok-video`，不要混用本 skill。
