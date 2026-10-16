# 动态可用模型列表（仅查询，不改生成链路）

| 原生成入口 | 模型列表 GET（相对配置域名） | bizType |
|---|---|---|
| /aigc/imageGenAsync | /image/model/config/list | 201 |
| /aigc/videoGenAsync | /image/video/model/config/list | 88 |
| /aigc/multiImageVideoGenAsync | /image/video/model/config/list | 88 |

## 环境地址覆盖

- 模型配置域名优先读取环境变量 `LINKFOX_AI_API_URL`；未设置、空字符串或仅空白时默认 `https://ai-api.linkfox.com`。
- 每次查询读取当前配置，自动去除首尾空白和末尾 `/`；可以使用自定义域名或带路径前缀的基础地址。
- 生成请求仍使用 `LINKFOX_TOOL_GATEWAY`。两个服务分别配置，不根据网关域名、Key 或测试前缀自动推断模型配置地址，也不复用登录、团队或文本模型的地址变量。

| 环境 | `LINKFOX_AI_API_URL` | `LINKFOX_TOOL_GATEWAY` |
|---|---|---|
| 生产 | `https://ai-api.linkfox.com`（默认） | `https://tool-gateway.linkfox.com`（默认） |
| 测试 | `https://test-ai-api.linkfox.com` | `https://test-sz-tool-gateway.linkfox.com` |

仅配置生成网关不会同步切换模型目录；测试环境必须同时设置两个地址。配置地址无效或查询失败时沿用当前包静态目录兜底，不改向生产重试，不发送生成 Key 或网关身份头。

## 查询和选择

介绍或选择模型前，按本 skill 的生成脚本调用 `--list-models --inline`。此模式只 GET 公共配置，不需要生成 API Key，不向配置域名发送 Authorization、SESSION_ID 等生成网关头，不创建任务、不轮询、不下载。

普通场景使用动态完整目录，不能把旧模型表或别名兼容表当成白名单。能力信息用于介绍和选择模型/参数选项：参考图、时长、声音等必须与用户任务相符，但不能据此新增一套通用执行前校验或静默改变参数。

只有明确的专用业务限制，在**列表查询**时传 `--allowed-models '["原有模型值", "..."]'` 取交集：图片裂变指定两模型、真人感固定模型、视频复刻四模型等。空数组表示无可选模型。普通图转视频、带货视频、多图入口不按历史模型名称封顶。

用户展示使用 name。requestValue 是构造新选择请求时的兼容参考值；图片依据 apiCode 及既有别名映射，视频依据 code（不是下游 apiCode）。同一个模型的旧值/规范别名等价，不能因字符串形式不同误拒绝；**已有生成调用值不强制迁移或重写**。重复渠道绑定单一记录，不合并不同渠道能力。

图片目录的 `refImageCount` 是本工具入口的有效参考图上限（当前最多10张）；`modelRefImageCount` 保留模型配置的原始上限。选择参考图数量使用前者，不能按 rawResponse 中的模型原始上限超出入口能力。这只修正能力展示，不限制可选模型，也不扩大原生成接口能力；视频参考图上限仍按各自动态配置返回。

## 失败兜底

5秒超时；连接/HTTP/协议读取错误、业务状态失败或解析/结构错误时，source=fallback，返回当前包 aigc_model_fallbacks.json 的原静态列表。成功返回空列表、维护或模型缺失，不能用静态表补回。静态目录只用于查询失败，不是永久可选上限。

## 保持原生成行为

正常 JSON 生成调用仍直接走原 create_task → 原网关 → 原轮询/下载/交付流程。**不会额外 GET 模型列表、不会保存一份配置作为提交前条件、不会用配置白名单拦截请求，也不会修改 provider、比例、质量、时长或分辨率。**

生成时不要传新的 --allowed-models 参数；专用范围在原业务确认/选择流程维持，而不是给全部生成入口增加新的权限或校验层。

默认模型、默认参数、缺参追问方式不改变。追问里的模型/分辨率/质量选项应参考当前模型，不能让1K模型只能在2K/4K中选择。没有合法默认值时提示选择，不自动调参数或换模型。

A+ 等业务版位的 1464:600、970:600、600:450 仍按原流程传递；这些不等于普通比例字段的字面档位，不能新增逐字符串校验误拦，也不在本次加入裁切、补边或近似替换。

## 查询输出与独立打包

查询结果以配置 JSON 输出，含 source、models、dataFile。完整原始响应正常落到会话 data/；超过8KB可用 --inline 打印完整目录。配置存档失败仅记录 stderr、返回 dataFile=null，不变成新的生成阻断点。输出不使用媒体交付标记 Saved full response。

每个独立 skill 的 scripts/ 同目录包含 aigc_model_config.py 和 aigc_model_fallbacks.json；不跨 skill 导入。生成响应和媒体仍使用原有落盘交付协议。
