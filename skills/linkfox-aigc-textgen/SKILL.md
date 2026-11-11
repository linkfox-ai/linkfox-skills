---
name: linkfox-aigc-textgen
description: AI 生文与图片理解，支持商品标题、五点描述、营销文案、翻译和数据总结。支持 GEM_3_1_PRO、GEM_3_7_FLASH、GEM_4_A、GT_6_1_S、GT_6_1_T、GT_6_L、GT_6_A；兼容旧模型别名。创建后查询同一任务，展示文本并以 count 读取 AI 实扣；不用于图片或视频生成。
---
# AI 生文与图片理解

## 适用与边界

- 按提示词生成商品标题、五点、营销文案、翻译、数据分析总结，或结合最多10张图片理解商品。
- 生图使用 linkfox-aigc-imagegen，生视频使用 linkfox-aigc-videogen，报告文件排版使用 linkfox-report-generator。
- 标准生文契约以文本和图片为输入，不把原生视频或音频当成图片传入。GT明确不支持原生音视频。视频任务先按对应业务技能的既有能力准备图片帧；帧图不能恢复音轨，不猜测口播。旧入口的视频能力必须单独确认，不能沿用为所有新模型的承诺。

## 接口与文件

| 操作 | 端点 | 实现 |
|---|---|---|
| 创建任务 | POST /aigc/textGenAsync | scripts/aigc_textgen.py |
| 查询已有任务 | POST /aigc/textTaskQuery | scripts/aigc_textgen.py |
| 本地图片上传 | POST /oss/getStsVoucherByAPI | scripts/upload_file.py |

详细接口、兼容与计费见 [references/api.md](references/api.md)。上传前确认图片可公开，再按 [references/file-upload.md](references/file-upload.md) 操作。禁止运行未获授权的真实收费测试。

## 模型与参数

| 标准 model 编码 | 场景 | thinkingLevel |
|---|---|---|
| GEM_3_1_PRO | 高质量生成、复杂分析；接口默认模型 | low / medium / high |
| GEM_3_7_FLASH | 常规文案、翻译、图片理解 | minimal / low / medium / high |
| GEM_4_A | 复杂推理、代码与高质量长文 | low / medium / high |
| GT_6_1_S | 复杂分析、文本生成 | low / medium / high / xhigh / max |
| GT_6_1_T | 图片理解、自然文本写作 | none / low / medium / high / xhigh / max |
| GT_6_L | 轻量、高频生文 | none / low / medium / high / xhigh / max |
| GT_6_A | 深度分析、高难度生成 | low / medium / high / xhigh / max |

- 仅 prompt 必填，最多100000字符。model建议显式传入；不传仍默认GEM_3_1_PRO，不是Flash。可用模型以环境实际部署版本和模型开通为准；新版接口的新建任务统一走AI生文计费。不可用时报告真实错误，不自动换模型试收费。
- 兼容 LF_GEM_1→GEM_3_FLASH、LF_GEM_2→GEM_3_1_PRO；GEM_3_FLASH仅作旧调用兼容，不把LF_GEM_1重定向到3.7。未知model报错，不静默回退。
- thinkingLevel可选，非法组合不自动降级。GT不传为medium；GEM不传交模型处理。GT不接受minimal/ultra；none仅GT_6_1_T、GT_6_L支持。
- systemPrompt仅GT支持。GEM应把指令放进prompt。
- imageUrlList为标准图片字段，可省略或传[]；最多10张HTTP(S)图片。兼容旧imageUrls，两个字段同时传入时内容必须一致。

## 安全执行流程

1. 明确目标、语言、模型和输入图片。已有公开URL直接复用；本地图片按上传规范准备，失败不创建生文任务，不把本地路径传给接口。
2. 只创建一次，取得并保存taskId；轮询同一任务直至SUCCESS或FAILED。网络状态不明、客户端超时、会话中断时只恢复查询，不自动重建收费任务。
3. 新任务由AI在生成成功后结算，查询不新增收费；旧任务保留原服务链路，不以客户端判断重算旧费用。
4. 新任务以count为实际扣点，points只是按用量计算的点数；costToken=0表示不要让网关再扣一次，不代表免费。实扣可能因余额或成员限额封顶小于points。
5. billingStatus为USAGE_UNAVAILABLE或DEDUCTION_UNCONFIRMED时，保留内容和taskId、明确提示核对原任务/账本；不能将count=0称为正常免费，也不自动重试创建或退款。
6. 需要继续用户已要求的生图等流程时，用--content-only提取文本，用JSON编码器构造下游参数；不手工拼接未转义引号。

## 脚本调用

推荐stdin避免提示词转义：

~~~bash
python scripts/aigc_textgen.py --stdin < params.json
python scripts/aigc_textgen.py --stdin --content-only < params.json
# 恢复同一任务；不会创建新任务
python scripts/aigc_textgen.py '{"taskId":"123456789"}'
# 高思考等级可延长本次客户端等待；不改变AI任务期限和计费标准
python scripts/aigc_textgen.py --stdin --poll-timeout 1800 < params.json
~~~

- 默认等待600秒，每次HTTP最多150秒；查询间隔10秒递减至5秒。--poll-timeout可指定正数秒数。客户端等待超时不代表服务端任务失败，按保留的taskId恢复查询。
- 创建只调用一次，不重试；查询仅对暂时的传输错误额外重试最多3次。认证、额度、明确业务失败以及本地保存/解析错误立即停止，查询失败不触发创建。
- 创建和查询始终禁用响应缓存；--no-cache保留兼容。

## 输出与展示

- 默认/--inline：stdout为响应JSON，诊断与计费警告只写stderr。--content-only仅输出内容，不混入计费提示。
- 原始响应和最终结果均保存到当前目录linkfox/<YYYY-MM-DD>/<session>/data/；SESSION_ID优先，禁止失败后回退到/tmp。
- 大结果默认stdout为含ok、truncated、savedPath、bytes、完整content的JSON信封；服务端实际提供的count、points、costToken、billingStatus、pricingVersion也保留。--inline强制全量。
- 内容换行保持既有⏎占位符机制，向用户展示时还原换行；下游AIGC脚本会解码。缺少用量或未返回count时不编造费用。
- 失败非零退出；成功文本但计费需核对时保留成功内容并在stderr警告，不通过重新创建任务来“修复”计费。

## 请求示例

快速文案（明确指定支持minimal的模型）：
~~~json
{"prompt":"写三条无线音箱卖点","model":"GEM_3_7_FLASH","thinkingLevel":"minimal","imageUrlList":[]}
~~~

图片分析：
~~~json
{"prompt":"分析商品图片的构图和卖点","model":"GEM_3_1_PRO","thinkingLevel":"high","imageUrlList":["https://example.com/product.jpg"]}
~~~

GT系统指令：
~~~json
{"prompt":"生成三条商品卖点","model":"GT_6_L","thinkingLevel":"none","systemPrompt":"使用中文，每条一句话","imageUrlList":[]}
~~~

## 认证、额度与反馈

缺少LINKFOX_AGENT_API_KEY/LINKFOXAGENT_API_KEY、HTTP401/402或提示额度不足时，按[references/onboarding.md](references/onboarding.md)处理。执行前可用额度至少100点；成功按实际usage计价，应扣最低1点，正常生成失败不扣点。具体价格与缓存/长上下文规则以AI配置和Wiki为准，不在技能内维护第二套单价。

使用反馈遵循[references/api.md#Feedback](references/api.md#Feedback)，不得因反馈打断用户当前任务，也不在本次开发中发送外部反馈。
