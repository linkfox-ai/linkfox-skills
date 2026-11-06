# Amazon 店铺授权流程与服务端背景

五个客户端接口的完整定义统一见 [接口说明](api.md)。本文件说明服务端内部回调、数据模型、站点映射与故障定位信息；不指导 Agent 调用内部接口或直接访问数据库。

## 授权与令牌处理

1. 获取授权链接：按流程准备区域与店铺名；服务端保存带当前成员、区域和店铺名的授权申请，以随机申请标识作 state，并根据 gateway.url 生成 tokenCallback 与 redirect 地址后请求紫鸟授权代理。客户端不手工组装 state 或回调地址。
2. 用户在安全环境完成 Amazon 同意，服务端处理回调；同一 sellingPartnerId + region 更新已有记录，否则新增，并维护成员绑定。
3. 查询店铺：服务端按 gatewayUserId 获取 sp_api_bind_user 关联 amazonAuthId，去重并按 sellerId、region 排序。
4. 刷新令牌：检查授权属于当前成员，通过紫鸟换取并保存最新令牌；状态查询只读本地记录，不执行刷新。
5. 下游只接收 sellerId + region，经 developerProxy 使用后台令牌；服务端识别到上游令牌过期或失效响应后刷新并重试一次。这里不提供下游业务操作。
6. 本地解绑只删除当前成员连接，详见 [本地解绑接口](api.md#接口本地解绑cancelauthorization) 与 [入口流程](../SKILL.md#授权与店铺管理流程)。

## 授权回调处理（服务端内部）

### 系统处理路径

- 服务端在生成链接时保存授权申请，用户身份、区域与店铺名来自该申请；state 用于关联申请，不承载客户端拼接的用户信息。
- `/spApi/oauth/tokenCallback` 接收紫鸟服务端令牌推送，网关还兼容 GET 回调；服务端按申请标识补全成员上下文，保存授权与绑定，成功后核销申请。
- `/spApi/oauth/redirect` 处理浏览器授权结果并跳转成功或失败页；该跳转与令牌入库是不同处理路径，看到成功页后仍须按自动授权规则核验对应卖家与区域。
- 网关另保留 `/spApi/oauth/callback` 浏览器兼容路径和 `auth=false` 的 `/spApi/authorizeCallback` 系统路由。以上均由系统调用，Agent 不手工提交回调、令牌或用户身份参数。

### 返回结果 (SpApiAuthorizeCallbackVo)

```json
{
  "saved": true,
  "authRecordId": 123,
  "bindUserId": 456,
  "message": "已新增授权"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| saved | Boolean | 是否保存成功 |
| authRecordId | Long | 授权记录ID（sp_api_amazon_auth 表） |
| bindUserId | Long | 绑定记录ID（sp_api_bind_user 表） |
| message | String | 处理结果消息 |

### 业务逻辑

1. 检查是否已存在同一店铺的授权（sellingPartnerId + region）
2. 如果存在，更新原有授权记录；否则新增
3. 创建或更新用户与授权的绑定关系
4. 返回保存结果

### 注意事项

- 生成链接、浏览器跳转和令牌入库分别核对；不以其中任一步单独认定本次授权成功。
- 成员上下文由服务端授权申请关联，Agent 不改写 state，也不索取或展示回调中的令牌。
- 同一店铺的授权会更新而非重复创建

---


## 区域与站点映射

### 北美 (NA)

- 加拿大: amazon.ca
- 美国: amazon.com
- 墨西哥: amazon.com.mx
- 巴西: amazon.com.br

### 欧洲 (EU)

- 爱尔兰: amazon.ie
- 西班牙: amazon.es
- 英国: amazon.co.uk
- 法国: amazon.fr
- 比利时: amazon.com.be
- 荷兰: amazon.nl
- 德国: amazon.de
- 意大利: amazon.it
- 瑞典: amazon.se
- 南非: amazon.co.za
- 波兰: amazon.pl
- 沙特阿拉伯: amazon.sa
- 埃及: amazon.eg
- 土耳其: amazon.com.tr
- 阿联酋: amazon.ae
- 印度: amazon.in

### 远东 (FE)

- 新加坡: amazon.sg
- 澳大利亚: amazon.com.au
- 日本: amazon.co.jp

> Amazon SP-API 没有独立的东南亚区域代码；东南亚目前只有新加坡站，使用 **FE**。`region` 按目标 Amazon 站点选择，与卖家所在地无关。

---

## 数据库表结构

### sp_api_amazon_auth (授权信息表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 主键 |
| region | String | 区域代码 (NA/EU/FE) |
| accessToken | String | 访问令牌 |
| refreshToken | String | 刷新令牌 |
| tokenType | String | 令牌类型 |
| expiresIn | String | 过期时间（秒） |
| sellingPartnerId | String | 卖家ID |
| sellerName | String | 卖家名称 |
| mwsAuthToken | String | MWS 授权令牌 |
| appId | String | 本次授权使用的紫鸟应用标识，由服务端用于令牌刷新 |
| createDate | Date | 创建时间 |
| createTime | Long | 创建时间戳 |
| lastUpdateDate | Date | 更新时间 |
| lastUpdateTime | Long | 更新时间戳 |

### sp_api_bind_user (用户绑定表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 主键 |
| gatewayUserId | String | 网关用户ID |
| amazonAuthId | Long | 授权记录ID（外键） |
| createDate | Date | 创建时间 |
| createTime | Long | 创建时间戳 |
| lastUpdateDate | Date | 更新时间 |
| lastUpdateTime | Long | 更新时间戳 |

---


## 故障排查

### 问题 1: 授权链接无法访问

**可能原因**:
- 网络连接问题
- 紫鸟代理服务异常
- 白名单配置错误

**解决方案**:
1. 检查网络连接
2. 确认白名单配置
3. 稍后重试或联系技术支持

### 问题 2: 回调未保存授权信息

**可能原因**:
- 授权申请标识缺失、失效，或未正确关联成员上下文
- 数据库连接异常

**解决方案**:
1. 核对本次授权申请与回调关联及服务端保存结果，不手工在 state 中补写用户信息
2. 检查数据库连接
3. 查看服务日志

### 问题 3: 刷新令牌失败

**可能原因**:
- refresh_token 已过期或失效
- 紫鸟代理服务异常

**解决方案**:
1. 如果 refresh_token 失效，需重新授权
2. 检查紫鸟服务状态
3. 确认白名单配置

### 问题 4: 查询令牌返回 1004 错误

**可能原因**:
- sellerId 或 region 错误
- 授权记录不属于当前用户

**解决方案**:
1. 调用 /spApi/authorizedStores 确认店铺信息
2. 确认 sellerId 和 region 正确
3. 如果确实未授权，需先完成授权流程

---

## 安全最佳实践

1. **令牌存储**:
   - 令牌存储在数据库中，不暴露给前端
   - 仅通过后端接口访问令牌

2. **访问控制**:
   - 五个客户端接口均需用户鉴权；系统回调按上方内部流程处理
   - 用户只能访问自己授权的店铺

3. **令牌刷新**:
   - 服务端建设建议：定期检查有效期并预刷新；当前 developerProxy 的自动刷新条件见「授权与令牌处理」。
   - 服务端令牌缓存建议：已有令牌缓存未过期时复用；未命中则读取数据库，距过期不足 5 分钟时先刷新，再更新服务端缓存。Agent 和本技能脚本不获取 raw token，也不增加客户端令牌缓存或响应缓存。

4. **日志记录**:
   - 记录所有授权操作
   - 记录令牌刷新操作
   - 不记录令牌明文内容

5. **错误处理**:
   - 不在错误消息中暴露敏感信息
   - 提供清晰的错误码和处理建议
