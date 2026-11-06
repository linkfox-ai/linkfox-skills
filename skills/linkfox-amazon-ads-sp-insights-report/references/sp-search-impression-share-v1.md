# Sponsored Products Search Term Impression Share/Rank（Reporting API v1）报告定义

本文件定义报告入口与固定字段；账号映射、创建报告、状态查询的完整接口定义、curl、业务结果、缓存与账号保护统一见 [api.md](api.md)。

## 入口参数

`python scripts/get_sp_search_impression_share.py '<JSON 参数>' [--inline] [--no-cache]`

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| profileId | integer/string | 是 | - | Long 范围内的正整数或十进制数字字符串，来自 Ads 授权技能；不接受布尔值、小数和越界值。 |
| region | string | 是 | - | `NA` / `EU` / `FE`；去空白并转大写。 |
| startDate | string | 创建模式是 | - | `YYYY-MM-DD`，不晚于 endDate；未给日期先询问。 |
| endDate | string | 创建模式是 | - | `YYYY-MM-DD`，不晚于今天；当天可能不完整，优先昨天及更早。 |
| timeUnit | string | 否 | `DAILY` | `DAILY` / `SUMMARY`，转大写；分别选择 date.value / dateRange.value。 |
| advertiserAccountId | string | 否 | 自动映射 | Ads v1 account ID，仅用于映射失败后的显式恢复；跳过账号映射。 |
| pollInterval | integer | 否 | `60` | 5–300 秒；兼容整数字符串，不接受布尔值或浮点数；建议每分钟一次，避免高频轮询。 |
| maxAttempts | integer | 否 | `10` | 1–120；兼容整数字符串，不接受布尔值或浮点数；默认约 10 分钟等待窗口，两次轮询间才 sleep。 |
| reportId | string | 否 | - | 提供时必须为非空字符串；跳过映射与创建，仅轮询，创建日期无需传入。空值或非法类型在请求前拒绝，不转为创建模式。 |

只允许上表参数，不接受自定义 Amazon 请求头。参数任意嵌套层级都禁止 access token、refresh token、LWA client ID/secret、Authorization 等凭证；键名忽略符号和大小写，联网前递归拒绝。未知参数同样在联网前拒绝；创建日期须严格符合补零的 YYYY-MM-DD，创建字段及枚举也在账号映射前校验。`search-impression-share` 为固定 reportKind，不接受调用方覆盖。

Reporting API v1 为 open beta，权限和限流可能变化；生成通常约 2–10 分钟，偶尔更久。约 5 分钟仍未完成时脚本提示继续等待。默认时间粒度为 DAILY；SUMMARY 改用 dateRange.value，不同时选择两个时间字段。

## 固定字段与 CSV 列

下表类型说明指标含义；实际 CSV 读取和 preview 中所有单元格均保留字符串，不擅自承诺上游 JSON 嵌套对象形态。

| 字段 | 逻辑类型 | 说明 |
|---|---|---|
| date.value | 日期字符串 | DAILY 使用，按日统计。 |
| dateRange.value | 日期范围字符串 | SUMMARY 替换 date.value，汇总区间。 |
| advertiserAccount.id | 标识符 | 报告目标账号；Search Impression Share 的必需非时间维度之一。 |
| adProduct.value | string | 固定 `SPONSORED_PRODUCTS`；Search Impression Share 的必需非时间维度之一。 |
| searchTerm.value | string | 搜索词；第三个必需非时间维度。 |
| metric.impressionShare | number | 搜索词展示份额，例如 0.34；保留原值，若换算百分比须标注。 |
| metric.impressionShareRank | number | 搜索词展示份额排名，例如 3。 |

不得追加 campaign、adGroup、target、keyword、groupBy、fields、维度或自定义过滤；三个非时间维度 advertiserAccount.id、adProduct.value、searchTerm.value 均为 impression share/rank 的官方必需字段，不可删除。

## 官方参考

- [Reporting API v1 overview](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/overview)
- [Reporting API v1 quickstart](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/quickstart)
- [Query advertiser accounts](https://advertising.amazon.com/API/docs/en-us/guides/account-management/query-advertiser-accounts)
- [Search term dimension](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/dimensions/targeting/search-term)
- [Search impression share metrics](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/metrics/impression-share/search)
