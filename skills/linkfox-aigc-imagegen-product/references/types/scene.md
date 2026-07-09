# SCENE 场景图

把一件实物商品放进真实使用场景里，生成一张比例自洽、贴合亚马逊品类视觉规范的场景类商品图。

## 适用场景

| 场景 | 说明 |
|------|------|
| 单品场景化 | 用户给商品白底图 / 实拍图，想要一张"商品在真实环境中被使用 / 陈列"的场景图 |
| 卖点可视化 | 把一个核心卖点转成具体生活化画面（如"防滑底座" → 厨房台面湿手取用场景） |
| 结构敏感品类 | 固定安装类（吸顶灯 / 门锁 / 龙头）需要 mounted 安装态与真实空间比例时 |

## 类型特有参数

| 参数 | 类型 | 默认 | 说明 | 占位符映射 |
|------|------|------|------|-----------|
| `point` | string | 必填 | 核心卖点（中文一段详细描述） | `{customer_keywords}` |
| `imageDesc` | string | "" | 画面内容 / 用户自定义场景 | `{customSetting}` |
| `brandGeneJson` | string | "" | 品牌基因 JSON（主色、字体、语言、平台、地区） | `{brandKey}` |
| `language` | string | 英文 | 文字语言，辅助推导模特人种 | `{language}` |
| `salesRegion` | string | 美国 | 销售国家/地区，决定模特人种与软装风格 | `{salesRegion}` |
| `platform` | string | 亚马逊 | 发布平台（Amazon / TikTok / Shopee），决定构图与合规 | `{platform}` |

> 字段映射规范：任意为 null 的入参都会被替换成空字符串 `""`，避免占位符残留在最终 prompt 里。

## 步骤 2：构造最终 prompt（辅助脚本构建参数 → textgen 改写）

- **输入**：`imageUrls`、`point`、`imageDesc`、`brandGeneJson`、`language`、`salesRegion`、`platform`
- **操作**：
  1. 先取会话 data 目录：
     ```bash
     DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)
     BRAND_GENE_FILE='<S1 save_brand_gene.py 落盘的 brandGeneJson 绝对路径，无则省略>'
     ```
  2. 使用 `scripts/build_textgen_params.py` 一条命令完成模板读取、占位符填充、JSON 参数文件写入（脚本自动选择模板 `scripts/templates/scene.txt`、设置 `model=GEM_3_FLASH`、`thinkingLevel=low`）。**禁止手动用 Write 工具构造 textgen 参数文件**。
     ```bash
     python scripts/build_textgen_params.py \
       --type SCENE \
       --image-urls '<imageUrls JSON 数组>' \
       --point '<point>' \
       --image-desc '<imageDesc>' \
       --brand-gene-file "$BRAND_GENE_FILE" \
       --language '<language>' \
       --sales-region '<salesRegion>' \
       --platform '<platform>' \
       --out "$DATADIR/textgen_scene.json"
     ```
     > 品牌基因也可用 `--brand-gene-json '<brandGeneJson>'` 代替 `--brand-gene-file`（短 JSON 时）；套图场景优先用 S1 落盘文件。
  3. 按本 skill **SKILL.md「步骤2」给出的标准链式调用**执行 textgen：把上面产出的 `$DATADIR/textgen_scene.json` 经 `--stdin --content-only` 取出单行 prompt，由模型完成品类识别、结构判定（TABLETOP / FIXTURE）、比例自检后吐出一条结构化英文 prompt（换行已压平为 `⏎`）。**具体命令以 SKILL.md 步骤2 为准，此处不重复。**
- 这一步**不做敏感词过滤**——场景图正文已含足够的几何/比例约束，且不产出 Text on Image 文案，敏感词风险低，省一次调用换更短链路。
- **输出**：取出的 prompt 即步骤 3 的来源，用 `jq` 内联拼进下游 imagegen 参数 JSON（下游自动把 `⏎` 还原为换行符）。

## 提示词正文（DictKey `agentProductScene`）

> **运行时模板唯一来源**：`scripts/templates/scene.txt`，运营更新直接改该 .txt。步骤 2 的 `build_textgen_params.py` 脚本自动读取该模板、填充占位符后交 `linkfox-aigc-textgen`（`model=GEM_3_FLASH`）生成最终 prompt。`entry_name=agentProductScene` 仅为来源标注（原后端 `ai_dict_def` 同名记录），**非运行时数据源**。

## 执行自检

- [ ] 步骤 1 所有参考图都为公开可访问 URL（本地路径已通过 linkfox-file-upload 上传），否则报错而非带空图调 `linkfox-aigc-textgen`
- [ ] 步骤 2 的占位符全部被真实值或空串替换，最终 prompt 里无残留 `{xxx}`
- [ ] 步骤 3 `provider` 已按入参透传给 imagegen、`outputNum=1`，`aspectRatio` 已按入参 `ratio` 透传给 `linkfox-aigc-imagegen`
- [ ] 产物为场景图（背景非纯白、产品比例真实、未被异常放大填满画面）
- [ ] FIXTURE 类产品处于 mounted / installed 安装态且保留完整空间比例
