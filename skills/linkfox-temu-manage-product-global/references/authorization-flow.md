# Temu 授权流程

下表说明通用后台授权来源和店铺类型，不据此更改全球区商品任务的目标区域。Global 包装的默认值与令牌精确匹配要求见 [运行约定](api.md#运行约定)；商品库存与订单发货令牌分别授权和保存。

```text
用户确认店铺类型与用途
        ↓
temu_token_guide.py（输出后台操作步骤）
        ↓
用户在 Temu 卖家后台复制 access_token
        ↓
save_temu_access_token.py（可选，写入本地 store）
        ↓
temu_proxy.py / temu_file_download.py
  - 直接传 accessToken，或
  - 传 storeKey + site + managementType + tokenPurpose
```

## 决策表

| 用户需求 | shopType | tokenPurpose | site |
|----------|----------|--------------|------|
| 半托管查商品/库存 | semi-managed | product-inventory | cn / partner |
| 半托管查订单/发货 | semi-managed | order-shipping | us / global / eu |
| 全托管任意接口 | full-managed | full-managed | cn / partner |
| 美欧本土店 | local-native | local-native | us 等 |

## 与 API 调用的对应关系

紫鸟转发路径：`/temu-proxy/{site}/{managementType}`

- 全托管 CN：`cn` + `full-managed`
- 半托管商品：`cn`/`partner` + `semi-managed` + 商品 token
- 半托管订单：`us`/`global`/`eu` + `semi-managed` + 订单 token

授权应用名称必须与后台一致：**酷鸟卖家助手** 或 **Cyber-ERP酷鸟助手** / **Cyber-ERP**。
