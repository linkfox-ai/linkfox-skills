---
name: linkfox-shopee-store-auth
description: 管理 Shopee（虾皮）店铺的 ERP 与广告（AD）独立授权，生成授权链接、查询已授权店铺与授权状态，并为后续业务确定店铺。适用于卖家账号绑定、补充广告授权、核对授权状态和多店选择；不适用于直接管理商品、订单、物流、广告投放等店铺业务，也不用于前台选品研究。
---
# Shopee 店铺授权与管理

## 适用范围

### 适用

完成 Shopee Open Platform 的店铺授权、已授权店铺查询和授权状态核对，为下游业务准备店铺身份。
用户提到虾皮卖家账号绑定、ERP 授权、广告授权、授权失效或“我的虾皮店”时，按目标能力处理。

**场景速查**

| 用户表达 | 查询场景 |
| -------- | -------- |
| 绑定我的虾皮店铺 | 生成 ERP 授权链接，引导浏览器完成授权。 |
| 已绑定店铺，还要开广告 | 检查 AD 记录，补充广告应用授权。 |
| 商品业务和广告都要用 | 分别检查两种应用，仅补充缺失授权。 |
| 看看我授权了哪些店 | 展示店铺与对应应用记录。 |
| 这家店的授权是否有效 | 查询对应应用的授权状态与到期元数据。 |
| 用我的店查业务数据 | 先选店并核对目标应用，再交由业务技能执行。 |

### 边界

本技能负责授权与选店。业务转发仅用于下游交接，不据此主动执行用户未要求的店铺操作。具体业务按以下范围转交：

- **Shopee 订单查询与处理** → `linkfox-shopee-store-orders`
- **Shopee 店铺信息与设置** → `linkfox-shopee-store-shop`
- **Shopee 店铺商品 listing** → `linkfox-shopee-store-product`
- **Shopee 跨境全球商品 GlobalProduct** → `linkfox-shopee-store-global-product`
- **Shopee 跨境商户信息 Merchant** → `linkfox-shopee-store-merchant`
- **Shopee 物流发货 Logistics** → `linkfox-shopee-store-logistics`
- **Shopee 退货退款 Returns** → `linkfox-shopee-store-returns`
- **Shopee 站内广告 Ads** → `linkfox-shopee-store-ads`（业务调用；授权仍用本技能的 `appType=ad`）
- **Shopee 支付结算 Payment** → `linkfox-shopee-store-payment`
- **Shopee 联盟营销 AMS** → `linkfox-shopee-store-ams`
- **Shopee 店铺视频 Video** → `linkfox-shopee-store-video`
- **Shopee 媒体上传 MediaSpace** → `linkfox-shopee-store-media-space`
- **Shopee 媒体上传 Media** → `linkfox-shopee-store-media`（`api/v2/media/...`，module=130）
- **Shopee 头程物流 FirstMile** → `linkfox-shopee-store-first-mile`
- **Shopee 折扣促销 Discount** → `linkfox-shopee-store-discount`
- **Shopee 套装优惠 Bundle Deal** → `linkfox-shopee-store-bundle-deal`
- **Shopee 加购优惠 Add-On Deal** → `linkfox-shopee-store-add-on-deal`
- **Shopee 店铺优惠券 Voucher** → `linkfox-shopee-store-voucher`
- **Shopee 店铺秒杀 Shop Flash Sale** → `linkfox-shopee-store-shop-flash-sale`
- **Shopee 关注有礼 Follow Prize** → `linkfox-shopee-store-follow-prize`
- **Shopee 精选商品 Top Picks** → `linkfox-shopee-store-top-picks`
- **Shopee 店铺分类 Shop Category** → `linkfox-shopee-store-shop-category`
- **Shopee 账户健康 Account Health** → `linkfox-shopee-store-account-health`
- **Shopee Public 公共模块** → `linkfox-shopee-store-public`（`v2.public.*` 底层 OAuth / Partner 查询）
- **Shopee Push 推送机制** → `linkfox-shopee-store-push`
- **Shopee SBS 仓储服务** → `linkfox-shopee-store-sbs`
- **Shopee FBS 巴西仓储** → `linkfox-shopee-store-fbs`
- **Shopee 直播 Livestream** → `linkfox-shopee-store-livestream`
- Shopee 选品（友鹰） → `linkfox-youying-shopee-product-search`
- 商品 listing 管理 → `linkfox-shopee-store-product` 或 `developerProxy` 商品 API

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 生成授权 URL（`authorizeUrl`） | POST `/shopee/authorizeUrl` | `scripts/authorize_url.py` | 为 ERP 或 AD 应用生成新授权链接。 |
| 列出已授权店铺（`authorizedStores`） | POST `/shopee/authorizedStores` | `scripts/authorized_stores.py` | 列出当前用户的店铺与应用授权记录。 |
| 查询授权状态（`storeTokens`） | POST `/shopee/storeTokens` | `scripts/store_tokens.py` | 查询状态与元数据，剥离原始令牌。 |
| 业务转发（`developerProxy`，下游协议） | POST `/shopee/developerProxy` -> path：`api/v2/**`；如 `api/v2/product/get_item_list`、`api/v2/ads/get_total_balance` | 无；由下游业务技能调用 | 服务端按资源路径选择对应应用令牌；本技能不提供业务操作封装。 |

## 前置条件

确定需要 ERP、广告或两种能力；授权前建议取得便于识别的店铺名并确认授权区域。需要操作已有店铺时，先按下方流程定位目标。各接口参数、时效、限制与脚本选项见 [接口说明](references/api.md)。

## 授权与选店流程

1. **确定能力与店铺**：商品、订单和物流等使用 ERP，站内广告使用 AD。查询已授权列表，按店铺身份和应用类型共同匹配；具体兼容约定见接口说明。
2. **为下游选店**：根据下表定位目标。定位成功后仅确认店铺标识与应用类型，不向用户索要令牌。

| 用户上下文 | 执行动作 |
|---|---|
| 只有一家店且已具备目标能力 | 直接使用该店铺标识，无需追问。 |
| 多家店，只提到店名且目标不明确 | 按店铺展示名澄清，不擅自选店。 |
| 提供可唯一定位的店名或店铺编号 | 直接定位。 |
| 显式给出店铺编号或商户编号 | 使用给定标识，核对对应应用授权。 |
| 店铺存在但缺少目标应用授权 | 先补充对应授权，再执行下游业务。 |

3. **生成新授权链接**：首次授权或补授权时，建议确认店铺展示名、区域和目标应用，然后运行 `scripts/authorize_url.py`。广告授权须明确标注为 AD；不得用 ERP 授权替代。两种能力均缺失时分别生成两个链接，标注用途，说明需要完成两次授权；仅缺一种时只补该项。
4. **浏览器完成授权**：把链接交给用户，并提醒：“为保障店铺安全，请务必在日常运营该店铺的安全网络环境中打开此链接。强烈建议使用紫鸟浏览器等专业的防关联浏览器进行授权，切勿在陌生或公共网络下操作。”授权链接的时效及重新获取要求见接口说明。优先从脚本保存的文件或剪贴板复制完整链接，避免终端软换行破坏地址。
5. **核验结果**：用户完成授权后，系统自动接收令牌并保存，浏览器跳转成功或失败页。再次查询已授权列表，确认目标店铺对应应用的记录；必要时通过 `scripts/store_tokens.py` 核对状态，不为业务调用提前获取令牌。
6. **交给下游**：确认目标应用已授权后，将店铺标识交给相应业务技能；由服务端按资源路径选择令牌。转发参数与路由限制见接口说明。
7. **处理异常**：授权失败先解释原因，不擅自重试。授权完成却查不到店铺时，可能是回调未成功落库或 `state` 不匹配，建议核查服务日志，再按用户需要重新生成链接。已授权却无法使用广告时，先核对 AD 记录；服务端确认授权已失效、无法继续使用时，按目标应用重新授权。具体错误码与处理见接口说明。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：本工具不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次；用户完成授权后需重新查询列表以核验结果，每次授权尝试均重新生成链接。业务脚本禁用响应缓存，每次运行均请求接口；失败或空结果时不自动连续试探，先解释原因，再按用户需要继续。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-auth-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。响应数据禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、响应体中的常见计数（如 `total`）、最大列表字段的长度和前 3 条样本。
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

- **双应用独立**：ERP 与 AD 使用不同应用和令牌；同店可有两条授权记录，一次授权不代表同时具备两种能力。
- **理解授权身份**：`authRecordId` 对应一条应用授权记录；店铺编号与商户编号是定位店铺的身份信息。历史空应用类型按 ERP 理解，不认作 AD。
- **展示店铺清单**：使用表格展示店铺名、店铺编号、商户编号、区域与应用类型；同店的 ERP 和 AD 记录分别展示，不把授权记录数当作不同店铺数。
- **仅展示授权状态**：展示状态与过期元数据，不假设响应包含原始令牌，不向用户索要令牌。脚本会在落盘与打印前剥离原始令牌。
- **状态读取边界**：`storeTokens` 仅读数据库；`expireIn` 是保存的有效期秒数，不是实时剩余时间，`ACTIVE` 仅表示库内存在令牌，不保证当前上游可用。不要据此计算倒计时或要求每 4 小时重新授权；下游转发的服务端刷新行为见接口说明。
- **理解授权过程**：生成链接后由用户在浏览器授权，Shopee 推送令牌，系统按 `state` 保存。内部回调和跳转地址不作为用户直接调用的接口。
- **保留已取得的数据**：先读摘要，再按需提取落盘字段；失败与空结果的后续调用遵循成本约束。

## 使用示例

### 首次授权 ERP 店铺

用户：绑定我的虾皮店，后续查订单。

建议取得店铺展示名并确认区域，生成 ERP 授权链接；用户在安全环境完成授权后，核验列表中的对应记录。

### 为已授权店铺补充广告能力

用户：这家店已经绑定，但广告查不了。

核对该店的 AD 记录；缺失时仅生成广告应用链接，授权后再次确认，再交给广告业务技能。

### 为下游定位店铺

用户：帮我用“东南亚一店”查询业务数据。

查询列表，按店名与目标能力定位；唯一匹配则直接使用店铺标识，多店歧义时澄清，不要求用户提供令牌。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
