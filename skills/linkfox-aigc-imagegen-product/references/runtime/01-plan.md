# plan phase

本节自包含定义商品套图 job；不依赖服饰技能文档。以下字段为本地编排输入，不转发到上传凭证接口。

场景 D 默认 types 为卖点×3 + 场景×2 + 白底×1。

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase plan --job "$DATADIR/collection-job.json"
```

stdout 协议（acpx-bridge 行级流式）：

1. **markdown 表格正文**（首行 `# 套图规划方案` 起）—— Agent **必须原样转发**到对话回复；**禁止**跳过表格直接 `AskUserQuestion` / `TodoWrite` / 出图。
2. **1 行 status JSON**（`status` / `state_file` / `run_one_task_script` / `total` / `summary` 等）—— Agent 内部解析，**禁止贴给用户**。

`awaiting_confirm` → 先转发 stdout 中的 markdown 表格 → Read `02-confirm.md` → 再追加 `AskUserQuestion`；`ready_to_dispatch` → 跳过确认直接并发出图（场景 E）。


## collection-job.json

| 字段 | 类型 | 必填 | 默认/说明 |
|------|------|------|-----------|
| imageUrls | string[] | 是 | 非空有效 http(s) URL，保留全部图及顺序；本地路径先经确认上传。 |
| scene | string | 否 | D；按索引的 A–G 业务场景确定，B/C/D/F 需要 S1，D 默认提取品牌基因，E 跳过确认。A/G 按索引处理后复用单张入口或确认后的计划。 |
| types | object[] | 否 | 未指定默认卖点×3、场景×2、白底×1；指定类型/数量先按索引规则展开为明确槽位。 |
| types[].type | string | 是（有 types 时） | WHITE_BG/SCENE/CLOSE_UP/SELLING_POINT/PREMIUM_APLUS/STANDARD_APLUS/PHONE_APLUS。 |
| types[].count | integer | 否 | 1，须为正数。 |
| provider | string | 否 | 选定模型 requestValue 原样透传；默认 GPT_2_5_IMAGE。 |
| resolution | string | 否 | 用户指定时原样透传；首轮默认 1K。 |
| quality | string | 否 | 用户指定时原样透传；首轮默认 low。 |
| aspectRatio / ratio | string | 否 | 非 A+ 统一比例，aspectRatio 优先；脚本默认 1:1。 |
| aplusRatio | string | 否 | A+ 专用比例，优先于全局比例；默认 PREMIUM_APLUS=1464:600、STANDARD_APLUS=970:600、PHONE_APLUS=600:450；套图不必读取 types。 |
| point | string / string[]（业务意图） | 否 | 完整卖点优先，不再推理对应卖点；数量不足的槽位补充推理。 |
| pointHint | string | 否 | 卖点方向性约束。 |
| imageDesc | string | 否 | 已有完整画面内容优先采用。 |
| sellingPoints / marketingPoints / material / targetPerson / brand / category / sceneStyling / wearingExperience | string / 上游已有值 | 否 | S1 上下文补充，由脚本插入提示词。 |
| historicalPoints | string[] | 否 | 历史卖点，追加时全部去重；整套重做排除被重做那套、避开其它历史轮次。 |
| brandKey | object | 否 | 品牌偏好；嵌套字段见下表。 |
| brand_gene_file | string | 否 | 已有品牌基因 JSON 绝对路径，复用时不重复提取。 |
| extract_brand_gene | boolean | 否 | false 可关闭 D 的提取；已有基因优先，品牌变更 G 必须先重新提取。 |
| skip_s1 | boolean | 否 | true 跳过 S1；仅在业务场景已明确允许且所需信息已备齐时使用。 |
| skip_confirm | boolean | 否 | true 跳过确认；仅在已有适用的明确确认或场景 E 下使用，不能替用户默认确认。 |
| datadir | string | 否 | 会话 data 绝对路径，默认由本地目录工具解析。 |
| textgen_script / imagegen_script / brand_gene_save_script / run_one_task_script | string | 否 | 已存在的绝对脚本路径优先；否则由 runner 自动解析同级技能官方脚本及本技能 run_one_task。 |

| brandKey 字段 | 类型 | 默认 | 说明 |
|--------------|------|------|------|
| language | string | 英文 | 图片内目标语言。 |
| platform | string | 亚马逊 | 发布平台。 |
| salesRegion | string | 美国 | 销售地区。 |
| brandColor | string | 空串 | 主色偏好。 |
| fontStyle | string | 空串 | 字体偏好。 |
| brandName | string | 空串 | 品牌名。 |

本地 types[].count=0 或不支持的类型在调用下游前报错；imageUrls 必须是数组，不能用 URL 字符串冒充。

## 内容推理规则

用户完整 point/imageDesc 优先；有 pointHint 时围绕其方向扩写，否则自动推理。卖点用中文 2–3 句话，补足槽位时可做相似卖点的不同描述，避开其它历史轮次和同批同类型的重复表达。画面内容用中文 2–4 句、100 字内，描述主体、机位、光线、环境，不能照抄原图场景；人物先遵循用户受众要求，儿童不得改成年模特。desc 为 10 字内中文主题。白底不需 point、image_desc、desc。卖点/A+ layout 只用概览、功能、品质、场景，其它类型空串；一般轮流分配；某个 A+ 子类型恰好五张时，由脚本固定为概览、功能、品质、场景、场景，不让 S1 覆盖。用户完整 point 按非白底槽位顺序采用，imageDesc 应用到非白底槽位；白底内容字段始终为空。

S1 原文仅作内部素材，完成后直接进规划表，不逐条向用户再汇报。品牌基因在 D 首次提取，已有文件的 B/C/E/F 复用；缺省 brandKey 采用上表，非空用户值优先。提取经官方 save_brand_gene.py 保存，state 使用 brand_gene_file，不内联大 JSON、不只留对话记忆。运行时 pipeline 内部依序完成 S1 和品牌提取，Agent 不额外重复或并发调用。

S1 或品牌提取的生文任务已创建后发生轮询失败或超时，保留返回的 taskId 和错误文件，按下游文档恢复查询，不重跑 plan 创建第二个生文任务。

## 计划与状态文件

比例优先级：非 A+ 用用户全局比例，否则按类型默认 1:1；A+ 用 aplusRatio，其次用户明确提供的全局比例，否则分别为高级 1464:600、普通 970:600、手机 600:450。脚本在 S1 推理合并后保留上述比例，不允许模型覆盖用户参数或子类默认值。用户确认阶段的修改优先，不将专属 A+ 比例用于非 A+ 图。

plan 写 image-urls.json、image-plan.json、collection-state.json，需确认时另存 plan-summary-*.md。state 包含 variant、scene、imageUrls/image_urls_file、provider、resolution、plan_file、brandKey、brand_gene_file、textgen_script、imagegen_script、run_one_task_script、skill_root、datadir、write_asset_manifest、task_specs；task_specs 每项为 id/type/label。stdout 的 status JSON 含 status、skip_confirm、plan_file、state_file、brand_gene_file、image_urls_file、run_one_task_script、total、specs（index/id/type/label）、summary（index/type/label/desc/point/image_desc/ratio），需要确认时还含 plan_summary_file。

这些是本地脚本状态和输出，不是 LinkFox API 响应。用户可修改最终 imagePlanList；确认后应直接供 dispatch 使用，不重跑会覆盖修改的推理阶段。修改与重新展示方法见 02-confirm.md。
