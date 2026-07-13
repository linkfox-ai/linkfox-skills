---
name: linkfox-temu-returns-refunds-eu
description: Temu 欧洲站电商退货与退款 API，经 LinkFox 网关转发 Partner EU Returns & Refunds / 售后退货退款 相关 bg/temu 接口（退货申请、退款、售后单查询与处理等，接口将按 Partner 文档逐条接入）。当用户提到 Temu EU 退货、退款、售后退货、return、refund、aftersales return、parentAfterSalesSn、退货单、退款单、order-shipping 售后 时触发。取消订单用 linkfox-temu-cancel-order-eu；订单用 linkfox-temu-order-eu。
---

# Temu 欧洲站 — 退货与退款（Returns & Refunds）

本 skill（`linkfox-temu-returns-refunds-eu`）覆盖 Partner Platform for EU **Returns & Refunds / 电商退货与退款**（及关联 **After-sales** 退货退款类）相关 `bg.*` / `temu.*` 接口（`menu_code` 与各 `sub_menu_code` 以 Partner 后台为准，见 [partner-eu-catalog.md](./references/partner-eu-catalog.md)）。

已接入 **9** 条 Partner **Return and Refund** 接口，清单见 [partner-eu-catalog.md](./references/partner-eu-catalog.md)。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 退货退款 OpenAPI（`eu_returns_refunds_*`、`temu_eu_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| **退货与退款**（本 skill） | **`linkfox-temu-returns-refunds-eu`** |
| 买家发起**取消订单**（非退货退款全流程） | `linkfox-temu-cancel-order-eu` |
| 卖家发起**取消订单** / 缺货取消 / 申诉 | `linkfox-temu-cancel-order-eu` |
| 订单列表/详情/金额/售后上下文 | `linkfox-temu-order-eu` |
| 商品管理 | `linkfox-temu-manage-product-eu` |
| 履约/发货 | `linkfox-temu-fulfillment-eu` |
| 网关与 Temu token | 本 skill `scripts/` |

## 调用方式

- **API 端点**：`POST /temu/proxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-returns-refunds-eu-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

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
| site | `eu` | Partner EU |
| managementType | `semi-managed` | 半托管（具体接口以 Partner 文档为准） |
| tokenPurpose | `order-shipping` | 订单/售后场景 token（见 [access-token.md](./references/access-token.md)） |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（`storeKey` 时建议带 `tokenPurpose=order-shipping`）

## Scripts

| 脚本 | 说明 |
|------|------|
| `temu_eu_proxy.py` | 任意 `type` 通用转发 |
| `temu_eu_file_download.py` | 加签文件下载 |
| `eu_returns_refunds_aftersales_parentaftersales_list_get.py` | `bg.aftersales.parentaftersales.list.get` |
| `eu_returns_refunds_aftersales_aftersales_list_get.py` | `bg.aftersales.aftersales.list.get` |
| `eu_returns_refunds_aftersales_parentaftersales_detail_get.py` | `temu.aftersales.parentaftersales.detail.get` |
| `eu_returns_refunds_aftersales_parentreturnorder_get.py` | `bg.aftersales.parentreturnorder.get` |
| `eu_returns_refunds_aftersales_returnaddress_get.py` | `temu.aftersales.returnaddress.get` |
| `eu_returns_refunds_aftersales_returnlabel_prepare_get.py` | `temu.aftersales.returnlabel.prepare.get` |
| `eu_returns_refunds_aftersales_signature_get.py` | `temu.aftersales.signature.get` |
| `eu_returns_refunds_aftersales_upload_returnlabel.py` | `temu.aftersales.upload.returnlabel` |
| `eu_returns_refunds_aftersales_carrier_get.py` | `temu.aftersales.carrier.get` |

## 接入更多接口（约定）

你每提供一条 Partner 文档（`type` + `sub_menu_code` + URL + Request/Response 参数表），将：

1. 新增 `references/apis/<type-slug>.md`（完整入参/出参层级）
2. 新增 `scripts/eu_returns_refunds_<slug>.py`（调用 `_eu_returns_refunds_script.run_cli`）
3. 更新 [partner-eu-catalog.md](./references/partner-eu-catalog.md)、[apis/README.md](./references/apis/README.md) 与本表

## 示例（通用代理）

```bash
export LINKFOXAGENT_API_KEY="<key>"

python scripts/temu_eu_proxy.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "type": "<TEMU_API_TYPE>",
  "params": {
    "request": {}
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-returns-refunds-eu`

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
