# SP-API Auth Scripts Usage Guide

本目录包含 **授权与店铺/令牌管理** 相关的 Python 脚本。若需要拉取报告，请使用 `linkfox-amazon-spapi-report` skill。

## Prerequisites

- Python 3.6 或更高
- 已设置 `LINKFOXAGENT_API_KEY` 环境变量
- 可访问 LinkFox 后端 API（默认 `https://tool-gateway.linkfox.com`）

```bash
export LINKFOXAGENT_API_KEY="your-api-key-here"
```

## Available Scripts

### 1. authorize_url.py

为新店铺生成授权 URL。

**`sellerName`（店铺名）必填**：必须为非空字符串。脚本会在缺失或为空白时直接退出并报错——调用前请先向用户询问一个可识别的店铺名。

```bash
python authorize_url.py '{"region": "NA", "sellerName": "My Store"}'
```

### 2. authorized_stores.py

列出当前用户已授权的所有亚马逊店铺。

```bash
python authorized_stores.py
```

### 3. refresh_token.py

刷新某店铺的 accessToken。

```bash
python refresh_token.py '{"sellerId": "A1234567890", "region": "NA"}'
```

### 4. store_tokens.py

获取某店铺的访问令牌。下游 skill（如 `linkfox-amazon-spapi-report`）会调用它以拿到 `accessToken`。

```bash
python store_tokens.py '{"sellerId": "A1234567890", "region": "NA"}'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| LINKFOXAGENT_API_KEY | API 鉴权 key | 必需 |
| SPAPI_BASE_URL | 后端网关 base URL | https://tool-gateway.linkfox.com |

## Error Codes

- `0`：成功
- `1`：缺少 API key、参数错误、网络/HTTP/权限错误

## Troubleshooting

**API Key 未配置**
```bash
export LINKFOXAGENT_API_KEY="your-key-here"
```

**Connection Refused / 网络错误**
- 确认 `https://tool-gateway.linkfox.com` 能从你的网络访问（或设置 `SPAPI_BASE_URL` 指向其他网关）
- 检查防火墙、代理设置

**403 Unauthorized**
- 店铺可能缺少必要的 SP-API 权限
- 用更完整的权限集合重新授权

**查询令牌返回 1004**
- 核对 sellerId 与 region
- 确认该店铺已完成授权

## Further Documentation

- API Reference: `../references/api.md`
- 授权流程详解: `../references/authorization-flow.md`
- 快速上手: `../references/quick-start.md`
- Skill 文档: `../SKILL.md`
