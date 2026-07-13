# 1688采购流程地图

本文档是流程地图，不是自动化脚本。Agent 可以按步骤协助用户完成采购，但不能一次性自动执行完整下单闭环。

## 总原则

1. 采购业务先查授权，再查商品和地址，再预览，再让用户确认。
2. 图搜找货使用 `linkfox-1688-search-by-image`，本 Skill 只处理采购履约。
3. 除 `authorizeUrl` 和 `authorizedStores` 外，脚本会在每个采购 endpoint 前自动检查当前用户 ACTIVE 授权。
4. 下单、支付链接、取消订单、确认收货都是独立高风险动作，各自需要单独确认。
5. 用户前面说过“继续”“可以”“按上面来”，不能作为后续高风险动作的确认。

## 1. 授权检查

运行：

```powershell
$env:PAYLOAD = "{}"
python scripts/authorized_stores.py --payload-env PAYLOAD --inline
```

判断：

- 有 `status=ACTIVE` 且 `expired=false`：可以继续采购流程。
- 没有 ACTIVE 授权：进入授权步骤。
- 浏览器最后跳到 MyERP 登录页不等于授权失败；以 `authorized_stores.py` 返回为准。

`authorizedStores` 应只返回当前 LinkFox API key 对应用户的授权店铺。不要把它理解为后台全库账号列表。

## 2. 发起授权

运行 `authorize_url.py` 获取 1688 授权链接，并让用户在浏览器打开。

用户完成授权后，再运行 `authorized_stores.py` 验证是否出现 ACTIVE 账号。

不要让用户提供 1688 token、refresh token 或 callback code。授权 token 保存由 MyERP/ecom-plat 后端闭环完成。

## 3. 找货与 SKU

如果用户按图片找货：

1. 切换到 `linkfox-1688-search-by-image`。
2. 从图搜结果中选择目标 `offerId`。
3. 回到本 Skill，用 `sku.py` 查询 SKU/规格。

如果用户已提供 `offerId`：

1. 直接运行 `sku.py`。
2. 展示 SKU、规格、价格、起订量、库存等关键字段。
3. 让用户选择明确的 SKU 和数量。

## 4. 收货地址

运行 `receive_address_list.py` 查询当前用户可用的 1688 收货地址。

展示地址时应包含：

- 收货人
- 手机/电话（如返回）
- 省市区与详细地址
- `addressId` 或等价标识

不要猜测默认地址。多地址时让用户明确选择。

## 5. 下单预览

运行 `order_preview.py` 前确认已具备：

- `offerId`
- SKU/规格
- 数量
- 收货地址
- schema 要求的其他交易字段

预览结果必须先展示给用户：

- 商品/offerId
- SKU/规格
- 数量
- 单价与商品总价
- 运费
- 收货地址
- 订单总额
- 任何异常、库存或价格变化提示

预览失败时停止，不要进入创建订单。

## 6. 创建订单

创建订单是高风险动作。必须先询问用户是否确认创建该订单，并复述预览摘要。用户只需要中文自然语言确认，例如“确认创建这个订单”；不要要求用户输入 `confirmCreateOrder=true`。

只有用户针对本次订单明确确认后，Agent 才在脚本 payload 中自动加入：

```json
{
  "...": "order payload",
  "confirmCreateOrder": true
}
```

`create_order.py` 会拒绝缺少 `confirmCreateOrder=true` 的请求。

## 7. 获取支付链接

获取支付链接也是独立高风险动作。创建订单成功不等于用户同意获取支付链接。用户只需要中文自然语言确认，例如“确认获取支付链接”；不要要求用户输入 `confirmGetPaymentUrl=true`。

用户单独确认后，Agent 在脚本 payload 中自动加入：

```json
{
  "orderId": "...",
  "confirmGetPaymentUrl": true
}
```

## 8. 订单状态与物流

查询类动作可在用户请求时执行：

- `order_status.py`
- `logistics.py`
- `logistics_trace.py`

这些仍然会消耗积分。不要在没有用户要求的情况下连续轮询。

## 9. 取消订单

取消订单是高风险动作。执行前展示：

- `orderId`
- 当前订单状态
- 取消原因
- 可能的履约或退款影响（如响应中可判断）

只有用户针对该订单明确确认取消后，Agent 才运行 `cancel_order.py`，并在脚本 payload 中自动加入：

```json
{
  "orderId": "...",
  "confirmCancel": true
}
```

## 10. 确认收货

确认收货是高风险动作。用户查询物流、看到已签收、或问“状态怎么样”，都不等于确认收货。

只有用户明确确认收货后，Agent 才运行 `confirm_receive.py`，并在脚本 payload 中自动加入：

```json
{
  "orderId": "...",
  "confirmReceive": true
}
```

## MCP 与 Skill 分离

MCP 停用只表示该工具不再通过 MCP 工具列表暴露。只要 tool-gateway 对应 HTTP route 仍启用，本 Skill 的脚本仍可通过 HTTP 调用。

如果需要彻底禁用某个采购能力，需要关闭对应 gateway route 或后端能力，而不是只从 MCP 列表移除。
