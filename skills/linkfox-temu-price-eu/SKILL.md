---
name: linkfox-temu-price-eu
description: 管理 Temu 欧洲站商品价格，支持定价单查询、批量修改 SKU 基础价、查询推荐供货价和发品或改价前的基础价估算，并支持获取加签价格文件。适用于欧洲站供货价核对、价格调整与调价结果检查；不适用于美国站或全球站价格管理、商品库存维护、订单履约或发品侧半托管供货价列表查询。
---

# Temu 欧洲站价格管理

## 适用范围

### 适用

管理已授权 Temu 欧洲站店铺的定价单、推荐供货价及 SKU 基础价。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看欧区商品的定价单或报价 | 查询定价单和当前供货价。 |
| 低流量或限流商品的推荐价是多少 | 查询已存在商品的推荐供货价。 |
| 发品或改价前估算基础价 | 根据类目、规格、站外价格及尺寸重量估算。 |
| 按我指定的价格批量调整 SKU | 提交改价并展示逐项结果。 |
| 获取价格业务中的加签文件 | 请求加签文件下载结果。 |

### 边界

美国站使用 `linkfox-temu-price-us`，全球站使用 `linkfox-temu-price-global`；商品维护使用 `linkfox-temu-manage-product-eu`，履约使用 `linkfox-temu-fulfillment-eu`。订单使用 `linkfox-temu-order-us`，取消订单使用 `linkfox-temu-cancel-order-us`，并指定欧洲站。发品及发品侧半托管供货价列表转交 `linkfox-temu-add-product-us`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 基础价估算 | POST `/temu/proxy` -> type（操作 path）：`temu.local.goods.baseprice.recommend` | `references/apis/temu-local-goods-baseprice-recommend.md` | `scripts/eu_price_baseprice_recommend.py` | 发品或改价前估算。 |
| 推荐供货价查询 | POST `/temu/proxy` -> type（操作 path）：`temu.local.goods.recommendedprice.query` | `references/apis/temu-local-goods-recommendedprice-query.md` | `scripts/eu_price_recommendedprice_query.py` | 读取已有商品推荐价。 |
| 定价单查询 | POST `/temu/proxy` -> type（操作 path）：`bg.local.goods.priceorder.query` | `references/apis/bg-local-goods-priceorder-query.md` | `scripts/eu_price_priceorder_query.py` | 查询定价单与报价。 |
| SKU 批量改价 | POST `/temu/proxy` -> type（操作 path）：`bg.local.goods.priceorder.change.sku.price` | `references/apis/bg-local-goods-priceorder-change-sku-price.md` | `scripts/eu_price_priceorder_change_sku_price.py` | 提交 SKU 基础价变更。 |
| 通用转发 | POST `/temu/proxy` -> type（操作 path）：用户指定的 Temu 操作名 | `references/api.md` | `scripts/temu_eu_proxy.py`、`scripts/temu_proxy.py`、`scripts/check_linkfox_token.py` | 通用入口和认证探测；探测复用此接口。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md` | `scripts/temu_eu_file_download.py`、`scripts/temu_file_download.py` | 获取加签资源。 |

转发操作标识在 Body 的 `type`，不是独立 URL 路径。本技能合计 6 项接口/操作；通用入口不重复计算上述四项专用操作。

## 前置条件

先确定目标店铺及价格业务范围。LinkFox 用户密钥与 Temu 店铺令牌用途不同；店铺令牌需要在卖家后台手动授权获取，或从本地已保存店铺读取。授权步骤与本地工具见 `references/access-token.md`，授权流程见 `references/authorization-flow.md`。

## 价格管理流程

1. 从商品管理的列表、详情或规格查询取得商品、叶子类目和规格信息，核对目标店铺与待处理 SKU。
2. 根据任务查询定价单和报价列表，记录本次查询范围。
3. 按已有商品读取平台推荐供货价，区分低流量和限流场景。
4. 发品或改价前，按类目、规格和站外价格等资料估算推荐基础价。
5. 需要批量改价时，按用户明确指定的目标和价格提交，并展示成功与失败项。
6. 改价后通过定价单查询核对最终供货价及审核结果；仅为核验不得重复提交改价。

按用户任务选择必要步骤，不自动执行整条流程。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：本工具不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次，业务入口不复用响应缓存。失败或空结果时，不得自动翻页、换条件或连续试探；需要继续查询时，先说明已有结果和后续查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-price-eu-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如响应体中的 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分价格概念**：已有商品推荐供货价、按类目和站外价估算的基础价、定价单中的参考价/目标价/原价/最终价含义不同，展示时分别标注。
- **清晰展示结果**：注明店铺和站点；以商品、SKU、币种、价格及定价状态为主列。改价结果分别展示成功 SKU、失败 SKU 与原因、成功定价单。
- **区分提交与生效**：请求成功、部分 SKU 成功和最终价格生效应分别解释；以返回数据和后续定价单为准。
- **保留业务边界**：本地仓定价单与发品侧半托管供货价列表不可混用；商品域独立 SKU 价格列表尚未单独封装，通用转发需另有已知的完整业务定义，不能猜测参数。
- **缓存与调用约定**：业务入口始终禁用响应缓存；`--no-cache` 可显式传入，不影响这一行为。具体选项、认证优先级、参数层级和接口限制见 `references/api.md` 及各接口定义。
- **信息不足时说明边界**：基础价估算尚无完整官方结果字段表；不补造推荐金额。欧洲站单位建议与通用字段说明存在冲突，调用前确认目标店铺的单位约定，详见对应接口定义。
- **结果不足时说明范围**：展示分页和筛选范围，不因空结果、失败或白名单限制自动翻页、换条件或再次提交。

## 使用示例

### 查询欧区定价单与推荐价

用户：帮我查看欧区这些商品的报价，并比较平台建议价。

核对店铺和商品，按需查询定价单及推荐供货价，分别展示当前、建议和目标价格以及币种。

### 批量调整指定 SKU 的基础价

用户：把这些 SKU 的供货价改成我给出的金额。

根据用户指定范围准备变更，展示逐项提交结果，再通过定价单核对最终价格。

### 发品前估算基础价

用户：根据类目、规格和站外售价，估算欧区基础价。

补齐商品资料后估算，说明返回数据范围，不将估算视为改价提交。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
