# 服饰种草图（SCENE）— ③textgen 改写支线

把一件服饰穿到真人模特身上，生成一张 Ins 时尚博主风格、服装完整占画面 60% 以上、具备大片感与种草感染力的场景图。自动匹配 Vibe（Old money / Y2K / Clean girl / 街拍 editorial 等）、富表现力的姿势与多样化机位。

> ⚠ 与模特图（MODEL_IMAGE，干净明亮的标准电商上身展示）的关键差异：种草图主打 Instagram 时尚博主风格大片，氛围感与社交媒体感染力优先。

## 适用场景

| 场景 | 说明 |
|------|------|
| 单品种草大片 | 用户给服饰图，想要一张"真人穿着该商品"的 Ins 博主风时尚写真 / 街拍 / 棚拍大片 |
| 卖点场景化 | 把核心营销卖点（面料、版型、搭配场景等）转成具体生活化穿搭画面，强化种草感 |
| 指定场景出图 | 用户描述了最佳场景（如海边度假、法式乡村、都市街头），按该画面内容生成（仍保持 Ins 风格） |
| 受众自适应 | 由模板按服装自动判断目标人群 / 年龄（童装 vs 成人）/ 性别，匹配对应模特与场景 |

## 类型特有参数

| 参数 | 占位符 | 说明 |
|------|--------|------|
| `point` | `{selling_points}` | 核心营销卖点（中文一段详细描述），必填 |
| `imageDesc` | `{image_desc}` | 最佳场景 / 画面内容（用户自定义场景）；为空时由模板自由构思多样场景 |

- **本模板只消费 `{selling_points}` 与 `{image_desc}` 两个占位符**。`language` / `salesRegion` / `platform` / `brandGeneJson` 等不写进本链路 prompt——模特人种 / 年龄 / 性别、场景 Vibe 均由模板内置工作流自动推导（未指定默认欧美模特）。
- 默认比例 1:1，比例走入参（`useRatio=true`）。

## 步骤 2 差异：③textgen 改写

- 走 **③textgen 改写**支线：用 `scripts/build_textgen_params.py` 读模板 → 填 `{selling_points}`/`{image_desc}`（null 替换成空串）→ 产出 textgen 参数文件（`model=GEM_3_FLASH`、`thinkingLevel=low`）。
- **不过敏感词**——种草图不产出 Text on Image 文案，敏感词风险低，省一次调用换更短链路。

```bash
DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)
python scripts/build_textgen_params.py \
  --type SCENE \
  --image-urls '<步骤1的URL JSON数组>' \
  --point '<核心卖点>' \
  --image-desc '<最佳场景，可空>' \
  --out "$DATADIR/textgen_scene.json"
```
> **运行时模板唯一来源**：`scripts/templates/scene.txt`，运营更新直接改该 .txt。

随后按本 skill **SKILL.md「步骤2 → ③textgen 改写支线」给出的标准链式调用**执行：把上面产出的 `$DATADIR/textgen_scene.json` 作为 `<textgen_params.json>`，经 `--stdin --content-only` 取出单行 prompt → `jq` 内联进下游 imagegen 参数 → 进入共享流水线步骤 3 出图（下游自动把 `⏎` 还原为换行符）。**具体命令以 SKILL.md 步骤2 为准，此处不重复。**

## 执行自检

- [ ] 步骤 1 所有参考图都为公开可访问 URL，否则报错而非带空图调 `linkfox-aigc-textgen`
- [ ] 步骤 2 的 `{selling_points}` / `{image_desc}` 已被真实值或空串替换，最终 prompt 里无残留 `{xxx}`
- [ ] 服装款式、颜色、细节与参考图 100% 一致，未被改款 / 改色
- [ ] 服装完整呈现且占画面 60% 以上，搭配单品（外套 / 罩衫 / 围巾 / 包袋等）未遮挡主体服装关键设计
- [ ] 人货物理逻辑一致（成人穿成人装 / 儿童穿童装），性别匹配
- [ ] 画面为 Ins 时尚博主风格大片：姿势富表现力（站姿 / 动态优先，避免坐姿）、机位多样、氛围感到位
- [ ] 无 iPhone / 品牌 logo、无黑边、未遮挡衣服主体；除非 `imageDesc` 指定，否则未使用黑人模特
- [ ] 步骤 3 `provider` 已按入参透传、`outputNum=1`、`aspectRatio=ratio` 已原样透传给 imagegen

## 已知局限

- 强依赖 `linkfox-aigc-textgen`（`GEM_3_FLASH`）对**目标人群 / 年龄（童装 vs 成人）/ 性别**与服装款式的判定；判定错误会直接传导到模特画像与场景构图。
- 模板只消费 `{selling_points}` 与 `{image_desc}`：`salesRegion` / `language` / `brandGeneJson` 等不接入本链路，市场化人种 / 品牌调性强控需改由 `imageDesc` 文字描述传入，否则默认欧美模特。
- 不做敏感词改写：若卖点 / 自定义场景含违禁内容，本链路不拦截，由上游或人工把关。
- 多张参考图时由模型自行判断主体服饰角色，复杂组合下可能误判主图。
- 本类型只做从服饰图"生成"种草大片，不做对已有模特图的换姿势 / 换动作裂变（模特裂变为独立能力，提示词由业务方上游构造，不读字典）。
