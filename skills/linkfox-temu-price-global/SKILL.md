---
name: linkfox-temu-price-global
description: Temu 全球站（非 US/EU）价格/供货价 API，经 LinkFox 网关转发 5 个接口（定价单、推荐价、SKU 供货价列表、批量改价等），默认 site=global。当用户提到 Temu Global 价格、全球站定价单、priceorder query、sku list price、查 SKU 供货价、改供货价、recommendedprice、baseprice recommend 时触发。美国站用 linkfox-temu-price-us；欧洲站用 linkfox-temu-price-eu；商品管理用 linkfox-temu-manage-product-global。
---

# Temu 全球站价格 API（linkfox-temu-price-global）

本 skill（`linkfox-temu-price-global`）覆盖 **全球区（`site=global`，非美国/欧洲）** 的 **Product** 菜单下与**价格/供货价**相关的 `bg.local.*` / `temu.local.*` 接口（`menu_code=fb16b05f7a904765aac4af3a24b87d4a`，具体 `sub_menu_code` 以 Partner 文档为准）。

> 当前已接入 **5** 个接口；其余价格接口将按 Partner 文档逐条补充到 `references/apis/` 与 `global_price_*.py`。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 价格 OpenAPI（`global_price_*`、`temu_global_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| 商品列表/详情/编辑/库存/上下架 | `linkfox-temu-manage-product-global` |
| 美国站价格 | `linkfox-temu-price-us` |
| 欧洲站价格 | `linkfox-temu-price-eu` |
| 订单查询、发货、物流 | `linkfox-temu-order-global` |
| 取消订单（买家+卖家） | `linkfox-temu-cancel-order-us` |

| 履约/发货（含自发货） | `linkfox-temu-fulfillment-us` |
| 发品、类目、V2 add | `linkfox-temu-add-product-us` |
| 半托管 `temu.goods.price.list.get`（`productSkuIds`） | `linkfox-temu-add-product-us` → `us_goods_price_list.py` |
| 网关与 Temu token | 本 skill `scripts/` |

## API Usage

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、错误码、典型流程 |
| [partner-global-catalog.md](./references/partner-global-catalog.md) | 接口目录 + Partner URL + 脚本 |
| [apis/README.md](./references/apis/README.md) | **按接口分文件**（`apis/<type-slug>.md`） |

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `global` | Partner Global（非 US/EU） |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `product-inventory` | 酷鸟卖家助手 token |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`

## Scripts（按 type）

| 脚本 | type | 状态 |
|------|------|------|
| `global_price_baseprice_recommend.py` | `temu.local.goods.baseprice.recommend` | 已接入 |
| `global_price_recommendedprice_query.py` | `temu.local.goods.recommendedprice.query` | 已接入 |
| `global_price_priceorder_query.py` | `bg.local.goods.priceorder.query` | 已接入 |
| `global_price_priceorder_change_sku_price.py` | `bg.local.goods.priceorder.change.sku.price` | 已接入 |
| `global_price_sku_list_price_query.py` | `bg.local.goods.sku.list.price.query` | 已接入 |
| `temu_global_proxy.py` | 任意 `type` | 通用 |
| `temu_global_file_download.py` | 加签文件下载 | 通用 |

> 新增接口后在此表与 [partner-global-catalog.md](./references/partner-global-catalog.md) 同步登记。

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 推荐基础价/供货价估算（须 catId + supplierPriceEstimateSkuQryList）
python scripts/global_price_baseprice_recommend.py '{
  "accessToken": "TOKEN",
  "site": "global",
  "tokenPurpose": "product-inventory",
  "request": {
    "supplierPriceEstimateQry": {
      "goodsBasicInfo": { "catId": 12345 },
      "supplierPriceEstimateSkuQryList": [
        {
          "specIdList": [9001],
          "externPlatformPriceInfo": { "amount": "19.99", "currency": "USD" }
        }
      ]
    }
  }
}'

# 推荐供货价查询（须 recommendedPriceType + goodsIdList，1～100 个 goodsId）
python scripts/global_price_recommendedprice_query.py '{
  "accessToken": "TOKEN",
  "site": "global",
  "tokenPurpose": "product-inventory",
  "request": {
    "recommendedPriceType": 10,
    "goodsIdList": [123456789]
  }
}'

# 定价单列表查询（白名单；分页 page/size，可选筛选）
python scripts/global_price_priceorder_query.py '{
  "accessToken": "TOKEN",
  "site": "global",
  "tokenPurpose": "product-inventory",
  "request": {
    "page": 1,
    "size": 20,
    "priceOrderType": 1,
    "orderBy": "order_create_time",
    "orderByType": 0
  }
}'

# 批量修改 SKU 基础价（白名单；须 goodsId + changeSkuPriceDTOList）
python scripts/global_price_priceorder_change_sku_price.py '{
  "accessToken": "TOKEN",
  "site": "global",
  "tokenPurpose": "product-inventory",
  "request": {
    "goodsId": 123456,
    "changeSkuPriceDTOList": [
      {
        "skuChangePriceBaseDTOList": [
          {
            "skuId": 58224724203874,
            "newSupplierPrice": { "amount": "15.99", "currency": "USD" }
          }
        ]
      }
    ]
  }
}'

# SKU 供货价列表（goodsId + skuIdList）
python scripts/global_price_sku_list_price_query.py '{
  "accessToken": "TOKEN",
  "site": "global",
  "tokenPurpose": "product-inventory",
  "request": {
    "querySupplierPriceBaseList": [
      { "goodsId": 123456789, "skuIdList": [58224724203874] }
    ]
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-price-global`

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

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/check_linkfox_token.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `get_temu_access_token.py`, `global_price_baseprice_recommend.py`, `global_price_priceorder_change_sku_price.py`, `global_price_priceorder_query.py`, `global_price_recommendedprice_query.py`, `global_price_sku_list_price_query.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_file_download.py`, `temu_global_file_download.py`, `temu_global_proxy.py`, `temu_proxy.py`, `temu_token_guide.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
