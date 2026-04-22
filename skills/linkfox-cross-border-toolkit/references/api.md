# LinkFox Cross-Border Toolkit — API 参考

## 调用规范

本综合技能包含 66 个子工具，每个工具调用 LinkFox Tool Gateway API 的不同端点。

- **API 基础地址**：`https://tool-gateway.linkfox.com/`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 子工具 API 端点速查

| 分类 | 技能名 | 端点路径 |
|------|--------|----------|
| Amazon 前台 | linkfox-amazon-search | amazon/search |
| Amazon 前台 | linkfox-amazon-product-detail | amazon/product-detail |
| Amazon 前台 | linkfox-amazon-reviews | amazon/reviews |
| Amazon 前台 | linkfox-amazon-search-by-image | amazon/search-by-image |
| Amazon 前台 | linkfox-amazon-opportunity-report | amazon/opportunity-report |
| ABA | linkfox-aba-data-explorer | aba/data-explorer |
| Keepa | linkfox-keepa-product-search | keepa/product-search |
| Keepa | linkfox-keepa-product-detail | keepa/product-detail |
| Keepa | linkfox-keepa-product-history | keepa/product-history |
| Sorftime | linkfox-sorftime-product-search | sorftime/product-search |
| Sorftime | linkfox-sorftime-product-detail | sorftime/product-detail |
| 卖家精灵 | linkfox-sellersprite-product-search | sellersprite/product-search |
| 卖家精灵 | linkfox-sellersprite-competitor | sellersprite/competitor |
| Jungle Scout | linkfox-junglescout-keyword-by-keyword | tool-jungle-scout/keywords/by-keyword |
| Jungle Scout | linkfox-junglescout-keyword-by-asin | tool-jungle-scout/keywords/by-asin |
| Jungle Scout | linkfox-junglescout-keyword-history | tool-jungle-scout/keywords/historical-search-volume |
| Jungle Scout | linkfox-junglescout-keyword-share-of-voice | tool-jungle-scout/keywords/share-of-voice |
| Jungle Scout | linkfox-junglescout-product-database | tool-jungle-scout/product-database/query |
| Jungle Scout | linkfox-junglescout-sales-estimates | tool-jungle-scout/sales-estimates/query |
| SIF | linkfox-sif-asin-keywords | sif/asin-keywords |
| SIF | linkfox-sif-asin-summary | sif/asin-summary |
| SIF | linkfox-sif-keyword-overview | sif/keyword-overview |
| SIF | linkfox-sif-keyword-traffic | sif/keyword-traffic |
| 极目 | linkfox-jiimore-niche-by-keyword | jiimore/niche-by-keyword |
| 极目 | linkfox-jiimore-niche-by-asin | jiimore/niche-by-asin |
| 极目 | linkfox-jiimore-niche-info | jiimore/niche-info |
| 极目 | linkfox-jiimore-niche-review | jiimore/niche-review |
| 极目 | linkfox-jiimore-product-discovery | jiimore/product-discovery |
| TikTok | linkfox-echotik-product-search | echotik/product-search |
| TikTok | linkfox-echotik-new-product-rank | echotik/new-product-rank |
| TikTok | linkfox-fastmoss-product-search | fastmoss/product-search |
| TikTok | linkfox-fastmoss-top-selling | fastmoss/top-selling |
| Shopee | linkfox-youying-shopee-product-search | youying/shopee-product-search |
| Walmart | linkfox-walmart-search | walmart/search |
| eBay | linkfox-ebay-search | ebay/search |
| 1688 | linkfox-dld-product-billboard | dld/product-billboard |
| 1688 | linkfox-dld-product-search | dld/product-search |
| Google Trends | linkfox-google-trends-keyword | google-trends/keyword |
| Google Trends | linkfox-google-trends-rising | google-trends/rising |
| Web Search | linkfox-tsearch-web-search | tsearch/web-search |
| AI 图像 | linkfox-multimodal-generate-image | multimodal/generate-image |
| AI 图像 | linkfox-multimodal-recognize-image | multimodal/recognize-image |
| AI 图像 | linkfox-multimodal-extract-attributes | multimodal/extract-attributes |
| AI 图像 | linkfox-multimodal-product-similarity | multimodal/product-similarity |
| 标题分析 | linkfox-product-title-analyze | product-title/analyze |
| 睿观 | linkfox-ruiguan-patent-design | ruiguan/patent-design |
| 睿观 | linkfox-ruiguan-utility-patent | ruiguan/utility-patent |
| 睿观 | linkfox-ruiguan-copyright | ruiguan/copyright |
| 睿观 | linkfox-ruiguan-graphic-trademark | ruiguan/graphic-trademark |
| 睿观 | linkfox-ruiguan-text-trademark | ruiguan/text-trademark |
| 睿观 | linkfox-ruiguan-image-compliance | ruiguan/image-compliance |
| 智慧芽 | linkfox-zhihuiya-patent-image-search | zhihuiya/patentImageSearch |
| 智慧芽 | linkfox-zhihuiya-simple-bibliography | zhihuiya/simpleBibliography |
| 智慧芽 | linkfox-zhihuiya-bibliography | zhihuiya/bibliography |
| 智慧芽 | linkfox-zhihuiya-claim-data | zhihuiya/claimData |
| 智慧芽 | linkfox-zhihuiya-claim-translated | zhihuiya/claimDataTranslated |
| 智慧芽 | linkfox-zhihuiya-abstract-translated | zhihuiya/abstractDataTranslated |
| 智慧芽 | linkfox-zhihuiya-description | zhihuiya/descriptionData |
| 智慧芽 | linkfox-zhihuiya-description-translated | zhihuiya/descriptionDataTranslated |
| 智慧芽 | linkfox-zhihuiya-legal-status | zhihuiya/legalStatus |
| 智慧芽 | linkfox-zhihuiya-pdf | zhihuiya/pdfData |
| 智慧芽 | linkfox-zhihuiya-cited-references | zhihuiya/patentForwardCitation |
| 智慧芽 | linkfox-zhihuiya-cited-by | zhihuiya/patentCited |
| 智慧芽 | linkfox-zhihuiya-patent-family | zhihuiya/patentFamily |
| 智慧芽 | linkfox-zhihuiya-fulltext-image | zhihuiya/fulltextImage |
| 智慧芽 | linkfox-zhihuiya-abstract-image | zhihuiya/abstractImage |

> 智慧芽路径为网关真实路径（camelCase，区分大小写），完整参数与 curl 见本目录 `references/zhihuiya.md` 或各独立技能目录下的 `references/api.md`。

## 错误码

所有工具共享统一的错误码体系：

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

## curl 示例（通用模式）

```bash
curl -X POST https://tool-gateway.linkfox.com/<endpoint> \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '<request-body-json>'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-cross-border-toolkit",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use `linkfox-cross-border-toolkit`
- `sentiment`: Choose ONE — `POSITIVE`, `NEUTRAL`, `NEGATIVE`
- `category`: Choose ONE — `BUG`, `COMPLAINT`, `SUGGESTION`, `OTHER`
- `content`: Include what happened and why
