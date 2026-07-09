---
name: linkfox-temu-price-eu
description: Temu 欧洲站商品价格管理 API，经 LinkFox 网关转发 Partner EU 价格接口：定价单列表查询(bg.local.goods.priceorder.query)、批量改 SKU 基础价(bg.local.goods.priceorder.change.sku.price)、推荐供货价/基础价估算等。当用户提到 Temu EU 价格、Temu欧洲站定价单、priceorder query、priceAuditList、改供货价、批量改价、site=eu 改价、recommendedprice query、baseprice recommend 时触发。商品管理用 linkfox-temu-manage-product-eu；订单/发品等其它域可用 US skill 并设 site=eu。
---

# Temu 欧洲站价格 API（linkfox-temu-price-eu）

美国站请用 **`linkfox-temu-price-us`**；全球站（非 US/EU）请用 **`linkfox-temu-price-global`**。

本 skill（`linkfox-temu-price-eu`）覆盖 Partner Platform for EU **Price** 菜单（`menu_code=dfff38c23adf498d8a7cd55052bd3648`）下与**价格/供货价**相关的 `bg.local.*` / `temu.local.*` 接口（`type` 与 US 版对齐，默认 `site=eu`）。

> 当前已接入 **4** 个接口；其余价格接口将按 Partner 文档逐条补充到 `references/apis/` 与 `eu_price_*.py`。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 价格 OpenAPI（`eu_price_*`、`temu_eu_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| 商品列表/详情/编辑/库存/上下架 | `linkfox-temu-manage-product-eu` |
| 订单查询、发货、物流 | `linkfox-temu-order-us` |
| 取消订单（买家+卖家） | `linkfox-temu-cancel-order-us` |

| 履约/发货（含自发货） | `linkfox-temu-fulfillment-eu` |
| 发品、类目、V2 add | `linkfox-temu-add-product-us` |
| 半托管 `temu.goods.price.list.get`（`productSkuIds`） | `linkfox-temu-add-product-us` → `us_goods_price_list.py` |
| 网关与 Temu token | 本 skill `scripts/` |

## 调用方式

- **API 端点**：`POST /temu/proxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `eu` | Partner EU |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `product-inventory` | 酷鸟卖家助手 token |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`

## Scripts（按 type）

| 脚本 | type | 状态 |
|------|------|------|
| `eu_price_baseprice_recommend.py` | `temu.local.goods.baseprice.recommend` | 已接入 |
| `eu_price_recommendedprice_query.py` | `temu.local.goods.recommendedprice.query` | 已接入 |
| `eu_price_priceorder_query.py` | `bg.local.goods.priceorder.query` | 已接入 |
| `eu_price_priceorder_change_sku_price.py` | `bg.local.goods.priceorder.change.sku.price` | 已接入 |
| `temu_eu_proxy.py` | 任意 `type` | 通用 |
| `temu_eu_file_download.py` | 加签文件下载 | 通用 |

> 新增接口后在此表与 [partner-eu-catalog.md](./references/partner-eu-catalog.md) 同步登记。

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 推荐基础价/供货价估算（须 catId + supplierPriceEstimateSkuQryList）
python scripts/eu_price_baseprice_recommend.py '{
  "accessToken": "TOKEN",
  "request": {
    "supplierPriceEstimateQry": {
      "goodsBasicInfo": { "catId": 12345 },
      "supplierPriceEstimateSkuQryList": [
        {
          "specIdList": [9001],
          "externPlatformPriceInfo": { "amount": "19.99", "currency": "EUR" }
        }
      ]
    }
  }
}'

# 推荐供货价查询（须 recommendedPriceType + goodsIdList，1～100 个 goodsId）
python scripts/eu_price_recommendedprice_query.py '{
  "accessToken": "TOKEN",
  "request": {
    "recommendedPriceType": 10,
    "goodsIdList": [123456789]
  }
}'

# 定价单列表查询（白名单；分页 page/size，可选筛选）
python scripts/eu_price_priceorder_query.py '{
  "accessToken": "TOKEN",
  "request": {
    "page": 1,
    "size": 20,
    "priceOrderType": 1,
    "orderBy": "order_create_time",
    "orderByType": 0
  }
}'

# 批量修改 SKU 基础价（白名单；须 goodsId + changeSkuPriceDTOList）
python scripts/eu_price_priceorder_change_sku_price.py '{
  "accessToken": "TOKEN",
  "request": {
    "goodsId": 123456,
    "changeSkuPriceDTOList": [
      {
        "skuChangePriceBaseDTOList": [
          {
            "skuId": 58224724203874,
            "newSupplierPrice": { "amount": "15.99", "currency": "EUR" }
          }
        ]
      }
    ]
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-price-eu`

## 网关与授权脚本

| 脚本 | 说明 |
|------|------|
| `check_linkfox_token.py` | 校验 LinkFox 用户 Token |
| `temu_token_guide.py` | Temu accessToken 后台授权步骤 |
| `save_temu_access_token.py` | 保存 accessToken 到本地 |
| `list_temu_access_tokens.py` | 列出已保存 token |
| `get_temu_access_token.py` | 读取已保存 token |
| `temu_proxy.py` | 通用网关转发（多 site） |
| `temu_file_download.py` | 加签文件下载（多 site） |

授权说明：[references/access-token.md](./references/access-token.md)

