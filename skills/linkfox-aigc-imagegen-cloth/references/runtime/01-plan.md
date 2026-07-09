# plan phase

## 前置

- `imageUrls` 全部为公开 HTTPS URL（本地路径先 `linkfox-file-upload`）
- 已 Read `00-index.md` 并完成 S0

## 写 collection-job.json

```json
{
  "scene": "D",
  "imageUrls": ["https://..."],
  "provider": "BANANA_PRO",
  "resolution": "2K",
  "aspectRatio": "1:1",
  "aplusRatio": "1464:600",
  "point": "",
  "pointHint": "",
  "imageDesc": "",
  "sellingPoints": "",
  "historicalPoints": [],
  "brandKey": {"language": "日文", "platform": "亚马逊", "salesRegion": "日本", "brandColor": "", "fontStyle": ""},
  "brand_gene_file": null,
  "types": null,
  "skip_s1": false,
  "datadir": "<DATADIR绝对路径>"
}
```

| 字段 | 说明 |
|------|------|
| `types` | 非 null 时 `[{"type":"SCENE","count":2}]`；null 用场景 D 默认 |
| `brandKey` | **必填透传**：前端「语言/平台/销售地区/字体/品牌色」映射为 `language`/`platform`/`salesRegion`/`fontStyle`/`brandColor`；缺省才用英文/亚马逊/美国 |
| `brand_gene_file` | 已有品牌基因绝对路径则传入 |
| `skip_s1` | 场景 E 设 `true` |

## 执行

```bash
python <本skill根>/scripts/run_collection_pipeline.py --phase plan --job "$DATADIR/collection-job.json"
```

stdout 协议（acpx-bridge 行级流式）：

1. **markdown 表格正文**（首行 `# 套图规划方案` 起）—— Agent **必须原样转发**到对话回复；
2. **1 行 status JSON**（`status` / `plan_file` / `state_file` / `summary` 等）—— Agent 内部解析，**禁止贴给用户**。

**禁止**依赖 `Saved full response: <md路径>` 让用户看到表格——bridge 对 Bash 工具卡内的 md 路径**不会**内联渲染；`plan-summary-<ts>.md` 仅作留档。

`status` 分支：

- `awaiting_confirm` → 先转发 stdout 中的 markdown 表格 → Read `02-confirm.md` → 再追加 `AskUserQuestion`
- `ready_to_dispatch` → 跳过确认，直接进入并发出图（场景 E，无表格）
- `error` → 如实上报
