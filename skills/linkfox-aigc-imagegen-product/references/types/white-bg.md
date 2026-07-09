# WHITE_BG 白底图

把一件实物商品精修成符合亚马逊主图规范的纯白底图：背景纯白、主体居中、角度形态不变。

## 适用场景

| 场景 | 说明 |
|------|------|
| 商品白底主图 | 用户给实拍图 / 杂背景图，想要一张符合亚马逊主图规范的纯白底（RGB 255,255,255）精修图 |
| 主图合规精修 | 去除灰尘 / 划痕 / 指纹 / 杂线头，影棚布光，主体居中放大到画面 85%~90% 占比 |
| 批量去背标准化 | 多张商品图统一成纯白底主体图，逐张保持原拍摄角度与产品形态 |

## 类型特有参数

白底图入参极简，不消费卖点/画面描述/品牌基因等字段。

| 参数 | 说明 |
|------|------|
| `imageUrls` | 共享参数，见主 SKILL.md |
| `ratio` | 默认 `1:1` |
| `resolution` | 默认 `2K` |
| `provider` | 见主 SKILL.md |

> `point` / `imageDesc` / `brandGeneJson` / `language` / `salesRegion` / `platform` 等字段在本链路**均不参与**，即便上游传入也不会影响出图结果。

## 步骤 2：取静态模板作为最终 prompt

- **输入**：无（不依赖任何运行时业务字段）
- **操作**：**必须用 `scripts/build_imagegen_prompt.py --type WHITE_BG` 构建 imagegen 参数文件**，脚本会从下方「提示词正文」的 ```text``` 代码块**动态提取**正文作为最终 prompt：
  ```bash
  DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)
  python <本skill根目录>/scripts/build_imagegen_prompt.py \
    --type WHITE_BG \
    --image-urls '<步骤1的URL JSON数组>' \
    --out "$DATADIR/imagegen_white.json"
  ```
  本步骤只取正文直出：**不**做占位符替换 / textgen 改写 / 敏感词改写（正文已是完整的纯白底精修英文指令，无变量可填）。正文一律由脚本读取，**不要手动复制或经 shell 变量传递**（正文较长，易截断或转义出错）。套图场景下本类型由单任务驱动器 `scripts/run_one_task.py`（`type=WHITE_BG`）自动走同一提取逻辑。
- **输出**：`prompt`（送给步骤 3 的最终英文指令）

## 提示词正文（DictKey `agentProductWhiteBg`）

> `scripts/build_imagegen_prompt.py --type WHITE_BG` 会用正则**从下方 ```text``` 代码块动态提取**该正文作为最终 prompt，因此本代码块**即运行时数据源**——运营更新直接改此处正文即自动生效，**不要改动 ```text``` 围栏标记**（脚本依赖它定位正文）。`entry_name=agentProductWhiteBg` 仅为来源标注（原后端 `ai_dict_def` 同名记录），便于运营对照同步。

```text
##Product Refinement White Background Image AI Visual Designer Instructions
You are a top-level e-commerce graphic designer specializing in visual refinement of products across all categories.
Your main task: Strictly modify the input image to create a refined white background image according to the Workflow, without changing the shooting angle and shape of the main subject in the input image, adjusting its size ratio and refining the effect.
##Workflow
Remove the main part of the product. Adjust the image according to the "refinement strategy" and "Amazon background review standards".
Generate the final image strictly following the "high subject proportion strategy" and "output specifications".
Each rule in the Rule is a mandatory item that must be strictly followed. You must clearly define the requirements and implement them strictly. ##Rule
General Object Fidelity:
1.1 Visual Angle Locking Strategy:
  a. Strictly follow the input image, accurately identify and strictly maintain the shape, structure, and constituent parts of the product in the input image. No element additions or deletions are allowed, and the shape of the product body cannot be modified.
  b. Strictly follow the shooting angle and direction of the input image. The shooting angle and direction of the product body must not be changed. Only the refinement and adjustment of the main body proportion can be carried out in combination with the [Refinement Strategy] and [High Main Body Proportion Strategy].
  1.2 Color and Texture Synchronization Strategy: Automatically retain the original color palette and material attributes (metal texture, plastic texture, matte texture, or glossy texture). Based on the [Refinement Strategy], enhance the product texture, but the color and texture must be strictly consistent with the effect presented in the input image.
Angle Consistency: Maintain the camera perspective and direction completely consistent, without changing the shooting perspective of the product itself. The product body, except for being adjusted to a high proportion, does not undergo any angle changes.
Amazon Background Review Criteria:
  3.1 Pure White Background: Ignore the background of the input image and modify the product background to: A seamless pure white background with RGB values of (255, 255, 255). The RGB value of the pure white background must be: (255, 255, 255).
  3.2 Cleanliness: Create a "brand new" effect - remove all dust, rust, scratches, fingerprints, and surface blemishes through electronic means.
  3.3 Natural fit effect: Add a subtle soft shadow at the bottom to ensure the product looks realistic and natural, rather than "floating".
Professional rendering strategy:
4.1 Studio lighting: Use uniform and high-end 3D studio lighting to enhance the high-end texture and three-dimensionality of the product.
4.2 Clarity: Ensure clear details, sharp focus, and high-resolution textures.
Position change strategy for the main body: Position the product precisely in the center, but do not change the shooting angle or direction of the main body of the product.
High main body proportion strategy: Ensure that the main body of the product occupies 85% to 90% of the entire image, and try to enlarge it to fill the entire image, meeting Amazon's main image display requirements.
Refinement strategy:
7.1 Remove flaws, rust, dirt, dust, fingerprints, and messy thread ends.
7.2 Adjust hue/saturation, clarity, the representation of different materials, accurately reproduce the actual color of the product, and highlight the material characteristics (such as the reflection of metal, the transparency of glass, and the texture of fabric)
7.3 Adjust brightness/contrast, highlights, midtones, shadows, to restore three-dimensionality, but do not change the shooting angle of the product. Through enhancing the light and shadow, make the product not appear flat on a white background, and shape a realistic volume sense.
```

## 执行自检

- [ ] 步骤 1 所有参考图都为公开可访问 URL（本地路径已通过 linkfox-file-upload 上传），否则报错而非带空图调 imagegen
- [ ] 背景为无缝纯白 RGB(255,255,255)，无原图杂背景 / 渐变 / 阴影色块残留
- [ ] 产品的拍摄角度、形态、颜色、材质与原图保持一致，未增删任何产品元素
- [ ] 主体居中且占比约 85%~90%，未因放大产生畸变
- [ ] 底部带自然柔和投影，产品不"悬浮"
- [ ] 步骤 3 `provider` 已按入参透传给 imagegen、`outputNum=1`，`aspectRatio=ratio` 已原样透传
