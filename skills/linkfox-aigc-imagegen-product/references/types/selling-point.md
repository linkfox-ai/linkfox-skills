# SELLING_POINT 卖点图

把一个核心卖点转成一张带图片内文案（Text on Image）、版式与品牌调性自洽的卖点图。

## 适用场景

| 场景 | 说明 |
|------|------|
| 卖点版式化 | 用户给商品图 + 一句卖点，想要一张"卖点 + 文案 + 版式构图"的成品图 |
| 多维度卖点裂变 | 围绕同一组 `customer_keywords` 按概览 / 功能 / 品质 / 场景做不同版式的卖点表达 |
| 品牌调性统一 | 按 `brandGeneJson` 的主色 / 字体风格，让卖点图与整套视觉保持一致 |

## 类型特有参数

| 参数 | 类型 | 默认 | 说明 | 占位符映射 |
|------|------|------|------|-----------|
| `point` | string | 必填 | 核心卖点（中文一段详细描述） | `{customer_keywords}` |
| `layout` | string | 概览 | 版型标签，仅限 概览/功能/品质/场景 → 映射 tagId（概览=187/功能=188/品质=189/场景=190） | `{layoutInfo}`（版式意图说明） |
| `imageDesc` | string | "" | 画面内容 / 用户自定义 | `{customSetting}` |
| `brandGeneJson` | string | "" | 品牌基因 JSON（主色 brandColor、字体 fontStyle、语言、平台、地区） | `{brandKey}` |
| `language` | string | 英文 | 图片内文案（Text on Image）语言 | `{language}` |
| `salesRegion` | string | 美国 | 销售国家/地区，决定模特人种与场景风格 | `{salesRegion}` |
| `platform` | string | 亚马逊 | 发布平台（Amazon / TikTok / Shopee），决定构图与合规 | `{platform}` |
| `ratio` | string | 1:1 | 图片比例 → 既填充 `{Ratio}` 写进 prompt 正文，也作为 `aspectRatio` 原样透传给 imagegen | `{Ratio}` |

> `{infringingWords}`（侵权词）为预留位，本链路恒填 `""`。任意为 null 的入参替换成空串 `""`。

## 步骤 2：构造最终 prompt（辅助脚本构建参数 → textgen 改写）

- **输入**：`imageUrls`、`point`、`layout`、`imageDesc`、`brandGeneJson`、`language`、`salesRegion`、`platform`、`ratio`
- **操作**：
  1. 先取会话 data 目录：
     ```bash
     DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)
     BRAND_GENE_FILE='<S1 save_brand_gene.py 落盘的 brandGeneJson 绝对路径>'
     ```
  2. 使用 `scripts/build_textgen_params.py` 一条命令完成模板读取、版式意图生成、占位符填充、敏感词规避指令追加、JSON 参数文件写入（脚本自动选择模板 `scripts/templates/selling-point-aplus.txt`、设置 `model=GEM_3_1_PRO`、`thinkingLevel=high`、追加敏感词规避指令）。**禁止手动用 Write 工具构造 textgen 参数文件**。
     ```bash
     python scripts/build_textgen_params.py \
       --type SELLING_POINT \
       --image-urls '<imageUrls JSON 数组>' \
       --point '<point>' \
       --layout '<layout 标签>' \
       --image-desc '<imageDesc>' \
       --brand-gene-file "$BRAND_GENE_FILE" \
       --language '<language>' \
       --sales-region '<salesRegion>' \
       --platform '<platform>' \
       --ratio '<ratio>' \
       --out "$DATADIR/textgen_sp.json"
     ```
     > 品牌基因也可用 `--brand-gene-json '<brandGeneJson>'` 代替 `--brand-gene-file`（短 JSON 时）；套图场景优先用 S1 落盘文件。
     > `--layout` 传入标签（概览/功能/品质/场景），脚本自动生成卖点图版式意图说明（如「卖点图·功能点展示版式：按概览/功能/品质/场景之一组织模块」）。
  3. 按本 skill **SKILL.md「步骤2」给出的标准链式调用**执行 textgen：把上面产出的 `$DATADIR/textgen_sp.json` 经 `--stdin --content-only` 取出单行 prompt。卖点图带 Text on Image 文案，需强版式扩写与文案能力，使用高质量模型 `GEM_3_1_PRO`（换行已压平为 `⏎`）。**具体命令以 SKILL.md 步骤2 为准，此处不重复。**
- **输出**：取出的 prompt 即步骤 3 的来源，用 `jq` 内联拼进下游 imagegen 参数 JSON（下游自动把 `⏎` 还原为换行符）。

## 提示词正文（DictKey `agentProductAPlusAndSellerPoint`）

> **运行时模板唯一来源**：`scripts/templates/selling-point-aplus.txt`，运营更新直接改该 .txt。步骤 2 的 `build_textgen_params.py` 脚本自动读取该模板、填充版式意图与占位符、追加敏感词规避指令后交 `linkfox-aigc-textgen`（`model=GEM_3_1_PRO`）生成最终 prompt。`entry_name=agentProductAPlusAndSellerPoint` 仅为来源标注（原后端 `ai_dict_def` 同名记录），**非运行时数据源**。

## 执行自检

- [ ] 步骤 1 所有参考图都为公开可访问 URL（本地路径已通过 linkfox-file-upload 上传），否则报错而非带空图调 `linkfox-aigc-textgen`
- [ ] `{layoutInfo}` 按 `layout` 标签（概览/功能/品质/场景）填了卖点图版式意图，未误填 A+ 版式
- [ ] 步骤 2 的占位符全部被真实值或空串替换，最终 prompt 里无残留 `{xxx}`
- [ ] textgen 用 `GEM_3_1_PRO`，prompt 末尾已追加敏感词规避指令，Text on Image 文案合规、无违禁/侵权词
- [ ] 图片内文案仅用 `language` 一种语种，未出现 `headline`/`sub-text`/色号/字体名等元信息字样
- [ ] 产品款式、颜色与参考图 100% 一致，`brandColor` 只控版式主色/背景、未染到产品本身
- [ ] 步骤 3 `provider` 已按入参透传给 imagegen、`outputNum=1`，`aspectRatio=ratio` 已原样透传给 imagegen，且与 prompt 内 `{Ratio}` 一致
