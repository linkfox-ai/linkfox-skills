# 服饰卖点图（SELLING_POINT）— ③textgen 改写支线

把核心卖点转成单张带 Text on Image 文案与版式的卖点图。模板由"亚马逊A+视觉营销总监"角色驱动，按 `{layoutInfo}` 版式意图组织模块，针对服装品类侧重生活方式营造、面料质感与版型优势展示。

> 卖点图与 A+ 图（`references/types/aplus.md`）**共用同一份模板** `selling-point-aplus.txt`，靠 `{layoutInfo}` 版式意图区分。

## 适用场景

| 场景 | 说明 |
|------|------|
| 单版式卖点图 | 把一个核心卖点转成带标题 / 副标题文案与视觉构图的 1:1 卖点版式图 |
| 概览 / 功能 / 品质 / 场景版式 | 按 layout 标签组织模块版式，突出面料质感与版型优势 |

## 类型特有参数

| 参数 | 占位符 | 说明 |
|------|--------|------|
| `point` | `{customer_keywords}` | 核心卖点（中文一段详细描述），提炼为 Text on Image |
| `layout` | `{layoutInfo}` | 版式标签（概览/功能/品质/场景），脚本据此生成"服装卖点图·{layout}展示版式：突出面料质感与版型优势" |
| `brandGeneJson` | `{brandKey}` | 品牌基因（主色 brandColor、字体 fontStyle、语言、平台、地区），控版式主色与字体 |
| `imageDesc` | `{customSetting}` | 用户自定义（人物 / 道具 / 氛围），优先级最高 |
| `language` | `{language}` | 图片内文案语种 |
| `salesRegion` | `{salesRegion}` | 销售地区，决定模特人种 / 场景风格 |
| `platform` | `{platform}` | 发布平台，决定视觉规范 |
| `ratio` | `{Ratio}` | 生图比例 |

- 默认比例 1:1。`{infringingWords}` 由脚本填空串。

## 步骤 2 差异：③textgen 改写（过敏感词）

- 走 **③textgen 改写**支线：用 `scripts/build_textgen_params.py` 读模板 → 填占位符（null 替换成空串）→ 产出 textgen 参数文件（`model=GEM_3_1_PRO`、`thinkingLevel=high`）。
- **过敏感词**：脚本在 prompt 末尾自动追加敏感词规避指令，要求撰写 Text on Image 文案时规避违禁 / 侵权词。

```bash
DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)
BRAND_GENE_FILE='<S1 save_brand_gene.py 落盘的 brandGeneJson 绝对路径>'
python scripts/build_textgen_params.py \
  --type SELLING_POINT \
  --image-urls '<步骤1的URL JSON数组>' \
  --point '<核心卖点>' \
  --layout '<概览/功能/品质/场景>' \
  --brand-gene-file "$BRAND_GENE_FILE" \
  --image-desc '<用户自定义，可空>' \
  --language '<语言>' --sales-region '<地区>' --platform '<平台>' \
  --ratio '1:1' \
  --out "$DATADIR/textgen_sp.json"
```
> **运行时模板唯一来源**：`scripts/templates/selling-point-aplus.txt`（与 A+ 图共用），运营更新直接改该 .txt。

随后按本 skill **SKILL.md「步骤2 → ③textgen 改写支线」给出的标准链式调用**执行：把上面产出的 `$DATADIR/textgen_sp.json` 作为 `<textgen_params.json>`，经 `--stdin --content-only` 取出单行 prompt → `jq` 内联进下游 imagegen 参数 → 进入共享流水线步骤 3 出图（下游自动把 `⏎` 还原为换行符）。**具体命令以 SKILL.md 步骤2 为准，此处不重复。**

## 执行自检

- [ ] 步骤 1 所有参考图都为公开可访问 URL，否则报错而非带空图调 `linkfox-aigc-textgen`
- [ ] 步骤 2 占位符全部被真实值或空串替换，最终 prompt 里无残留 `{xxx}`，且末尾已追加敏感词规避指令
- [ ] 服装款式、颜色、细节与参考图 100% 一致；产品颜色与输入图强关联，未随意增色
- [ ] Text on Image 仅用 `language` 一种语种，文案合规、无违禁 / 侵权词，未出现色号 / fontStyle / "headline" 等字样
- [ ] 版式严格遵循 `{layoutInfo}` 结构；背景非纯白、配色以 brandColor 为准
- [ ] 比例为 `{Ratio}`（默认 1:1）；步骤 3 `provider` 已按入参透传、`outputNum=1`、`aspectRatio=ratio` 已原样透传给 imagegen

## 已知局限

- 卖点图 / A+ 共用字典模板，靠 `{layoutInfo}` 区分；版式意图填错会导致版式串型。
- 强依赖 `linkfox-aigc-textgen`（`GEM_3_1_PRO`）对卖点的视觉化与版式扩写；改写质量影响最终构图。
- 敏感词规避以"prompt 末尾追加规避指令、由文本模型自审"实现，无确定性词库兜底，合规仍需上游或人工把关。
- 多张参考图时由模型自行判断主体服饰角色，复杂组合下可能误判主图。
