# Amazon SP-API 授权快速开始指南

本指南帮助你快速上手使用亚马逊 SP-API 授权功能。

## 前置条件

1. **已部署的服务**:
   - linkfox-agent-ecom-plat 服务已启动
   - 紫鸟代理服务可访问
   - 数据库已正确配置

2. **已配置的环境**:
   - 回调地址已添加到紫鸟白名单
   - gateway.url 配置正确

3. **用户认证**:
   - 用户已登录并获取 Token

## 5分钟快速授权

> **重要：店铺名（`sellerName`）必填**  
> 调用 `/spApi/authorizeUrl` 时**必须**传入非空的 `sellerName`，用于在系统中标识该授权店铺（多店铺时便于区分）。若用户未提供，请先询问用户填写后再请求授权链接。脚本 `authorize_url.py` 会在本地校验该字段。

### 第一步：获取授权链接

**调用接口**:
```bash
POST /spApi/authorizeUrl
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "region": "NA",
  "sellerName": "我的店铺"
}
```

**预期响应**:
```json
{
  "authorizeUrl": "https://sellercentral.amazon.com/apps/authorize/consent?..."
}
```

**操作**: 复制 `authorizeUrl` 的值

### 第二步：浏览器授权

1. 在浏览器中打开上一步获取的 `authorizeUrl`
2. 使用亚马逊卖家账号登录
3. 查看并同意授权请求
4. 点击"确认"或"Authorize"按钮
5. 等待页面跳转（自动完成授权保存）

### 第三步：验证授权成功

**调用接口**:
```bash
POST /spApi/authorizedStores
Content-Type: application/json
Authorization: Bearer <your-token>
```

**预期响应**:
```json
{
  "stores": [
    {
      "sellerName": "我的店铺",
      "sellerId": "A1234567890",
      "region": "NA"
    }
  ],
  "total": 1
}
```

如果看到店铺信息，说明授权成功！

## 使用授权令牌

### 获取访问令牌

**调用接口**:
```bash
POST /spApi/storeTokens
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "sellerId": "A1234567890",
  "region": "NA"
}
```

**预期响应**:
```json
{
  "sellerId": "A1234567890",
  "region": "NA",
  "accessToken": "Atza|IwEBIA...",
  "refreshToken": "Atzr|IwEBIJ...",
  "tokenType": "bearer",
  "expiresIn": "3600"
}
```

### 使用访问令牌调用 Amazon SP-API

使用返回的 `accessToken` 作为请求头：

```bash
GET https://<endpoint>/orders/v0/orders
x-amz-access-token: Atza|IwEBIA...
```

## 令牌管理

### 令牌过期时间

- **accessToken**: 通常 1 小时（3600秒）
- **refreshToken**: 长期有效，用于刷新 accessToken

### 检查令牌是否即将过期

从 `/spApi/storeTokens` 响应中获取 `expiresIn` 值：
- 如果小于 300 秒（5分钟），建议立即刷新
- 如果大于 300 秒，可以继续使用

### 刷新过期令牌

**调用接口**:
```bash
POST /spApi/refreshToken
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "sellerId": "A1234567890",
  "region": "NA"
}
```

**预期响应**:
```json
{
  "authRecordId": 123,
  "accessToken": "Atza|IwEBIA...(新令牌)",
  "refreshToken": "Atzr|IwEBIJ...",
  "tokenType": "bearer",
  "expiresIn": "3600",
  "message": "刷新成功并已更新数据库"
}
```

刷新后，使用新的 `accessToken` 进行后续 API 调用。

## 多店铺管理

### 授权第二个店铺

重复授权流程，但使用不同的区域或账号：

```bash
POST /spApi/authorizeUrl
{
  "region": "EU",
  "sellerName": "欧洲店铺"
}
```

### 查看所有授权店铺

```bash
POST /spApi/authorizedStores
```

响应会包含所有已授权的店铺：

```json
{
  "stores": [
    {
      "sellerName": "我的店铺",
      "sellerId": "A1234567890",
      "region": "NA"
    },
    {
      "sellerName": "欧洲店铺",
      "sellerId": "A9876543210",
      "region": "EU"
    }
  ],
  "total": 2
}
```

### 为不同店铺获取令牌

只需指定不同的 `sellerId` 和 `region`：

```bash
POST /spApi/storeTokens
{
  "sellerId": "A9876543210",
  "region": "EU"
}
```

## 常见场景

### 场景 1: 定时任务调用 SP-API

1. 从数据库或缓存中读取 `accessToken`
2. 检查是否过期（根据上次更新时间 + expiresIn）
3. 如果过期，调用 `/spApi/refreshToken` 刷新
4. 使用新令牌调用 Amazon SP-API

### 场景 2: 多店铺数据同步

1. 调用 `/spApi/authorizedStores` 获取所有店铺
2. 遍历店铺列表
3. 为每个店铺获取令牌 (`/spApi/storeTokens`)
4. 并行调用 Amazon SP-API 获取数据

### 场景 3: 用户重新授权

如果用户在亚马逊卖家中心撤销了授权：

1. 老令牌会失效
2. 调用 SP-API 会返回 401 Unauthorized
3. 需要用户重新授权（重复获取授权链接的流程）
4. 系统会自动更新数据库中的令牌

## 故障排查

### 问题：获取授权链接失败（错误码 1003）

**可能原因**: 网络问题或白名单配置错误

**解决方法**:
1. 检查网络连接到紫鸟代理服务
2. 确认回调地址已添加到白名单
3. 查看服务日志获取详细错误信息

### 问题：授权完成但未保存（查询不到店铺）

**可能原因**: 回调参数缺失或数据库异常

**解决方法**:
1. 检查浏览器回调 URL 是否包含所有参数
2. 查看服务日志，确认回调是否被触发
3. 检查数据库连接和表结构

### 问题：刷新令牌失败（错误码 1004）

**可能原因**: refresh_token 已失效

**解决方法**:
1. refresh_token 一旦失效，无法恢复
2. 需要用户重新完成授权流程
3. 建议定期刷新令牌，避免长时间不使用导致失效

### 问题：调用 SP-API 返回 401

**可能原因**: accessToken 过期或无效

**解决方法**:
1. 调用 `/spApi/refreshToken` 刷新令牌
2. 如果刷新失败，需要重新授权
3. 使用新令牌重试 API 调用

## 最佳实践

### 1. 令牌缓存策略

```
获取令牌时：
  ↓
检查缓存是否存在且未过期
  ↓
如果是，直接使用缓存的令牌
  ↓
如果否，从数据库读取并检查过期时间
  ↓
如果即将过期（< 5分钟），先刷新
  ↓
将新令牌写入缓存
```

### 2. 错误重试机制

```
调用 SP-API
  ↓
如果返回 401
  ↓
刷新令牌
  ↓
重试 API 调用（最多1次）
  ↓
如果仍失败，返回错误
```

### 3. 批量操作优化

```
获取所有店铺列表
  ↓
批量获取所有店铺的令牌
  ↓
并行调用 SP-API（控制并发数）
  ↓
汇总结果
```

### 4. 安全建议

- ✅ 令牌仅存储在后端，不传递给前端
- ✅ 使用 HTTPS 传输令牌
- ✅ 定期检查并刷新令牌
- ✅ 记录所有授权操作日志
- ❌ 不在日志中记录完整令牌
- ❌ 不在前端 JavaScript 中存储令牌

## 下一步

- 查看 [完整接口文档](authorization-flow.md) 了解所有接口的详细说明
- 查看 [SKILL.md](../SKILL.md) 了解 skill 的完整功能
- 参考项目代码: `src/main/java/com/zixun/spapi/controller/SpApiController.java`

## 技术支持

如遇到问题，请：
1. 查看服务日志
2. 参考故障排查章节
3. 联系技术团队
