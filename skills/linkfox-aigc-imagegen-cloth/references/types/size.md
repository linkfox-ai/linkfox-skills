# 服饰尺码图（SIZE）— 两阶段：阶段1=③textgen 前置分析 + 阶段2=②占位符直出

把一件服饰转成一张信息精准、背景高级、含双单位尺码数据的电商尺码图，按版式输出"三联画身材对比"或"尺码表 + 测量指南"两种布局。

> ⚠ 与其它服饰类型的关键差异：尺码图是**两阶段**链路。
> - **阶段 1（前置分析，③textgen）**：用 `linkfox-aigc-textgen`（`GEM_3_1_PRO`/`medium`）把参考图读成结构化的【服装基础档案】+【温馨提示】文本（`analysis_result`），不出图、无占位符、**不过敏感词**。
> - **阶段 2（出图，②占位符直出）**：按 `layout` 选模板填占位符 → 末尾追加敏感词规避指令 → 出图，**不再调 textgen 改写**。

## 适用场景

| 场景 | 说明 |
|------|------|
| 智能尺码表生成 | 用户只给一张服饰图、没给尺码数据，需要按品类自动生成符合行业逻辑的 S/M/L/XL 尺码表 |
| 模特身材对比（三版） | 需要"偏瘦 / 标准 / 偏胖"三位欧美模特并排、各带身材数据的三联画尺码图 |
| 测量指南型（普通） | 需要尺码表 + 模特参考 + "如何测量"线稿图示 + 图标化温馨提示四模块的综合尺码图 |
| 成人 / 儿童自适配 | 童装自动切换为儿童模特与儿童身材数据逻辑，成人装走成人逻辑 |

## 类型特有参数

| 参数 | 占位符 | 阶段 | 说明 |
|------|--------|------|------|
| `imageUrls` | — | 阶段1+2 | 服饰参考图，阶段1 textgen 读图分析、阶段2 出图都用 |
| `layout` | — | 阶段2 | 版式，仅限 `普通` / `三版`（后端判定值 `三栏` 等同 `三版`）。决定阶段2 选哪份模板 |
| `brandGeneJson` | `{brandKey}` | 阶段2 | 品牌基因，控背景配色 / 字体；严禁 `brandName` 影响图片内容 |
| `language` | `{language}` | 阶段2 | 图片内文字语言；未指定默认英文 |
| （阶段1产出） | `{analysis_result}` | 阶段2 | 阶段1 前置分析结果，用 `--analysis-file` 注入，避免大文本经 shell |

- 默认比例 1:1。尺码图模板**不消费** `point`（与卖点无关）、`customSetting`（画面固定为尺码示意）、`salesRegion` / `platform`（模特恒定为欧美面孔，由模板内置规则决定）。
- 任意为 null 的入参替换成空串 `""`，避免占位符残留。

## 步骤 2 差异：两阶段执行

### 阶段 1：前置分析（③textgen，无占位符，不过敏感词）

用 `scripts/build_textgen_params.py` 取前置分析模板（无占位符）→ 产出 textgen 参数文件（`model=GEM_3_1_PRO`、`thinkingLevel=medium`），按 textgen SKILL.md 链式调用方式用 `--stdin --content-only` 执行，把单行 `analysis_result`（换行已压平为 `⏎`）**重定向保存到一个临时文件**供阶段 2 `--analysis-file` 注入（`⏎` 占位符会随阶段2 prompt 传到 imagegen 时被自动还原为换行符）。

```bash
DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)
python scripts/build_textgen_params.py \
  --type SIZE_PRE_ANALYSIS \
  --image-urls '<步骤1的URL JSON数组>' \
  --out "$DATADIR/textgen_size_pre.json"

python <textgen根目录>/scripts/aigc_textgen.py --stdin --content-only \
  < "$DATADIR/textgen_size_pre.json" > "$DATADIR/size_analysis.txt"
```
> `<textgen根目录>` 通过 `skill:linkfox-aigc-textgen` 解析其 SKILL.md 所在目录的绝对路径取得。

> **阶段1 运行时模板唯一来源**：`scripts/templates/size-pre-analysis.txt`，运营更新直接改该 .txt。

### 阶段 2：出图（②占位符直出，末尾追加敏感词规避指令）

用 `scripts/build_imagegen_prompt.py` 按 `layout` 选模板 → 填 `{brandKey}`/`{language}`/`{analysis_result}`（`analysis_result` 用 `--analysis-file` 注入）→ 脚本自动在末尾追加敏感词规避指令 → 产出最终 imagegen prompt 参数文件。**不再调 textgen 改写。**

```bash
DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)
BRAND_GENE_FILE='<S1 save_brand_gene.py 落盘的 brandGeneJson 绝对路径>'
python scripts/build_imagegen_prompt.py \
  --type SIZE \
  --layout '<普通|三版>' \
  --image-urls '<步骤1的URL JSON数组>' \
  --brand-gene-file "$BRAND_GENE_FILE" \
  --language '<语言>' \
  --analysis-file "$DATADIR/size_analysis.txt" \
  --out "$DATADIR/imagegen_size.json"
```
模板按 layout 选择：
- `普通` → `scripts/templates/size-common.txt`（尺码表 / 模特 / 测量指南 / 智能提示四模块）
- `三版`（后端 `三栏`）→ `scripts/templates/size-three-column.txt`（偏瘦 / 标准 / 偏胖三联画身材对比）

> **阶段2 运行时模板唯一来源**：`scripts/templates/size-common.txt`（普通）/ `size-three-column.txt`（三版），运营更新直接改对应 .txt。

随后将参数文件中的 `prompt` / `imageUrls` 连同 `provider` / `aspectRatio=ratio` / `resolution` / `outputNum=1` 送共享流水线步骤 3 出图。

## 执行自检

- [ ] 步骤 1 所有参考图都为公开可访问 URL，否则报错而非带空图调 textgen
- [ ] 阶段1 用 `GEM_3_1_PRO`，`analysis_result` 非空且为结构化【服装基础档案】+【温馨提示】，无闲聊式语言
- [ ] 阶段2 模板选用与 `layout` 匹配：`三版` 走三联画模板；`普通` 走四模块模板
- [ ] 阶段2 占位符（`{brandKey}`/`{language}`/`{analysis_result}`）全部被真实值或空串替换，最终 prompt 里无残留 `{xxx}`，且末尾已追加敏感词规避指令
- [ ] 图片内文案合规、无违禁 / 侵权词
- [ ] 尺码表数值同时标注 **cm 和 in 双单位**（换算 1 in = 2.54 cm）
- [ ] 图片内文字仅用 `language` 一种语种；背景非纯白（#FFFFFF），整体配色高级
- [ ] 三版：三位模特为偏瘦 / 标准 / 偏胖、外貌各异、年龄段与性别统一的欧美模特；普通：尺码表 + 模特参考 + 测量指南线稿 + 图标化提示四模块齐全
- [ ] 童装自动切换为儿童模特与儿童身材数据；模特所穿服装与参考图 100% 一致
- [ ] 步骤 3 `provider` 已按入参透传、`outputNum=1`、`aspectRatio=ratio`（默认 1:1）已原样透传给 imagegen

## 已知局限

- 双阶段链路：阶段 1 的 `analysis_result` 质量直接决定阶段 2 尺码表的品类判定与提示文案；前置分析识别错误（如把童装认成成人装）会传导到模特年龄与尺码逻辑。
- `layout` 取值在套图层用语为 `普通` / `三版`，后端按 `request.getType()=="三栏"` 判定走三联画模板——`三版` 与后端 `三栏` 为同一含义，传值需对齐，否则会落到 `普通`（Common）模板。
- 用户未提供尺码数据时由模型按行业逻辑"智能生成"尺码表，数值仅供参考、非真实测量；用户提供了具体数据时模板会直接采用、严禁编造。
- 模特恒定为欧美面孔（模板内置规则），不随 `salesRegion` 变化。
- **敏感词规避降级**：阶段 2 不经文本模型改写，已降级为「在送 imagegen 的最终 prompt 末尾追加规避指令、由出图模型自审」。代价：无确定性词库兜底，词库级违禁 / 侵权词可能漏过，合规仍需上游或人工把关。
