# 套图运行时索引（Agent 必读）

> 维护细则见 `references/maintainer/collection/`（S0~S3 业务细则）。**运行时禁止 Read maintainer 或 `types/*.md`（套图出图阶段）。**

## 流程

```
S0 判场景 → 写 collection-job.json → run_collection_pipeline --phase plan
    → S2 表格确认（场景 E 可跳过）
    → run_collection_pipeline --phase dispatch（skill 层 ThreadPool 并发跑 run_one_task.py，不渲染图）
    → run_collection_pipeline --phase summary（含 ![]() 的 markdown 明细，整组图由前端 markdown 渲染）→ 交付
```

## 场景速查（S0）

| 场景 | 信号 | plan | 确认 | 出图 |
|------|------|------|------|------|
| D 首次套图 | 无历史套图 | ✅ | ✅ | ✅ |
| B/C/F | 重做/组合/追加含卖点 | ✅ | ✅ | ✅ |
| E 仅白底等 | 追加且无卖点类型 | ✅ `skip_s1:true` | ❌ | ✅ |
| A 重做单张 | 指定某张不满意 | ❌ 单张直出 | — | — |
| G 改品牌基因 | 改主色/语言等 | 重新提取品牌基因并复用已确认条目 | 范围已明确则不重复问 | 按新品牌基因生成指定范围 |

## 默认套图（场景 D，未指定 types）

卖点图×3、种草图×2、模特图×1、白底图×1（不含尺码/A+，除非用户明确要求）

## 脚本

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase plan --job "$DATADIR/collection-job.json"
# 用户确认后 agent 只发 1 个 dispatch Bash（并发由 skill 层 ThreadPoolExecutor 完成，dispatch 不渲染图）：
python <本skill根>/scripts/run_collection_pipeline.py --phase dispatch --state "$DATADIR/collection-state.json"
# summary 输出含 ![]() 的 markdown 明细 + status JSON，整组图由前端 markdown 渲染：
python <本skill根>/scripts/run_collection_pipeline.py --phase summary --state "$DATADIR/collection-state.json"
```

`DATADIR=$(python <brand-gene根>/scripts/save_brand_gene.py --datadir)`

## 状态文件

| 文件 | 说明 |
|------|------|
| `collection-job.json` | plan 入参 |
| `collection-state.json` | plan 产出；run_one_task / summary 必读（含 `task_specs[]` / `run_one_task_script`） |
| `image-plan.json` | 确认后的 imagePlanList；run_one_task 按 `--index` 取第 i 条 |
| `image-urls.json` | 全部 imageUrls |

## 下一步

- S0 完成 → Read `references/runtime/01-plan.md`
- plan 返回 `awaiting_confirm` → Read `02-confirm.md`
- 出图与交付协议 → Read `references/runtime/03-deliver.md`（本技能内置完整协议）

## 场景与意图约束

- A：从历史取指定单张的完整输入，合并修改后按单张路径生成，不重规划整套。
- B：以原类型/数量及本轮意见重规划；本轮被重做的卖点可保留，仍须与其他历史轮次去重。
- C：旧图加新图整体规划；B/C/E/F 复用已有品牌基因。F 追加的卖点及画面与历史所有轮次去重。
- G：提取用户修改的 brandColor/fontStyle/language/platform/salesRegion，其他值沿用；必须调用品牌基因提取技能生成新文件，不复用旧结果。范围不明确才询问全部或特定类型，随后沿用对应图片原 type/point/image_desc/ratio/layout/desc。
- 只规划生成阶段；A+ 转手机 A+、模特裂变、去水印、换背景等后续操作交还调用方编排，不能混入 imagePlanList 或本轮任务计划。
- 多图先检查独立套图意图。若用户希望每件服饰各做一套，解释当前所有图片按整体规划以协调品牌、穿搭与视觉，建议每次单独上传一件服饰，并请其选择整体继续或分次上传；未选择前停止，不自行拆分。整体方案的每个出图任务必须传入全部 URL。

## 用户指定类型时的数量

- 仅规划用户提到的类型，不自行增加其他非关联类型。
- A+ 未指定数量时：指定 A+ 子类型 4 张，按概览→功能→品质→场景分配版式，另加普通版式 SIZE 1 张；用户只说 A+ 时先按 aplusRatio 反推子类型（1464:600/970:600/600:450），仍不确定才兜底 PREMIUM_APLUS。
- 非 A+ 未给数量时默认随机选择 3～5 张；选定数量后显式传 types，脚本不替 agent 随机选数量。用户明确数量时以用户要求为准。

## 内容与版式

point 非空优先使用，pointHint 只约束推理方向；imageDesc 非空直接沿用，否则由 plan 推理，禁止 agent 在对话手工做 S1。历史卖点传 historicalPoints。本批同类型卖点与其他历史轮次去重，允许同一卖点含义的不同表述。
point 用中文 2～3 句话；image_desc 用中文 2～4 句话且不超过 100 个中文字符；desc 通常不超过 10 字，模特图含画面、姿势和景别且不超过 15 字，白底不填。尺码图画面内容固定为「这是一张商品尺码示意图，图中详细标注了产品的各项关键参数」。
人物必须服从用户指定年龄/性别，儿童意图不得改成成人；模特图单人、完整展示服饰，按输入图锁定视角：含正面时用正面，仅背面时用背面，不能把正面服饰转成背面展示。指定模特/场景按对应参考图描述且不写「参考图」字样。多张图保持整体搭配逻辑。
卖点/A+ 的 layout 只用概览、功能、品质、场景并依次轮换；SIZE 用普通、三版轮换；其余类型留空。比例优先使用用户确认修改值，A+ 优先 aplusRatio，其次兼容普通比例，再取子类型默认；其他类型先取普通比例，再取各类型默认。参数与模型支持范围见 `references/cloth-options.md`。
