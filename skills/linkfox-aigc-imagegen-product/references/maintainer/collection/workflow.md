# 业务流程详述：商品套图

## 业务目标

用户上传商品图片（非模特、非服饰类，如美妆、数码、家居、食品等），本技能作为编排层统一规划出图方案（卖点推理 + 画面设计），然后通过 dispatch 在线程池内按类型执行共享流水线，最终交付一组成套的电商图片。

## 输入参数清单

| 参数 | 性质 | 默认 | 说明 |
|------|------|------|------|
| imageUrls | 运行时入参，必填 | — | 用户上传的商品图片 URL 列表 |
| provider | 运行时入参 | GPT_2_5_IMAGE | 默认 LF智能模型 G-2.5 Sunburst；用户指定时原样透传当前可用 requestValue |
| resolution | 运行时入参 | 1K | 首轮预览；确认画面后询问是否重出 2K、medium；只有用户明确要求才传 4K |
| quality | 运行时入参 | low | 首轮预览；用户指定时原样透传 |
| point | agent 层传入（可空） | — | 完整卖点描述（2~3句话），有则跳过卖点推理 |
| pointHint | agent 层传入（可空） | — | 方向性关键词（需扩写） |
| imageDesc | agent 层传入（可空） | — | 完整画面描述，有则跳过画面推理 |
| 比例 | 前端传入（可空） | 1:1 | 非A+图的统一比例 |
| A+图比例 | 前端传入（可空） | 按子类型默认 | A+图专用比例 |

## 步骤概览

| 编号 | 动作 | 上游 | 下游 | 调用能力 |
|------|------|------|------|----------|
| S0 | 场景路由 | 用户消息 | S1/S2/S3 | 内部逻辑判断 |
| S1 | 内容推理（卖点/画面/desc/layout） | S0 | S2 | 内部 AI 推理 |
| S2 | 输出规划方案给用户确认 + **落盘 image-plan.json** | S1 | S3 | Markdown 表格 + AskUserQuestion + `scripts/save_image_plan.py` |
| S3 | agent 单次 dispatch，由 skill 内部并发各任务，再 summary | S2 | 用户 | `scripts/run_collection_pipeline.py` + `scripts/run_one_task.py` |

## 类型路由关系（单张时读取；套图由脚本路由）

- SCENE → `references/types/scene.md`
- CLOSE_UP → `references/types/close-up.md`
- SELLING_POINT → `references/types/selling-point.md`
- PREMIUM_APLUS / STANDARD_APLUS / PHONE_APLUS → `references/types/aplus.md`
- WHITE_BG → `references/types/white-bg.md`

## 已知局限

- 套图编排层不亲自出图，图片质量取决于共享流水线中各类型的参数组装与生图接口
- 多商品场景不支持自动拆分为独立套图，需用户分次上传
- 卖点推理基于 AI 理解，可能不完全准确，用户可在步骤二确认时修改
- 品牌基因提取结果依赖上传图片质量，低分辨率图片可能影响提取准确性
