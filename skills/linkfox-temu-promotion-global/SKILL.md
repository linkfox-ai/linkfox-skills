---
name: linkfox-temu-promotion-global
description: Temu 全球站电商促销 API，经 LinkFox 网关转发 Partner Global Promotion / 促销活动 相关 bg/temu 接口（活动创建、报名、查询、优惠券/秒杀等，接口将按 Partner 文档逐条接入）。当用户提到 Temu Global 促销、促销活动、优惠券、秒杀、活动报名、promotion campaign、product-inventory 促销 时触发。商品管理用 linkfox-temu-manage-product-global；价格用 linkfox-temu-price-global；订单用 linkfox-temu-order-global。
---

# Temu 全球站 — 电商促销（Promotion）

本 skill（`linkfox-temu-promotion-global`）覆盖 Partner Platform for Global **Promotion / 电商促销**（促销活动、优惠券、活动报名等；Partner 后台菜单可能显示为 Marketing/Promotion）相关 `bg.*` / `temu.*` 接口（`menu_code` 与各 `sub_menu_code` 以 Partner 后台为准，见 [partner-global-catalog.md](./references/partner-global-catalog.md)）。

已接入 **6** 条 Partner **Promotion** 接口，清单见 [partner-global-catalog.md](./references/partner-global-catalog.md)。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 促销 OpenAPI（`global_promotion_*`、`temu_global_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| **促销/营销活动**（本 skill） | **`linkfox-temu-promotion-global`** |
| 广告 Ads | `linkfox-temu-ads-us` |
| 商品列表/详情/编辑/库存/上下架 | `linkfox-temu-manage-product-global` |
| 发品 | `linkfox-temu-add-product-us` |
| 价格/供货价、定价单 | `linkfox-temu-price-global` |
| 订单列表/详情 | `linkfox-temu-order-global` |
| 退货与退款 | `linkfox-temu-returns-refunds-global` |
| 网关与 Temu token | 本 skill `scripts/` |

## API Usage

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、错误码、接入约定 |
| [partner-global-catalog.md](./references/partner-global-catalog.md) | 接口目录 + Partner URL + 脚本（随接入更新） |
| [apis/README.md](./references/apis/README.md) | **按接口分文件**（`apis/<type-slug>.md`） |

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `global` | Partner Global |
| managementType | `semi-managed` | 半托管（具体接口以 Partner 文档为准） |
| tokenPurpose | `product-inventory` | 与商品/促销场景一致（见 [access-token.md](./references/access-token.md)） |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（`storeKey` 时建议带 `tokenPurpose=product-inventory`）

## Scripts

| 脚本 | 说明 |
|------|------|
| `temu_global_proxy.py` | 任意 type |
| `temu_global_file_download.py` | 加签下载 |
| `global_promotion_activity_query.py` | `bg.promotion.activity.query` |
| `global_promotion_activity_candidate_goods_query.py` | `bg.promotion.activity.candidate.goods.query` |
| `global_promotion_activity_goods_query.py` | `bg.promotion.activity.goods.query` |
| `global_promotion_activity_goods_enroll.py` | `bg.promotion.activity.goods.enroll` |
| `global_promotion_activity_goods_operation_query.py` | `bg.promotion.activity.goods.operation.query` |
| `global_promotion_activity_goods_update.py` | `bg.promotion.activity.goods.update` |

## 接入新接口（约定）

你每提供一条 Partner 文档（`type` + `sub_menu_code` + URL + Request/Response 参数表），将：

1. 新增 `references/apis/<type-slug>.md`（完整入参/出参层级）
2. 新增 `scripts/global_promotion_<slug>.py`（调用 `_global_promotion_script.run_cli`）
3. 更新 [partner-global-catalog.md](./references/partner-global-catalog.md)、[apis/README.md](./references/apis/README.md) 与本表

## 示例（通用代理）

```bash
export LINKFOXAGENT_API_KEY="<key>"

python scripts/temu_global_proxy.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "product-inventory",
  "type": "<TEMU_API_TYPE>",
  "params": {
    "request": {}
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-promotion-global`

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

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `get_temu_access_token.py`, `global_promotion_activity_candidate_goods_query.py`, `global_promotion_activity_goods_enroll.py`, `global_promotion_activity_goods_operation_query.py`, `global_promotion_activity_goods_query.py`, `global_promotion_activity_goods_update.py`, `global_promotion_activity_query.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_file_download.py`, `temu_global_file_download.py`, `temu_global_proxy.py`, `temu_proxy.py`, `temu_token_guide.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
