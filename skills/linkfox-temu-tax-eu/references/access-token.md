# Temu accessToken 授权与获取

> 本文件供 **`linkfox-temu-tax-eu`**（及同仓库其它 Temu EU skill）共用。Tax 接口默认 `site=eu`、`tokenPurpose=product-inventory`；若 Partner Tax 文档指定其它 token，以文档为准。

Temu **没有** LinkFox 侧自动 OAuth；`accessToken` 须在 Temu 卖家后台「服务市场 → 授权管理」**手动复制**。与 `LINKFOXAGENT_API_KEY`（LinkFox 用户鉴权）是两套令牌（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）。

## 两种鉴权（勿混淆）

| 令牌 | 用途 | 获取方式 |
|------|------|----------|
| **LinkFox 用户 Token** | 调用 `/temu/proxy`、`/temu/fileDownload` **必填** | `LINKFOXAGENT_API_KEY` 或请求 JSON 的 `token`；Header `Authorization` + `Token`（同 amazon-store-auth）（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理） |
| **Temu accessToken** | Temu 业务 API（经紫鸟转发） | Temu 卖家后台授权后复制 |

```bash
export LINKFOXAGENT_API_KEY="<your-key>"
python scripts/check_linkfox_token.py
```

## tokenPurpose 与场景

| tokenPurpose | 店铺类型 | 推荐 site | 授权应用 |
|--------------|----------|-----------|----------|
| `product-inventory` | 半托管 | `cn` / `partner` | 酷鸟卖家助手 |
| `order-shipping` | 半托管 | `us` / `global` / `eu` | Cyber-ERP酷鸟助手 |
| `full-managed` | 全托管 | `cn` / `partner` | 酷鸟卖家助手 |
| `local-native` | 本土（美/欧主体） | `us` 等 | Cyber-ERP |

## 1. 半托管 — 商品/库存 Token

1. 登录 [seller.kuajingmaihuo.com](https://seller.kuajingmaihuo.com) 或 [agentseller.temu.com](https://agentseller.temu.com)
2. **系统管理** → **服务市场** → **授权管理**
3. **获取授权** → 选择 **「酷鸟卖家助手」**
4. 全选常规和特殊授权 → 确认 → **复制 access_token**
5. 调用 API：`site=cn` 或 `partner`，`managementType=semi-managed`

## 2. 半托管 — 订单/发货 Token

1. 登录 Temu 卖家后台
2. 右上角 **Seller Central** → 切换到目标区域（美区 / 欧区 / 全球）
3. **服务市场** → **授权管理**
4. **获取授权** → 选择 **「Cyber-ERP酷鸟助手」**
5. 全选授权 → 确认 → 复制 token
6. 调用 API：`site=eu` / `global` / `eu`，`managementType=semi-managed`

## 3. 全托管店铺

1. 登录 Temu 平台
2. **系统管理** → **服务市场** → **授权管理**
3. **获取授权** → **「酷鸟卖家助手」** → 全选 → 复制 token
4. 调用 API：`managementType=full-managed`，`site` 通常 `cn` 或 `partner`

## 4. 本土店铺（美区、欧区主体）

1. 登录 Temu
2. **Apps And Services** → **Manage Your Apps**
3. **Authorize a new app** → 搜索 **「Cyber-ERP」**
4. 一般权限与敏感权限全选 → 确认 → 复制 token

## 站点与 OpenAPI 网关

| site | 说明 | Temu 网关 |
|------|------|-----------|
| cn | 中国站 | openapi.kuajingmaihuo.com |
| partner | Partner 网关 | openapi-b-partner.temu.com |
| us | 欧洲站 | openapi-b-eu.temu.com |
| global | 全球区 | openapi-b-global.temu.com |
| eu | 欧洲站 | openapi-b-eu.temu.com |

## 本地保存 Token（推荐）

默认存储：`~/.linkfox/temu-access-tokens.json`（可用 `TEMU_TOKEN_STORE_PATH` 覆盖）。

```bash
# 查看授权步骤
python scripts/temu_token_guide.py '{"shopType":"semi-managed","tokenPurpose":"product-inventory","site":"cn"}'

# 保存 token
python scripts/save_temu_access_token.py '{
  "storeKey": "my-shop",
  "label": "中国半托管",
  "site": "cn",
  "managementType": "semi-managed",
  "tokenPurpose": "product-inventory",
  "accessToken": "PASTE_TOKEN"
}'

# 列出已保存（脱敏）
python scripts/list_temu_access_tokens.py

# 用 storeKey 调 API（无需每次粘贴 token）
python scripts/temu_proxy.py '{
  "storeKey": "my-shop",
  "site": "cn",
  "managementType": "semi-managed",
  "tokenPurpose": "product-inventory",
  "type": "bg.goods.category.mapping",
  "params": {"goodsName": "测试", "goodsNameEn": "Test"}
}'
```

## 注意事项

1. **子账号**：可能无法进入服务市场，需主账号授权。
2. **多站点**：欧洲站、英国站等需分别登录对应后台获取 Token。
3. **有效期**：Token 会过期，过期后重新在后台复制并 `save_temu_access_token.py`。
4. **IP 白名单**：需联系紫鸟开放平台配置调用 IP。
5. **参数小写**：`site`、`managementType` 必须小写。

## 脚本一览

| 脚本 | 说明 |
|------|------|
| `temu_token_guide.py` | 按店铺类型/用途输出授权步骤 |
| `save_temu_access_token.py` | 保存 accessToken 到本地 |
| `list_temu_access_tokens.py` | 列出已保存 token（默认脱敏）|
| `get_temu_access_token.py` | 读取指定 store 的 token |
