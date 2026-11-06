---
name: linkfox-temu-price-us
description: 管理 Temu 美国站商品价格，支持定价单与报价列表查询、批量修改 SKU 基础价、查询商品推荐供货价和发品或改价前的基础价估算，并支持加签资源文件下载。适用于美国站定价单、供货价核对、推荐价查询和改价管理；不适用于欧洲站或全球站价格、商品编辑和库存、订单履约或商品发布。
---

# Temu 美国站商品价格管理

## 适用范围

### 适用

管理 Partner US 商品菜单下的价格与供货价，按用户任务查询、估算或修改已授权店铺的商品价格。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看美国站商品的定价单和报价 | 定价单列表查询。 |
| 平台建议这个商品用什么供货价 | 查询已存在商品的推荐供货价。 |
| 发品或改价前估算基础价 | 根据类目、规格、站外价及可用尺寸重量估算。 |
| 按我给出的价格批量调整 SKU | 修改基础价并核对逐项结果。 |
| 下载接口返回的加签文件 | 经加签下载能力获取资源结果。 |

### 边界

欧洲站价格使用 `linkfox-temu-price-eu`，全球站价格使用 `linkfox-temu-price-global`。
商品列表、详情、编辑、库存与上下架使用 `linkfox-temu-manage-product-us`；发品、类目和半托管供货价列表使用 `linkfox-temu-add-product-us`。
订单查询使用 `linkfox-temu-order-us`，取消订单使用 `linkfox-temu-cancel-order-us`，发货履约使用 `linkfox-temu-fulfillment-us`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 |
|---|---|---|---|
| 推荐基础价/供货价估算 | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`，Body `type=temu.local.goods.baseprice.recommend` | [references/apis/temu-local-goods-baseprice-recommend.md](references/apis/temu-local-goods-baseprice-recommend.md) | `scripts/us_price_baseprice_recommend.py` |
| 推荐供货价查询 | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`，Body `type=temu.local.goods.recommendedprice.query` | [references/apis/temu-local-goods-recommendedprice-query.md](references/apis/temu-local-goods-recommendedprice-query.md) | `scripts/us_price_recommendedprice_query.py` |
| 定价单列表查询 | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`，Body `type=bg.local.goods.priceorder.query` | [references/apis/bg-local-goods-priceorder-query.md](references/apis/bg-local-goods-priceorder-query.md) | `scripts/us_price_priceorder_query.py` |
| 批量修改 SKU 基础价 | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`，Body `type=bg.local.goods.priceorder.change.sku.price` | [references/apis/bg-local-goods-priceorder-change-sku-price.md](references/apis/bg-local-goods-priceorder-change-sku-price.md) | `scripts/us_price_priceorder_change_sku_price.py` |
| 加签文件下载 | POST `/temu/fileDownload` | [references/api.md](references/api.md) | `scripts/temu_us_file_download.py`、`scripts/temu_file_download.py` |

通用入口 `scripts/temu_us_proxy.py` 与 `scripts/temu_proxy.py` 复用代理能力，不新增已定义业务操作。

## 前置条件

先确定店铺和操作目标，准备 LinkFox 用户密钥与 Temu 店铺授权。Temu 令牌须在卖家后台手动复制，可按 [references/access-token.md](references/access-token.md) 和 [references/authorization-flow.md](references/authorization-flow.md) 获取并保存；两套认证不可混淆。
商品标识、类目和规格缺失时，先从商品管理或发品流程取得，不猜测。按需读取接口清单中的完整定义；Partner US 原始文档目录见 [references/partner-us-catalog.md](references/partner-us-catalog.md)。

## 价格管理流程

1. 从商品管理流程取得商品、类目和规格标识。
2. 按用户任务查询定价单或报价列表。
3. 查询已存在商品的平台推荐供货价；需要发品或改价前估算时，再使用基础价估算。
4. 用户要求调价时，核对店铺、商品、SKU、金额和币种，按明确范围提交。
5. 展示逐项成功、失败及原因，再查询定价单核对最终供货价与提交状态。不得用再次调价作为结果查询。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，优先读取已保存的响应。业务脚本不读取或保存响应缓存。失败或空结果时，不得自动更换筛选条件、翻页或连续试探；需要继续查询时，先明确查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-price-us-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **区分价格概念**：已存在商品的推荐供货价、发品或改价前的基础价估算、定价单中的参考价、目标价、原价和最终价分别展示。半托管发品侧供货价列表属于发品技能，不与本技能本地仓定价单混用。
- **清晰展示结果**：注明店铺、美国站、商品和 SKU，金额带币种；定价单展示当前页、总数及状态，修改结果分别列出成功 SKU、失败 SKU、失败原因和生成的定价单。
- **区分估算与结果**：推荐价和估算值供用户判断，不表示调价已生效；状态未定义时展示原始状态值，不补造含义。基础价估算未定义的返回子字段按实际数据说明，不编造响应。
- **解释空结果和错误**：保留网关原始结果和已取得数据，依接口定义判断转发与业务状态；不以 HTTP 正常就认定全部 SKU 修改成功。
- **脚本运行约定**：业务脚本接受 JSON 参数和 `--inline`，提供本地授权工具，不使用响应缓存；认证优先级、参数包装与输出规则见 [references/api.md](references/api.md#脚本运行约定)。

## 使用示例

### 查询推荐供货价

用户：看看这些美国站商品的平台推荐供货价。

确认店铺和商品后查询，按商品及 SKU 展示推荐供货价、币种与返回范围。

### 估算基础价

用户：发布前根据这些规格和站外售价估算供货价。

准备类目、规格及用户提供的价格资料，按接口定义估算，说明估算依据和返回内容。

### 批量改价并核对

用户：把这些 SKU 改成我给的价格，并核对结果。

核对目标与价格，提交修改，逐项展示成功和失败，再通过定价单查询核对，不重复提交修改。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
