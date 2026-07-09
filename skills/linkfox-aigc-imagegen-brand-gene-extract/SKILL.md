---
name: linkfox-aigc-imagegen-brand-gene-extract
description: 品牌基因样式提取原子技能。根据商品图片与用户品牌基因参数（主色、字体、平台、地区、语言），提取统一的品牌视觉语言（Brand DNA），输出结构化 brandGeneJson 供下游原子技能消费。品牌基因提取、brand gene extract、brand DNA、品牌视觉定义、品牌调性提取、brand style extraction、visual identity extraction。被套图编排层（linkfox-aigc-imagegen-cloth / product 套图编排路径）在步骤三中调用；当用户说"提取品牌基因"、"定义品牌风格"、"brand gene"、"品牌视觉"时触发。
---

# 品牌基因样式提取（Brand Gene Extract）

根据商品图片与用户品牌基因参数，提取统一的品牌视觉语言（Brand DNA），输出结构化 JSON 供下游原子技能消费。

---

## 适用场景

| 场景 | 说明 |
|------|------|
| 套图编排调用 | 被 `linkfox-aigc-imagegen-cloth` / `linkfox-aigc-imagegen-product`（套图编排路径）在步骤三中调用，为整套图定义统一视觉基因 |
| 品牌基因变更 | 用户修改主色调/字体/平台/地区后重新提取 |
| 首次品牌定义 | 上下文中尚无品牌基因结果时，首次提取 |

## 不适用

- 已有完整 brandGeneJson 且无需变更时（直接复用，不重复调用本 skill）
- 纯背景替换/抠图/合成等图片编辑操作
- 非视觉类的品牌故事文案

---

## 输入参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| images | list[image] | — | 用户上传的商品图片列表（至少 1 张），用于分析商品色彩与气质 |
| brandKey | object | — | 用户输入的品牌基因信息（见下方字段说明） |

### brandKey 字段说明

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| brandColor | string | "" | 品牌主色（HEX 值），非空时直接使用，为空时自动提取 |
| fontStyle | string | "" | 字体风格，非空时直接使用，为空时自动提取 |
| brandName | string | "" | 品牌名称，用于品牌植入策略 |
| language | string | "英文" | 目标市场语言 |
| platform | string | "亚马逊" | 发布平台（Amazon/TikTok/Shopee 等） |
| salesRegion | string | "美国" | 销售地区/国家 |

---

## 流水线步骤

### 步骤 1：参数解析与决策路由

- **输入**：`brandKey`、`images`
- **操作**：
  1. 解析 `brandKey` 中各字段值
  2. **主色决策**：`brandColor` 非空 → 直接采用；为空 → 标记为"自动提取"
  3. **字体决策**：`fontStyle` 非空 → 直接采用；为空 → 标记为"自动提取"
  4. **填充默认值**：`language` 空则默认"英文"；`platform` 空则默认"亚马逊"；`salesRegion` 空则默认"美国"
  5. 将 `images` 转为可访问 URL 列表（`imageUrlList`），供步骤 3 传入 textgen
- **输出**：决策路由表（哪些字段用户给定、哪些需自动提取）+ `imageUrlList`
- **用途**：指导步骤 2 的 prompt 组装

### 步骤 2：组装品牌视觉基因提取 prompt

- **输入**：步骤 1 的决策路由表、`brandKey` 全部字段
- **操作**：将以下品牌视觉基因提取指令与 `brandKey` 参数拼装为完整 prompt，传入步骤 3：

  **角色**：你是顶尖品牌视觉专家和创意总监，基于商品图片与参数，构建一套统一的视觉语言，确保品牌在不同场景下的高度一致性。

  **A. 统一视觉主题（UNIFIED_VISUAL_THEME）**

  1. **Brand Color（品牌主色）**：
     - 定义一个具有"世界观"的核心色，而不仅仅是色板
     - 唯一性：全案只能定义 1 个核心 HEX 色值
     - 来源：必须考虑商品本身的颜色，具备极高审美
     - ⚠️ **黑白灰协议（CRITICAL）**：除非商品本身为黑白灰，否则禁止使用黑白灰作为主色，必须输出具体色值（如 #EAF86C）

  2. **背景策略（Background Strategy）**：必须**完整输出以下 4 个子字段，缺一不可**，每个都给出具体内容（不得留空、不得只写字段名）：
     - **背景策略-风格定义**：根据 `salesRegion` 做文化本土化的整体环境风格。追求 100% 摄影级写实环境，严禁分层背景图层感，侧重生活方式与情感共鸣。
       示例：`"现代北欧极简家居，原木与暖白色调，落地窗自然采光，符合美国中产审美"`
     - **背景策略-场景关键词**：逗号分隔的具体场景/道具关键词。
       示例：`"原木长桌, 亚麻桌布, 绿植, 陶瓷器皿, 晨光"`
     - **背景策略-光影**：明确的光线方向、色温与氛围（**这是必填字段，最易被漏，务必输出**）。
       示例：`"柔和自然侧光，暖色温 4000K，营造清晨慵懒氛围，轻微长投影增强立体感"`
     - **Brand Injection（品牌植入）**：品牌主色 / Logo / 标识元素如何自然融入场景（**这是必填字段，最易被漏，务必输出**）。
       示例：`"品牌主色作为抱枕/标签点缀色出现，Logo 以低饱和压印形式出现在道具上，不喧宾夺主"`

  **B. 绝对字体锁定（LOCKED_TYPOGRAPHY）**

  1. **字体风格**：从以下库中锁定唯一一种风格：
     - 几何无衬线体：Jost, League Spartan, Montserrat, Manrope, Outfit
     - 硬朗无衬线体：Bebas Neue, Oswald, Barlow Condensed, Anton, Fjalla One
     - 经典优雅衬线体：Bodoni Moda, Playfair Display, Prata, Cormorant Garamond, DM Serif Display
     - 圆润童趣字体：Nunito, Quicksand, Varela Round, Fredoka, Baloo 2
     - 俏皮手写风格: Pacifico, Permanent Marker, Amatic SC, Caveat, Luckiest Guy

  2. **颜色策略**：
     - 标题色（Heading Color）：必须使用品牌主色或反白色；当标题底部颜色是品牌主色或同色系时，自动触发"灵活反白"；其次考虑使用品牌主色同色系颜色（禁止接近黑色的颜色，颜色不能过深）
     - 正文色（Body Color）：与标题色区分，确保可读性
     - ⚠️ **输出格式注意**：颜色策略输出格式为 `["Heading Color"：颜色值]` 和 `["Body color"：颜色值]`，这是颜色定义而非文本内容

  3. **灵活反白权限**：当使用深色背景或纯品牌色色块时，授权切换为哑光白（#FFFFFF）文本

  4. **排版限制**：统一为非斜体（Non-italic），行距适中（standard leading）

  **输出要求**：严格按照下方「输出格式」输出完整 JSON，禁止输出任何解释性文字或代码块标记。

- **输出**：完整的 textgen prompt 字符串
- **用途**：作为步骤 3 的 prompt 输入

### 步骤 3：调用 linkfox-aigc-textgen 执行视觉推理

- **输入**：步骤 2 的 prompt、步骤 1 的 `imageUrlList`
- **操作**：按 `linkfox-aigc-textgen` SKILL.md 的调用方式调用 textgen 执行视觉推理。本步骤产出的内容要**回读进上下文做字段提取**（步骤 4），**不**链式拼进下游出图，因此用 textgen 的**默认模式**（不是 `--content-only`）：把下列字段写成 JSON 参数文件，经 `--stdin` 传入运行，再解析 stdout。`<textgen根目录>` 通过 `skill:linkfox-aigc-textgen` 解析其 SKILL.md 所在目录的绝对路径取得；`<本skill根目录>` = 本 SKILL.md 所在目录的绝对路径。
  > ⚠️ **中间参数文件落到会话 `data/` 目录**。先取目录：
  > ```bash
  > DATADIR=$(python <本skill根目录>/scripts/save_brand_gene.py --datadir)
  > ```
  > ⚠️ **构造 `brand_gene_params.json` 必须用 Write 工具**写到 `$DATADIR/brand_gene_params.json`（prompt 含引号、反斜杠等特殊字符，shell heredoc 内嵌 JSON 易解析失败）。若走命令行生成，只用 `python -c` 配合 `json.dumps`，不要手拼 JSON 字符串。
  ```bash
  python <textgen根目录>/scripts/aigc_textgen.py --stdin < "$DATADIR/brand_gene_params.json"
  ```
  JSON 参数文件包含以下字段：
  - `prompt`：步骤 2 组装的品牌视觉基因提取指令（含「输出格式」要求）
  - `imageUrls`：步骤 1 输出的 `imageUrlList`
  - `model`：`GEM_3_1_PRO`（需要视觉理解与复杂推理能力）
  - `thinkingLevel`：`high`
- **输出**：解析 textgen stdout 得到 `content`（解析方式按 `linkfox-aigc-textgen` SKILL.md 的「输出契约」）。
- **用途**：作为步骤 4 的组装原料

### 步骤 4：组装 brandGeneJson

- **输入**：步骤 3 解析出的 `content`（换行可能为 `⏎` 占位符，提取前先还原为换行符）
- **操作**：从该 `content` 中提取品牌视觉基因各字段，严格按照下方「输出格式」自行组装为 `brandGeneJson`
- **缺失字段兜底（强制）**：组装后**必须逐一核对**「输出格式」中的全部字段是否齐全。若模型输出遗漏了某字段（实测最易漏 `背景策略-光影` 与 `Brand Injection（品牌植入）`），**不得直接交付残缺 JSON**，须按以下顺序兜底补齐：
  1. 优先从 `content` 其余文字中归纳推断该字段的合理值；
  2. 无可推断内容时，结合已确定的主色 / 风格定义生成一句与整体调性一致的兜底描述（如光影按"自然柔和侧光、暖色温、增强立体感"，品牌植入按"主色作点缀、Logo 低调融入道具"）。
  最终 `brandGeneJson` 必须字段齐全，**禁止**出现缺字段或字段值为空串。
- **输出**：`brandGeneJson`（长度为 1 的 JSON 列表，字段齐全）
- **落盘（强制）**：组装完成后**必须**写入会话目录并保留路径供下游复用：
  1. 用 Write 工具将 `brandGeneJson` 写到 `$DATADIR/brand_gene_assembled.json`（`DATADIR` 同步骤 3）；或
  2. 运行落盘脚本（推荐，自动注册 `_meta.json`）：
     ```bash
     python <本skill根目录>/scripts/save_brand_gene.py "$DATADIR/brand_gene_assembled.json"
     ```
     stdout 会打印 `Saved full response: <绝对路径> (<N> bytes)`——**将该绝对路径记入上下文**，后续 S3 套图编排通过 `--brand-gene-file <绝对路径>` 或 manifest 的 `brand_gene_json` 消费。
- **用途**：透传给下游出图链路（`linkfox-aigc-imagegen-cloth` 的种草图/卖点图/A+图 等类型 / `linkfox-aigc-imagegen-product` 等）作为 `brandGeneJson` 参数

---

## 产物落盘

| 产物 | 目录 | 说明 |
|------|------|------|
| `brand_gene_params.json` | `<session>/data/` | textgen 入参（步骤 3 中间文件） |
| `brandGeneJson` 最终结果 | `<session>/data/linkfox-aigc-imagegen-brand-gene-extract-<ts>.json` | 经 `save_brand_gene.py` 落盘，供套图 S3 与单张 `--brand-gene-file` 复用 |

路径协议：`<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`（`<session>` 取自 `SESSION_ID`），与仓库 `CLAUDE.md`「输出文件位置」一致。

---

## 核心规则

### A. 主色和字体逻辑

- 如果 `brandColor` 有值 → 输出 JSON 中 "brandColor (品牌主色)" 直接用该值
- 如果 `fontStyle` 有值 → 输出 JSON 中 "字体风格" 直接用该值
- 如果哪个值为空 → 该值用核心变量里的规则来自动提取

### B. 其他值逻辑

"背景策略-风格定义"、"颜色策略-Heading" 等字段，默认都用核心变量的规则来获取，不受 brandKey 中 brandColor/fontStyle 的透传影响。

---

## 输出格式

严格按照以下 JSON 格式输出，输出为长度为 1 的列表：

```json
[
  {
    "brandColor": {
      "brandColor (品牌主色)": "颜色名称与HEX值",
      "背景策略-风格定义": "基于 salesRegion 的风格描述",
      "背景策略-场景关键词": "关键词1, 关键词2, ...",
      "背景策略-光影": "光影氛围描述",
      "Brand Injection（品牌植入）": "品牌元素如何植入场景"
    },
    "fontStyle": {
      "字体策略": "选定的字体家族名称",
      "字体风格": "选定的具体字体名称",
      "颜色策略-Heading": "[\"Heading Color\"：颜色值/反白逻辑]",
      "颜色策略-Body/Sub": "[\"Body color\"：颜色值]",
      "灵活反白": "You are authorized to switch to Matte White (#FFFFFF) text whenever using a dark background or a solid brand-color panel.",
      "排版": "Non-italic, standard leading"
    }
  }
]
```

---

## 错误处理

| 情况 | 处理 |
|------|------|
| images 为空 | 停止执行，提示用户上传至少 1 张商品图片 |
| brandKey 完全为空 | 所有字段按默认值填充（salesRegion=美国、language=英文、platform=亚马逊），主色与字体走自动提取 |
| 商品为纯黑白灰且无法提取彩色主色 | 允许使用黑白灰作为主色（黑白灰协议的唯一豁免条件） |

---

## 调用方式

本 skill 由套图编排层在步骤三中调用，调用时机：

1. **首次调用**：上下文中没有进行过品牌基因样式提取时
2. **重新调用**：用户明确要求修改品牌基因（场景 G）时

复用规则：同一上下文中提取结果可复用，无需重复调用。

---

## 已知局限

- 品牌主色提取基于 `GEM_3_1_PRO` 对商品图片的视觉理解，可能与专业设计师判断有偏差
- 字体风格限定在预设的 5 类 25 款字体中，无法选择库外字体
- 背景策略的文化本土化依赖 salesRegion 的语义理解，非结构化地域数据库
- 品牌基因 JSON 必须经 `save_brand_gene.py` 落盘到会话 `data/`，不可仅存于对话上下文
- 依赖 `linkfox-aigc-textgen` skill 可用；若 textgen 调用失败，品牌基因提取无法完成
