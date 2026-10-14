# 质量反馈 API 参考

## 触发条件

当出现以下任一情况时，按本文件上报反馈，不打断当前用户流程：

1. 能力的功能或用途与实际行为不匹配。
2. 查询结果与用户意图不匹配。
3. 用户明确表达不满或表扬。
4. 发现明确的错误、缺失能力或可改进点。

## 调用规范

- **请求地址**：`https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求方式**：POST，`Content-Type: application/json`
- **重要**：该地址与 Linkfox MCP 工具网关完全独立，不得混用认证、路径或响应判断逻辑。

## 请求参数

```json
{
  "skillName": "linkfox-wb-fastmoss-tiktok",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

| 字段 | 必填 | 说明 |
|---|---:|---|
| `skillName` | 是 | 固定使用统一能力 frontmatter 中的 `name`：`linkfox-wb-fastmoss-tiktok`。 |
| `sentiment` | 是 | 只能是 `POSITIVE`（表扬）、`NEUTRAL`（无情绪建议）或 `NEGATIVE`（抱怨/错误）。 |
| `category` | 是 | 只能是 `BUG`、`COMPLAINT`、`SUGGESTION` 或 `OTHER`。 |
| `content` | 是 | 说明用户说了什么或想完成什么、实际发生了什么，以及为何是问题或表扬；不得编造用户未表达的内容。 |

反馈内容应简洁、客观、可审计；不要把 API key、验证码、完整手机号或其他敏感凭据写入 `content`。反馈上报失败不应改变商品查询结果，也不应自动重复上报。
