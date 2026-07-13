---
name: linkfox-temu-manage-product-global
description: Temu 全球站（非 US/EU）商品管理 Manage Product API，经 LinkFox 网关转发 24 个 bg.local/temu.local 接口，默认 site=global。当用户提到 Temu Global Manage Product、全球站商品、site=global 商品上下架、改库存、bg.local.goods 时触发。美国站用 linkfox-temu-manage-product-us；欧洲站用 linkfox-temu-manage-product-eu；发品/价格/促销/广告/订单等其它域用对应 skill 并设 site=global。
---

# Temu 全球站商品管理 API（Manage Product）

本 skill（`linkfox-temu-manage-product-global`）覆盖 **全球区（`site=global`，非美国/欧洲）** 的 **Product > Manage Product** 下 **24** 个 `bg.local.*` / `temu.local.*` 接口（`type` 与 US/EU 对齐）。美国站请用 **`linkfox-temu-manage-product-us`**；欧洲站请用 **`linkfox-temu-manage-product-eu`**。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 商品 OpenAPI（`global_manage_*`、`temu_global_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

> **发品**请用 **`linkfox-temu-add-product-us`**（JSON 中 **`site=global`**）。**电商合规**（资质/GPSR/实拍图/责任人）用 **`linkfox-temu-compliance-global`**；**价格/供货价**（含 SKU 列表价）用 **`linkfox-temu-price-global`**；**促销**用 **`linkfox-temu-promotion-global`**；**广告**用 **`linkfox-temu-ads-global`**；**订单**用 **`linkfox-temu-order-global`** / **`linkfox-temu-order-eu`**；**履约**用 **`linkfox-temu-fulfillment-global`** / **`linkfox-temu-fulfillment-eu`**；**取消**用 **`linkfox-temu-cancel-order-us`** / **`linkfox-temu-cancel-order-eu`**（均需 **`site=global`** 时显式传入）。

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
| [partner-global-catalog.md](./references/partner-global-catalog.md) | 24 接口目录 + 脚本 + 文档链接 |
| [apis/README.md](./references/apis/README.md) | **按接口分文件**（24 个 `apis/*.md`） |

常用单接口文档示例：

- 部分编辑：[apis/bg-local-goods-partial-update.md](./references/apis/bg-local-goods-partial-update.md)
- 商品列表：[apis/bg-local-goods-list-query.md](./references/apis/bg-local-goods-list-query.md)
- 库存编辑：[apis/bg-local-goods-stock-edit.md](./references/apis/bg-local-goods-stock-edit.md)

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `global` | Partner Global |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `product-inventory` | 酷鸟卖家助手 token |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`

## Scripts（按 type）

| 脚本 | type |
|------|------|
| `global_manage_list_query.py` | `bg.local.goods.list.query` |
| `global_manage_goods_list_retrieve.py` | `temu.local.goods.list.retrieve` |
| `global_manage_detail_query.py` | `bg.local.goods.detail.query` |
| `global_manage_sku_list_query.py` | `bg.local.goods.sku.list.query` |
| `global_manage_sku_list_retrieve.py` | `temu.local.sku.list.retrieve` |
| `global_manage_publish_status_get.py` | `bg.local.goods.publish.status.get` |
| `global_manage_sku_stock_query.py` | `temu.local.goods.sku.stock.query` |
| `global_manage_stock_edit.py` | `bg.local.goods.stock.edit` |
| `global_manage_partial_update.py` | `bg.local.goods.partial.update` |
| `global_manage_goods_update.py` | `bg.local.goods.update` |
| `global_manage_goods_delete.py` | `temu.local.goods.delete` |
| `global_manage_spec_info_get.py` | `temu.local.goods.spec.info.get` |
| `global_manage_category_check.py` | `bg.local.goods.category.check` |
| `global_manage_property_get.py` | `bg.local.goods.property.get` |
| `global_manage_property_relations.py` | `bg.local.goods.property.relations` |
| `global_manage_property_relations_level_template.py` | `bg.local.goods.property.relations.level.template` |
| `global_manage_property_relations_template.py` | `bg.local.goods.property.relations.template` |
| `global_manage_out_sn_set.py` | `bg.local.goods.out.sn.set` |
| `global_manage_sku_out_sn_set.py` | `bg.local.goods.sku.out.sn.set` |
| `global_manage_compliance_list_query.py` | `bg.local.compliance.goods.list.query` |
| `global_manage_compliance_edit.py` | `bg.local.goods.compliance.edit` |
| `global_manage_sale_status_set.py` | `bg.local.goods.sale.status.set` |
| `global_manage_pre_sale_status_edit.py` | `temu.local.goods.pre.sale.status.edit` |
| `global_manage_videocoverimage_get.py` | `bg.local.goods.videocoverimage.get` |
| `temu_global_proxy.py` | 任意 `type` |
| `temu_global_file_download.py` | 加签文件下载 |

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 商品列表
python scripts/global_manage_list_query.py '{"accessToken":"TOKEN","site":"global","tokenPurpose":"product-inventory","request":{"pageNo":1,"pageSize":20,"goodsSearchType":1,"goodsStatusFilterType":0}}'

# 详情
python scripts/global_manage_detail_query.py '{"accessToken":"TOKEN","request":{"goodsId":123456,"versionQueryType":2}}'

# 部分编辑标题（官方字段为 goodsBasic.goodsName，非 productName）
python scripts/global_manage_partial_update.py '{"accessToken":"TOKEN","request":{"goodsId":123456,"goodsBasic":{"goodsName":"New Title"}}}'

# 库存增量
python scripts/global_manage_stock_edit.py '{"accessToken":"TOKEN","request":{"goodsId":123456,"skuStockChangeList":[{"skuId":999,"stockDiff":10}]}}'
```

**Feedback：** `skillName`：`linkfox-temu-manage-product-global`

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

## 积分消耗规则

不消耗积分。
