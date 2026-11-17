# Amazon Store 授权快速开始指南

本指南帮助你快速上手使用亚马逊店铺授权功能。

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

## 使用授权状态

### 查询授权状态

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
  "authRecordId": 123,
  "status": "ACTIVE",
  "tokenExpiresAt": 3600,
  "message": "授权信息已后台化管理，token 不再经由 Agent 返回"
}
```

### 调用卖家开放接口

下游业务不要读取 raw token。直接调用 `/spApi/developerProxy`，并传入同一个 `sellerId` + `region`：

```bash
POST /spApi/developerProxy
{
  "sellerId": "A1234567890",
  "region": "NA",
  "path": "orders/v0/orders",
  "method": "GET"
}
```

## 令牌管理

### 令牌过期时间

- **accessToken**: 通常 1 小时（3600秒）
- **refreshToken**: 长期有效，用于刷新 accessToken

### 检查令牌是否即将过期

从 `/spApi/storeTokens` 响应中查看 `status` / `tokenExpiresAt` / `message`：
- `ACTIVE`：可继续通过 `developerProxy` 调用
- `EXPIRED` 或调用返回 token 失效：调用 `/spApi/refreshToken` 刷新
- 当前用户连接已解绑时，需重新授权后才能使用该连接；解绑接口不将共享授权标记为 REVOKED

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
  "success": true,
  "message": "刷新成功并已更新数据库，token 已后台化管理"
}
```

刷新后，继续通过 `/spApi/developerProxy` 传 `sellerId` + `region` 调用业务接口。

### 本地取消/解绑授权

按 [SKILL.md 场景 5](../SKILL.md#scenario-5-cancel-local-authorization) 确定目标与范围后执行；参数及示例见 [API §5](api.md#5-cancel-authorization)。

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

### 场景 1: 定时任务调用卖家开放接口

1. 任务保存或接收 `sellerId` + `region`
2. 通过 `/spApi/developerProxy` 调用卖家开放接口
3. 如返回 token 失效，调用 `/spApi/refreshToken` 刷新
4. 使用相同 `sellerId` + `region` 重试一次

### 场景 2: 多店铺数据同步

1. 调用 `/spApi/authorizedStores` 获取所有店铺
2. 遍历店铺列表
3. 可选调用 `/spApi/storeTokens` 确认状态
4. 用每个店铺的 `sellerId` + `region` 调 `developerProxy`

### 场景 3: 用户重新授权

如果用户在亚马逊卖家中心撤销了授权：

1. 老令牌会失效
2. 调用卖家开放接口 会返回 401 Unauthorized
3. 需要用户重新授权（重复获取授权链接的流程）
4. 系统会自动更新数据库中的令牌

### 场景 4: 用户取消本地授权

1. 先用 `/spApi/authorizedStores` 确认要解绑的店铺
2. 调用 `/spApi/cancelAuthorization`
3. 告知用户 LinkFox 已不再使用该授权；如需 Amazon 侧彻底撤销，请到 Seller Central 授权管理页手动 Disable authorization

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

### 问题：调用卖家开放接口 返回 401

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
调用卖家开放接口
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
并行调用卖家开放接口（控制并发数）
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
- 参考后端工程中店铺网关相关 Controller 实现（包名与类名以你们仓库为准）

## 技术支持

如遇到问题，请：
1. 查看服务日志
2. 参考故障排查章节
3. 联系技术团队
