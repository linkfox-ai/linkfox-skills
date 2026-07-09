# 业务流程详述：服饰套图

## 业务目标

用户上传服饰图片（上装/下装/连衣裙/外套/鞋帽等），本技能作为编排层统一规划出图方案（卖点推理 + 画面设计），然后内部按类型 Read 对应的 type reference 并执行共享流水线逐张生成，最终交付一组成套的电商图片。

## 输入参数清单

| 参数 | 性质 | 默认 | 说明 |
|------|------|------|------|
| imageUrls | 运行时入参，必填 | — | 用户上传的服饰图片 URL 列表 |
| provider | 运行时入参 | 由用户确认 | 生图模型：BANANA_PRO / GPT_2_IMAGE / BANANA_2 / AIDRAW_EDIT / WAN2_7 |
| resolution | 运行时入参 | 由用户确认 | 分辨率：2K / 4K |
| point | agent 层传入（可空） | — | 完整卖点描述（≥2句话），有则跳过卖点推理 |
| pointHint | agent 层传入（可空） | — | 方向性关键词（需扩写） |
| imageDesc | agent 层传入（可空） | — | 完整画面描述，有则跳过画面推理 |
| 比例 | 前端传入（可空） | 1:1 | 非A+图的统一比例 |
| A+图比例 | 前端传入（可空） | 按子类型默认 | A+图专用比例 |

## 步骤概览

| 编号 | 动作 | 上游 | 下游 | 调用能力 |
|------|------|------|------|----------|
| S0 | 场景路由 | 用户消息 | S1/S2/S3 | 内部逻辑判断 |
| S1 | 内容推理（卖点/画面/desc/layout） | S0 | S2 | 内部 AI 推理 |
| S2 | 输出规划方案给用户确认 + **落盘 image-plan.json** | S1 | S3 | Markdown 表格 + AskUserQuestion + `save_image_plan.py` |
| S3 | agent 端 N 个并发 Bash（`run_one_task.py --state --index`）+ summary | S2 | 用户 | `run_one_task.py` + summary phase |

## 类型路由关系

- WHITE_BG → `references/types/white-bg.md`（①静态直出）
- MODEL_IMAGE → `references/types/model-image.md`（②占位符直出）
- SCENE → `references/types/scene.md`（③textgen 改写）
- SELLING_POINT → `references/types/selling-point.md`（③textgen 改写）
- PREMIUM_APLUS / STANDARD_APLUS / PHONE_APLUS → `references/types/aplus.md`（③textgen 改写）
- SIZE → `references/types/size.md`（阶段1③textgen + 阶段2②占位符直出）

## 已知局限

- 套图编排层不亲自出图，图片质量取决于共享流水线中各类型的参数组装与生图接口
- 多商品场景不支持自动拆分为独立套图，需用户分次上传
- 卖点推理基于 AI 理解，可能不完全准确，用户可在步骤二确认时修改
- 品牌基因提取结果依赖上传图片质量，低分辨率图片可能影响提取准确性
