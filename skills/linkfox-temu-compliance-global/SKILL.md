---
name: linkfox-temu-compliance-global
description: Temu 全球站电商合规（Compliance）API，经 LinkFox 网关转发 Partner Global 合规相关 OpenAPI（bg.compliance.*、bg.arbok.open.*、bg.flash.open.* 等，共 9 个接口）。当用户提到 Temu Global 合规、商品资质、GPSR、治理属性、实拍图、资质上传、bg.compliance.edit、arbok cert、site=global 合规 时触发。
---

# Temu 全球站 — 电商合规（Compliance）

本 skill（`linkfox-temu-compliance-global`）覆盖 Partner Platform for **Global** 的 **电商合规 / Product Compliance** 相关 OpenAPI。

已接入 **9** 个接口，清单见 [partner-global-catalog.md](./references/partner-global-catalog.md)。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 合规 OpenAPI（`global_compliance_*`、`temu_global_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| **电商合规**（本 skill） | **`linkfox-temu-compliance-global`** |
| 商品列表/详情/编辑/库存 | `linkfox-temu-manage-product-global` |
| 价格 | `linkfox-temu-price-global` |
| 促销 | `linkfox-temu-promotion-global` |
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

## API 文档

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、错误码 |
| [partner-global-catalog.md](./references/partner-global-catalog.md) | 接口目录 |
| [apis/README.md](./references/apis/README.md) | 分接口文档 |

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `global` | Partner Global |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `product-inventory` | 商品/合规场景 |

## Scripts（按 type）

| 脚本 | type | 状态 |
|------|------|------|
| `global_compliance_edit.py` | `bg.compliance.edit` | 已接入 |
| `global_compliance_metadata_get.py` | `bg.compliance.metadata.get` | 已接入 |
| `global_compliance_goods_compliancelabel_get.py` | `bg.goods.compliancelabel.get` | 已接入 |
| `global_compliance_arbok_cert_query_need_upload_items.py` | `bg.arbok.open.cert.queryNeedUploadItems` | 已接入 |
| `global_compliance_arbok_cert_upload_product_cert.py` | `bg.arbok.open.cert.uploadProductCert` | 已接入 |
| `global_compliance_flash_upload_recognize.py` | `bg.flash.open.upload.recognize` | 已接入 |
| `global_compliance_flash_upload_real_image.py` | `bg.flash.open.upload.real.image` | 已接入 |
| `global_compliance_arbok_upload_upload_file.py` | `bg.arbok.open.upload.uploadFile` | 已接入 |
| `global_compliance_arbok_product_cert_query.py` | `bg.arbok.open.product.cert.query` | 已接入 |
| `temu_global_proxy.py` | 任意 `type` | 通用 |
| `temu_global_file_download.py` | 加签文件下载 | 通用 |

## 示例

```bash
python scripts/global_compliance_edit.py '<JSON>'  # bg.compliance.edit
```

```bash
python scripts/global_compliance_metadata_get.py '<JSON>'  # bg.compliance.metadata.get
```

**Feedback：** `skillName`：`linkfox-temu-compliance-global`

## 网关与授权脚本

授权说明：[references/access-token.md](./references/access-token.md)

## 积分消耗规则

不消耗积分。
