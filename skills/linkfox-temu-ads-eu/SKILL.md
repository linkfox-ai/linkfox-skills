---
name: linkfox-temu-ads-eu
description: Temu 欧洲站电商广告 Ads API，经 LinkFox 网关转发 Partner EU Ads / 广告投放 相关 bg/temu 接口（广告计划、广告组、创意、报表、预算出价等，接口将按 Partner 文档逐条接入）。当用户提到 Temu EU 广告、Ads、广告投放、广告计划、广告组、创意、出价、预算、广告报表、ad campaign、product-inventory 广告 时触发。商品管理用 linkfox-temu-manage-product-eu；促销用 linkfox-temu-promotion-eu；订单用 linkfox-temu-order-eu。
---

# Temu 欧洲站 — 电商广告（Ads）

本 skill（`linkfox-temu-ads-eu`）覆盖 Partner Platform for EU **Ads / 电商广告**（广告计划、投放、报表等；`menu_code` 与各 `sub_menu_code` 以 Partner 后台为准，见 [partner-eu-catalog.md](./references/partner-eu-catalog.md)）。

已接入 **7** 条 Partner **Ads**（`temu.searchrec.ad.*`）接口，清单见 [partner-eu-catalog.md](./references/partner-eu-catalog.md)。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 广告 OpenAPI（`eu_ads_*`、`temu_eu_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| **广告 Ads**（本 skill） | **`linkfox-temu-ads-eu`** |
| 商品列表/详情/编辑/库存/上下架 | `linkfox-temu-manage-product-eu` |
| 促销/营销活动 | `linkfox-temu-promotion-eu` |
| 发品 | `linkfox-temu-add-product-eu` |
| 价格/供货价、定价单 | `linkfox-temu-price-eu` |
| 订单列表/详情 | `linkfox-temu-order-eu` |
| 退货与退款 | `linkfox-temu-returns-refunds-eu` |
| 网关与 Temu token | 本 skill `scripts/` |

## API Usage

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、错误码、接入约定 |
| [partner-eu-catalog.md](./references/partner-eu-catalog.md) | 接口目录 + Partner URL + 脚本（随接入更新） |
| [apis/README.md](./references/apis/README.md) | **按接口分文件**（`apis/<type-slug>.md`） |

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `eu` | Partner EU |
| managementType | `semi-managed` | 半托管（具体接口以 Partner 文档为准） |
| tokenPurpose | `product-inventory` | 卖家助手默认（若 Partner 某 Ads 接口要求其他 `tokenPurpose`，以该接口文档为准） |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（`storeKey` 时建议带 `tokenPurpose=product-inventory`）

## Scripts

| 脚本 | 说明 |
|------|------|
| `temu_eu_proxy.py` | 任意 type |
| `temu_eu_file_download.py` | 加签下载 |
| `eu_ads_searchrec_ad_roas_pred.py` | `temu.searchrec.ad.roas.pred` |
| `eu_ads_searchrec_ad_reports_mall_query.py` | `temu.searchrec.ad.reports.mall.query` |
| `eu_ads_searchrec_ad_create.py` | `temu.searchrec.ad.create` |
| `eu_ads_searchrec_ad_detail_query.py` | `temu.searchrec.ad.detail.query` |
| `eu_ads_searchrec_ad_log_query.py` | `temu.searchrec.ad.log.query` |
| `eu_ads_searchrec_ad_goods_create_query.py` | `temu.searchrec.ad.goods.create.query` |
| `eu_ads_searchrec_ad_modify.py` | `temu.searchrec.ad.modify` |

## 接入新接口（约定）

你每提供一条 Partner 文档（`type` + `sub_menu_code` + URL + Request/Response 参数表），将：

1. 新增 `references/apis/<type-slug>.md`（完整入参/出参层级）
2. 新增 `scripts/eu_ads_<slug>.py`（调用 `_eu_ads_script.run_cli`）
3. 更新 [partner-eu-catalog.md](./references/partner-eu-catalog.md)、[apis/README.md](./references/apis/README.md) 与本表

## 示例（通用代理）

```bash
export LINKFOXAGENT_API_KEY="<key>"

python scripts/temu_eu_proxy.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "product-inventory",
  "type": "<TEMU_API_TYPE>",
  "params": {
    "request": {}
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-ads-eu`

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

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `eu_ads_searchrec_ad_create.py`, `eu_ads_searchrec_ad_detail_query.py`, `eu_ads_searchrec_ad_goods_create_query.py`, `eu_ads_searchrec_ad_log_query.py`, `eu_ads_searchrec_ad_modify.py`, `eu_ads_searchrec_ad_reports_mall_query.py`, `eu_ads_searchrec_ad_roas_pred.py`, `get_temu_access_token.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_eu_file_download.py`, `temu_eu_proxy.py`, `temu_file_download.py`, `temu_proxy.py`, `temu_token_guide.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
