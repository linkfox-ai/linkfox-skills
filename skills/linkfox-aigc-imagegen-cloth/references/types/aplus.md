# 服饰 A+ 图（PREMIUM_APLUS / STANDARD_APLUS / PHONE_APLUS）— ③textgen 改写支线

把核心卖点转成 A+ 详情页版式图（带 Text on Image 文案与多模块版式）。三个子类型走同一份模板与同一支线，仅默认比例和版式意图不同。

> A+ 图与卖点图（`references/types/selling-point.md`）**共用同一份模板** `selling-point-aplus.txt`，靠 `{layoutInfo}` 版式意图区分。

## 子类型与默认比例

| type | 名称 | 默认比例 | 版式意图（脚本生成） |
|------|------|---------|---------------------|
| PREMIUM_APLUS | 高级A+图 | 1464:600 | 高级A+·{layout}点多模块版式 |
| STANDARD_APLUS | 普通A+图 | 970:600 | 普通A+·{layout}点多模块版式 |
| PHONE_APLUS | 手机A+图 | 600:450 | （手机A+不附加额外版式意图，layoutInfo 为空） |

## 适用场景

| 场景 | 说明 |
|------|------|
| 详情页多模块版式 | 把核心卖点转成带文案与视觉构图的 A+ 详情页版式图 |
| 高级 / 普通 / 手机 A+ | 按子类型选默认比例，按 layout 标签组织模块版式 |

## 类型特有参数

占位符映射同卖点图：`point`→`{customer_keywords}`、`layout`→`{layoutInfo}`、`brandGeneJson`→`{brandKey}`、`imageDesc`→`{customSetting}`、`language`→`{language}`、`salesRegion`→`{salesRegion}`、`platform`→`{platform}`、`ratio`→`{Ratio}`。`{infringingWords}` 由脚本填空串。

## 步骤 2 差异：③textgen 改写（过敏感词，按子类生成版式意图）

- 走 **③textgen 改写**支线：用 `scripts/build_textgen_params.py` 读模板 → 按子类型填占位符（含按子类生成的 `{layoutInfo}` 版式意图，null 替换成空串）→ 产出 textgen 参数文件（`model=GEM_3_1_PRO`、`thinkingLevel=high`）。
- **过敏感词**：脚本在 prompt 末尾自动追加敏感词规避指令。

```bash
DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)
BRAND_GENE_FILE='<S1 save_brand_gene.py 落盘的 brandGeneJson 绝对路径>'
python scripts/build_textgen_params.py \
  --type PREMIUM_APLUS \
  --image-urls '<步骤1的URL JSON数组>' \
  --point '<核心卖点>' \
  --layout '<概览/功能/品质/场景>' \
  --brand-gene-file "$BRAND_GENE_FILE" \
  --image-desc '<用户自定义，可空>' \
  --language '<语言>' --sales-region '<地区>' --platform '<平台>' \
  --ratio '1464:600' \
  --out "$DATADIR/textgen_aplus.json"
```
> `--type` 取 `PREMIUM_APLUS` / `STANDARD_APLUS` / `PHONE_APLUS`，`--ratio` 取对应默认比例（或用户/A+图比例）。

> **运行时模板唯一来源**：`scripts/templates/selling-point-aplus.txt`（与卖点图共用），运营更新直接改该 .txt。

随后按本 skill **SKILL.md「步骤2 → ③textgen 改写支线」给出的标准链式调用**执行：把上面产出的 `$DATADIR/textgen_aplus.json` 作为 `<textgen_params.json>`，经 `--stdin --content-only` 取出单行 prompt → `jq` 内联进下游 imagegen 参数 → 进入共享流水线步骤 3 出图（下游自动把 `⏎` 还原为换行符）。**具体命令以 SKILL.md 步骤2 为准，此处不重复。**

## 执行自检

- [ ] 步骤 1 所有参考图都为公开可访问 URL，否则报错而非带空图调 `linkfox-aigc-textgen`
- [ ] 步骤 2 占位符全部被真实值或空串替换，最终 prompt 里无残留 `{xxx}`，且末尾已追加敏感词规避指令
- [ ] `--type` 与子类型一致，`--ratio` 为该子类默认比例或用户/A+图比例
- [ ] 服装款式、颜色、细节与参考图 100% 一致；产品颜色与输入图强关联，未随意增色
- [ ] Text on Image 仅用 `language` 一种语种，文案合规、无违禁 / 侵权词，未出现色号 / fontStyle / "headline" 等字样
- [ ] 版式严格遵循 `{layoutInfo}` 结构；背景非纯白、配色以 brandColor 为准
- [ ] 步骤 3 `provider` 已按入参透传、`outputNum=1`、`aspectRatio=ratio` 已原样透传给 imagegen

## 已知局限

- 卖点图 / A+ 共用字典模板，靠 `{layoutInfo}` 区分；版式意图填错会导致版式串型。
- 强依赖 `linkfox-aigc-textgen`（`GEM_3_1_PRO`）对卖点的视觉化与版式扩写；改写质量影响最终构图。
- 敏感词规避以"prompt 末尾追加规避指令、由文本模型自审"实现，无确定性词库兜底，合规仍需上游或人工把关。
- 多张参考图时由模型自行判断主体服饰角色，复杂组合下可能误判主图。
