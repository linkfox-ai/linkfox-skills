---
name: linkfox-temu-manage-product-us
description: Temu 美国站商品管理（Manage Product）API，经 LinkFox 网关转发 Partner US 24 个 bg.local/temu.local 接口：商品列表/详情/SKU查询、部分/全量编辑、删除、库存、上下架、预售、类目预检、属性模板、合规、外部编码、视频封面等。当用户提到 Temu US Manage Product、bg.local.goods、商品上下架、改库存、删除商品、合规编辑、Partner US 商品管理文档 时触发。发品用 linkfox-temu-add-product-us；**价格/供货价**用 **linkfox-temu-price-us**；**促销/营销活动**用 **linkfox-temu-promotion-us**；**广告 Ads**用 **linkfox-temu-ads-us**；**订单**用 **linkfox-temu-order-us**；**Self-Fulfilled Shipments**用 **linkfox-temu-fulfillment-us**；**买家取消**用 **linkfox-temu-cancel-order-us**；**卖家取消**用 **linkfox-temu-cancel-order-us**。
---

# Temu 美国站商品管理 API（Manage Product）

本 skill（`linkfox-temu-manage-product-us`）覆盖 Partner Platform for US **Product > Manage Product**（`menu_code=fb16b05f7a904765aac4af3a24b87d4a`）下 **24** 个 `bg.local.*` / `temu.local.*` 接口。欧洲站请用 **`linkfox-temu-manage-product-eu`**；全球站（非 US/EU）请用 **`linkfox-temu-manage-product-global`**。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 商品 OpenAPI（`us_manage_*`、`temu_us_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

> **发品**（V2 add、类目映射等）请用 **`linkfox-temu-add-product-us`**。**价格/供货价**（`priceorder.query`、`recommendedprice.query` 等）请用 **`linkfox-temu-price-us`**。**促销/营销活动**请用 **`linkfox-temu-promotion-us`**（`bg.promotion.*`）。**广告 Ads**请用 **`linkfox-temu-ads-us`**。**订单**请用 **`linkfox-temu-order-us`**。**履约/发货**请用 **`linkfox-temu-fulfillment-us`**。**取消订单**请用 **`linkfox-temu-cancel-order-us`**。

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


入参/出参、**Partner 官方文档 URL** 已内联至 `references/`：

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、错误码 |
| [partner-us-catalog.md](./references/partner-us-catalog.md) | 24 接口目录 + 脚本 + 文档链接 |
| [apis/README.md](./references/apis/README.md) | **按接口分文件**（24 个 `apis/*.md`） |

常用单接口文档示例：

- 部分编辑：[apis/bg-local-goods-partial-update.md](./references/apis/bg-local-goods-partial-update.md)
- 商品列表：[apis/bg-local-goods-list-query.md](./references/apis/bg-local-goods-list-query.md)
- 库存编辑：[apis/bg-local-goods-stock-edit.md](./references/apis/bg-local-goods-stock-edit.md)

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `us` | Partner US |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `product-inventory` | 酷鸟卖家助手 token |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`

## Scripts（按 type）

| 脚本 | type |
|------|------|
| `us_manage_list_query.py` | `bg.local.goods.list.query` |
| `us_manage_goods_list_retrieve.py` | `temu.local.goods.list.retrieve` |
| `us_manage_detail_query.py` | `bg.local.goods.detail.query` |
| `us_manage_sku_list_query.py` | `bg.local.goods.sku.list.query` |
| `us_manage_sku_list_retrieve.py` | `temu.local.sku.list.retrieve` |
| `us_manage_publish_status_get.py` | `bg.local.goods.publish.status.get` |
| `us_manage_sku_stock_query.py` | `temu.local.goods.sku.stock.query` |
| `us_manage_stock_edit.py` | `bg.local.goods.stock.edit` |
| `us_manage_partial_update.py` | `bg.local.goods.partial.update` |
| `us_manage_goods_update.py` | `bg.local.goods.update` |
| `us_manage_goods_delete.py` | `temu.local.goods.delete` |
| `us_manage_spec_info_get.py` | `temu.local.goods.spec.info.get` |
| `us_manage_category_check.py` | `bg.local.goods.category.check` |
| `us_manage_property_get.py` | `bg.local.goods.property.get` |
| `us_manage_property_relations.py` | `bg.local.goods.property.relations` |
| `us_manage_property_relations_level_template.py` | `bg.local.goods.property.relations.level.template` |
| `us_manage_property_relations_template.py` | `bg.local.goods.property.relations.template` |
| `us_manage_out_sn_set.py` | `bg.local.goods.out.sn.set` |
| `us_manage_sku_out_sn_set.py` | `bg.local.goods.sku.out.sn.set` |
| `us_manage_compliance_list_query.py` | `bg.local.compliance.goods.list.query` |
| `us_manage_compliance_edit.py` | `bg.local.goods.compliance.edit` |
| `us_manage_sale_status_set.py` | `bg.local.goods.sale.status.set` |
| `us_manage_pre_sale_status_edit.py` | `temu.local.goods.pre.sale.status.edit` |
| `us_manage_videocoverimage_get.py` | `bg.local.goods.videocoverimage.get` |
| `temu_us_proxy.py` | 任意 `type` |
| `temu_us_file_download.py` | 加签文件下载 |

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 商品列表
python scripts/us_manage_list_query.py '{"accessToken":"TOKEN","request":{"pageNo":1,"pageSize":20,"goodsSearchType":1,"goodsStatusFilterType":0}}'

# 详情
python scripts/us_manage_detail_query.py '{"accessToken":"TOKEN","request":{"goodsId":123456,"versionQueryType":2}}'

# 部分编辑标题（官方字段为 goodsBasic.goodsName，非 productName）
python scripts/us_manage_partial_update.py '{"accessToken":"TOKEN","request":{"goodsId":123456,"goodsBasic":{"goodsName":"New Title"}}}'

# 库存增量
python scripts/us_manage_stock_edit.py '{"accessToken":"TOKEN","request":{"goodsId":123456,"skuStockChangeList":[{"skuId":999,"stockDiff":10}]}}'
```

**Feedback：** `skillName`：`linkfox-temu-manage-product-us`

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

