# 字段汇总表：商品套图

供运行时快速查字段，不必重读 SKILL.md。

## S0 场景路由

| 字段 | 中文 | 方向 | 来源/去向 |
|------|------|------|-----------|
| 用户消息 | 用户输入 | 输入 | 用户 |
| 上下文状态 | 是否已做过套图/历史卖点 | 输入 | 会话上下文 |
| 场景类型 | A-G | 输出 | → 决定执行路径 |

## S1 内容推理

| 字段 | 中文 | 方向 | 来源/去向 |
|------|------|------|-----------|
| imageUrls | 商品图 key 列表 | 输入 | 用户上传 |
| point | 完整卖点（agent 层传入） | 输入 | agent 层 / 空 |
| pointHint | 方向性关键词 | 输入 | agent 层 / 空 |
| imageDesc | 完整画面描述 | 输入 | agent 层 / 空 |
| point[] | 推理后的卖点列表 | 输出 | → S2 imagePlanList |
| image_desc[] | 推理后的画面内容列表 | 输出 | → S2 imagePlanList |
| desc[] | 简单描述列表 | 输出 | → S2 imagePlanList |
| layout[] | 版式列表 | 输出 | → S2 imagePlanList |

## S2 规划确认

| 字段 | 中文 | 方向 | 来源/去向 |
|------|------|------|-----------|
| imagePlanList | 规划方案 JSON | 输入/输出 | S1 产出 → 用户确认 → **落盘** `$DATADIR/image-plan.json` → S3 |
| type | 图片类型 code | 字段 | SCENE/CLOSE_UP/SELLING_POINT/PREMIUM_APLUS/... |
| point | 卖点 | 字段 | 来自 S1 |
| desc | 简单描述 | 字段 | 来自 S1 |
| image_desc | 画面内容 | 字段 | 来自 S1 |
| ratio | 比例 | 字段 | 按比例约束规则确定 |
| layout | 版式 | 字段 | 来自 S1 |

## S3 调度执行

| 字段 | 中文 | 方向 | 来源/去向 |
|------|------|------|-----------|
| imagePlanList | 确认后的方案 | 输入 | S2 落盘 `$DATADIR/image-plan.json`（**禁止仅留上下文**） |
| image-urls.json | 全部商品图 URL | 输入 | 步骤 1 校验后落盘 |
| collection-state.json | run_one_task / summary 入参 | 中间产物 | plan phase 落盘（含 `task_specs[]` / 脚本路径 / brandKey） |
| task-result-*.json | 单任务结果片段（含 assets[]） | 中间产物 | 每个 `run_one_task.py` 落盘，summary 读后汇总 + 写 asset manifest |
| brandGeneJson | 品牌基因 | 输入/生成 | S3 `save_brand_gene.py` 落盘路径 → state `brand_gene_file` |
| provider | 生图模型 | 输入 | 用户选择 |
| resolution | 分辨率 | 输入 | 用户选择（2K/4K） |
| imageUrls | 全部商品图 key | 输入 | 用户上传（必须全量传） |
| 图片产物 | 共享流水线步骤 3 输出 | 输出 | 直接交付用户 |
