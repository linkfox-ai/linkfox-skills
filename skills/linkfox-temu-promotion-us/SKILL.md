---
name: linkfox-temu-promotion-us
description: Temu 美国站电商促销 API，经 LinkFox 网关转发 Partner US Promotion / 促销活动 相关 bg/temu 接口（活动创建、报名、查询、优惠券/秒杀等，接口将按 Partner 文档逐条接入）。当用户提到 Temu US 促销、促销活动、优惠券、秒杀、活动报名、promotion campaign、product-inventory 促销 时触发。商品管理用 linkfox-temu-manage-product-us；价格用 linkfox-temu-price-us；订单用 linkfox-temu-order-us。
---

# Temu 美国站 — 电商促销（Promotion）

本 skill（`linkfox-temu-promotion-us`）覆盖 Partner Platform for US **Promotion / 电商促销**（促销活动、优惠券、活动报名等；Partner 后台菜单可能显示为 Marketing/Promotion）相关 `bg.*` / `temu.*` 接口（`menu_code` 与各 `sub_menu_code` 以 Partner 后台为准，见 [partner-us-catalog.md](./references/partner-us-catalog.md)）。

已接入 **6** 条 Partner **Promotion** 接口，清单见 [partner-us-catalog.md](./references/partner-us-catalog.md)。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 促销 OpenAPI（`us_promotion_*`、`temu_us_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| **促销/营销活动**（本 skill） | **`linkfox-temu-promotion-us`** |
| 广告 Ads | `linkfox-temu-ads-us` |
| 商品列表/详情/编辑/库存/上下架 | `linkfox-temu-manage-product-us` |
| 发品 | `linkfox-temu-add-product-us` |
| 价格/供货价、定价单 | `linkfox-temu-price-us` |
| 订单列表/详情 | `linkfox-temu-order-us` |
| 退货与退款 | `linkfox-temu-returns-refunds-us` |
| 网关与 Temu token | 本 skill `scripts/` |

## 调用方式

- **API 端点**：`POST /temu/proxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-promotion-us-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `us` | Partner US |
| managementType | `semi-managed` | 半托管（具体接口以 Partner 文档为准） |
| tokenPurpose | `product-inventory` | 与商品/促销场景一致（见 [access-token.md](./references/access-token.md)） |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（`storeKey` 时建议带 `tokenPurpose=product-inventory`）

## Scripts

| 脚本 | 说明 |
|------|------|
| `temu_us_proxy.py` | 任意 type |
| `temu_us_file_download.py` | 加签下载 |
| `us_promotion_activity_query.py` | `bg.promotion.activity.query` |
| `us_promotion_activity_candidate_goods_query.py` | `bg.promotion.activity.candidate.goods.query` |
| `us_promotion_activity_goods_query.py` | `bg.promotion.activity.goods.query` |
| `us_promotion_activity_goods_enroll.py` | `bg.promotion.activity.goods.enroll` |
| `us_promotion_activity_goods_operation_query.py` | `bg.promotion.activity.goods.operation.query` |
| `us_promotion_activity_goods_update.py` | `bg.promotion.activity.goods.update` |

## 接入新接口（约定）

你每提供一条 Partner 文档（`type` + `sub_menu_code` + URL + Request/Response 参数表），将：

1. 新增 `references/apis/<type-slug>.md`（完整入参/出参层级）
2. 新增 `scripts/us_promotion_<slug>.py`（调用 `_us_promotion_script.run_cli`）
3. 更新 [partner-us-catalog.md](./references/partner-us-catalog.md)、[apis/README.md](./references/apis/README.md) 与本表

## 示例（通用代理）

```bash
export LINKFOXAGENT_API_KEY="<key>"

python scripts/temu_us_proxy.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "product-inventory",
  "type": "<TEMU_API_TYPE>",
  "params": {
    "request": {}
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-promotion-us`

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

