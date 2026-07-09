# CLOSE_UP 特写图

把一件实物商品的关键区域（材质、纹理、光泽、工艺、卖点细节）放大成一张局部占比高、质感突出、贴合亚马逊品类视觉规范的特写商品图。

## 适用场景

| 场景 | 说明 |
|------|------|
| 材质质感特写 | 用户给商品白底图 / 实拍图，想要一张突出材质（金属拉丝 / 皮革缝线 / 宝石光泽 / 织物纹理）的细节大图 |
| 卖点细节可视化 | 把一个核心卖点对应到具体局部区域，用浅景深 + 高锐度把卖点拍清楚 |
| 工艺/结构细节 | 强调做工、接缝、按键、涂层等关键结构细节，局部占比 60%~80% 聚焦展示 |

## 类型特有参数

| 参数 | 类型 | 默认 | 说明 | 占位符映射 |
|------|------|------|------|-----------|
| `point` | string | 必填 | 核心卖点（中文一段详细描述），决定特写聚焦哪个区域 | `{customer_keywords}` |
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
  2. 使用 `scripts/build_textgen_params.py` 一条命令完成模板读取、占位符填充、JSON 参数文件写入（脚本自动选择模板 `scripts/templates/close-up.txt`、设置 `model=GEM_3_FLASH`、`thinkingLevel=low`）。**禁止手动用 Write 工具构造 textgen 参数文件**。
     ```bash
     python scripts/build_textgen_params.py \
       --type CLOSE_UP \
       --image-urls '<imageUrls JSON 数组>' \
       --point '<point>' \
       --image-desc '<imageDesc>' \
       --brand-gene-file "$BRAND_GENE_FILE" \
       --language '<language>' \
       --sales-region '<salesRegion>' \
       --platform '<platform>' \
       --out "$DATADIR/textgen_close_up.json"
     ```
     > 品牌基因也可用 `--brand-gene-json '<brandGeneJson>'` 代替 `--brand-gene-file`（短 JSON 时）；套图场景优先用 S1 落盘文件。
  3. 按本 skill **SKILL.md「步骤2」给出的标准链式调用**执行 textgen：把上面产出的 `$DATADIR/textgen_close_up.json` 经 `--stdin --content-only` 取出单行 prompt，由模型完成品类与风格基调识别、分离外观/用法信息、定位关键细节区域后吐出一条专注清晰细节展示的英文 prompt（换行已压平为 `⏎`）。**具体命令以 SKILL.md 步骤2 为准，此处不重复。**
- 这一步**不做敏感词过滤**——特写图正文不产出 Text on Image 文案，敏感词风险低，省一次调用换更短链路。
- **输出**：取出的 prompt 即步骤 3 的来源，用 `jq` 内联拼进下游 imagegen 参数 JSON（下游自动把 `⏎` 还原为换行符）。

## 提示词正文（DictKey `agentProductCloseUp`）

> **运行时模板唯一来源**：`scripts/templates/close-up.txt`，运营更新直接改该 .txt。步骤 2 的 `build_textgen_params.py` 脚本自动读取该模板、填充占位符后交 `linkfox-aigc-textgen`（`model=GEM_3_FLASH`）生成最终 prompt。`entry_name=agentProductCloseUp` 仅为来源标注（原后端 `ai_dict_def` 同名记录），**非运行时数据源**。

## 执行自检

- [ ] 步骤 1 所有参考图都为公开可访问 URL（本地路径已通过 linkfox-file-upload 上传），否则报错而非带空图调 `linkfox-aigc-textgen`
- [ ] 步骤 2 的占位符全部被真实值或空串替换，最终 prompt 里无残留 `{xxx}`
- [ ] 步骤 3 `provider` 已按入参透传给 imagegen、`outputNum=1`，`aspectRatio` 已按入参 `ratio` 原样透传给 `linkfox-aigc-imagegen`
- [ ] 产物为特写图（局部区域占比约 60%~80%、浅景深、高锐度，背景非纯白且不抢焦点）
- [ ] 聚焦区域与 `point` 卖点对应，关键质感（材质 / 纹理 / 光泽 / 工艺）清晰可见
- [ ] 产品外观、颜色、形态与参考图一致，未增删原图不存在的元素、未新增文字设计
