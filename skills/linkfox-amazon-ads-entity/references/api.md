# linkfox-amazon-ads-entity — 参数与字段参考（总览）

按 Amazon Ads 广告产品分类维护。

| 广告产品 | 脚本子目录 | 详细参考 |
|---------|-----------|---------|
| **Sponsored Products (SP)** — v3 | `scripts/sp/` | [api/sp.md](./api/sp.md) |
| **Sponsored Brands (SB)** — v4 | `scripts/sb/` | [api/sb.md](./api/sb.md) |

> Sponsored Display (SD) / Sponsored Television (ST) / Amazon DSP 暂未覆盖。

## 通用约定

- 每个脚本接受一个 JSON 字符串作为唯一位置参数
- 鉴权：环境变量 `LINKFOXAGENT_API_KEY`
- 依赖 `linkfox-amazon-ads-auth`（脚本启动自动检查；缺失时 exit 42，stderr 打 `DEPENDENCY_MISSING`）

## 共用参数（SP + SB 均适用）

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `profileId` | number | ✅ | — | 从 ads-auth 获取 |
| `region` | string | ✅ | — | `NA` / `EU` / `FE` |
| `fetchAll` | boolean | 否 | `true` | 自动按分页 token 翻完 |
| `maxResults` | integer | 否 | `100` | 单页 1-100；超限上游可能静默 clamp |
| `skipDepCheck` | boolean | 否 | `false` | 跳过依赖检查 |
| `includeExtendedDataFields` | boolean | 否 | — | 返回扩展字段（部分实体） |
| `locale` | string | 否 | — | 本地化（keywords 支持） |

## 输出格式

```json
{
  "success": true,
  "<entityKey>": [ /* 实体数组 */ ],
  "total": 157,
  "pagesFetched": 2,
  "truncated": false
}
```

客户端过滤时（SP productAds 的 asinFilter/skuFilter）额外带 `serverTotalBeforeClientFilter` + `clientSideFilters`。

失败：
```json
{
  "error": "Upstream HTTP 401",
  "httpStatus": 401,
  "body": "...",
  "pagesFetched": 0
}
```

## 通用错误码

| httpStatus / exit | 含义 | 建议 |
|-------------------|------|------|
| 200 | 成功 | — |
| 400 | 入参结构错 | 核对对应 adProduct 的过滤器结构（api/sp.md 或 api/sb.md） |
| 401 | accessToken 过期 | 调 `linkfox-amazon-ads-auth/scripts/refresh_token.py` 后重试 |
| 403 | profileId 无权限 | 核对 profileId 归属 |
| 429 | 限流 | 间隔 2-5s 重试 |
| exit 42 | 依赖 skill 未安装 | 先装 `linkfox-amazon-ads-auth` |

---

## Feedback API

与上面的工具 API **base URL 不同**：

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-amazon-ads-entity","sentiment":"POSITIVE",
       "category":"OTHER","content":"实体查询结果与预期一致"}'
```

- `sentiment`: `POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`: `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
