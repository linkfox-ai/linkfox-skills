# 品牌视觉基因提取

## 流程

1. 用商品图、品牌图和用户要求构造文本生成参数。
2. 按 `linkfox-aigc-textgen-api.md` 调用 `aigc/textGenAsync`，保存 `taskId`。
3. 需要查询时，每次仅调用一次 `aigc/textTaskQuery`。
4. 当 `status=SUCCESS` 时，把 `content` 解析为品牌基因 JSON。
5. 将 JSON 通过 stdin 交给 `scripts/brand/save_brand_gene.py`，保存完整响应和 `brand-gene.json`。

`save_brand_gene.py` 是纯本地解析与落盘工具，不发起网络请求。响应字段以 `linkfox-aigc-textgen-api.md` 的来源表为准。
