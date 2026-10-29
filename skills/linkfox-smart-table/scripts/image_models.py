"""附件 AI 列可用的出图模型 —— **改模型只改这个文件**（以及 references/ai.md 里那张同名表）。

来源：LinkFoxAI `GET https://ai-api.linkfox.com/image/model/config/list?bizType=71`
（与页面上附件列 AI 配置的下拉同一个接口、同一个 bizType；测试线 test-ai-api 同一份清单）。
`code` 就是页面落库的 modelKey —— 不是 `apiCode`。2026-10-12 取值。

后端不维护模型白名单（只要求非空），所以：
  - 上游新增模型：在 IMAGE_MODELS 里加一项、在 references/ai.md 的表里加一行，就能用；
  - 上游下线模型：删掉对应项，脚本就会在本地先拦住。
比例/分辨率取各模型自己声明的支持列表；不传时取列表第一项（与页面一致）。
"""

DEFAULT_IMAGE_MODEL = "GPT_2_5_IMAGE"

_COMMON_RATIOS = ["1:1", "3:2", "2:3", "3:4", "4:3", "4:5", "5:4", "16:9", "9:16", "21:9"]
_GPT_RATIOS = ["1:1", "3:4", "4:3", "2:3", "3:2", "9:16", "16:9", "4:5", "5:4", "21:9", "9:21"]

# code -> {name, ratios, resolutions, ref}；ref 是该模型自己声明能吃几张参考图
IMAGE_MODELS = {
    "GPT_2_5_IMAGE": {"name": "LF智能模型 G-2.5 Sunburst", "ratios": _GPT_RATIOS, "resolutions": ["1K", "2K", "4K"], "ref": 5},
    "GPT_2_5_F_IMAGE": {"name": "LF智能模型 G-2.5 Flare", "ratios": _GPT_RATIOS, "resolutions": ["1K", "2K", "4K"], "ref": 5},
    "GPT_2_IMAGE": {"name": "LF智能模型 G-2", "ratios": _GPT_RATIOS, "resolutions": ["1K", "2K", "4K"], "ref": 5},
    "GEMINI_NANO_BANANA_2_1": {"name": "LF全能模型 2.1", "ratios": _COMMON_RATIOS, "resolutions": ["1K", "2K", "4K"], "ref": 5},
    "GEMINI_FLASH_PRO": {
        "name": "LF全能模型 Pro",
        "ratios": ["1:1", "16:9", "9:16", "3:4", "4:3", "3:2", "2:3", "4:5", "5:4", "21:9"],
        "resolutions": ["1K", "2K", "4K"],
        "ref": 5,
    },
    "GEMINI_31_FLASH_IMAGE": {"name": "LF全能模型 2", "ratios": _COMMON_RATIOS, "resolutions": ["1K", "2K", "4K"], "ref": 5},
    "GEMINI_31_FLASH_LITE": {
        "name": "LF全能模型 Lite",
        "ratios": ["1:1", "3:2", "2:3", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        "resolutions": ["1K"],
        "ref": 5,
    },
    "SEEDREAM5_PRO": {
        "name": "Seedream 5.0 Pro",
        "ratios": ["1:1", "3:4", "4:3", "9:16", "16:9", "3:2", "2:3", "21:9"],
        "resolutions": ["1K", "2K"],
        "ref": 5,
    },
    "WAN2_7": {"name": "Wan 2.7", "ratios": _COMMON_RATIOS, "resolutions": ["1K", "2K"], "ref": 5},
    "AIDRAW_EDIT": {
        "name": "Linkfox-Image-1",
        "ratios": ["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9", "21:9"],
        "resolutions": ["2K"],
        "ref": 4,
    },
}

_AI_KEYS = {"prompt", "referenceFields", "model", "aspectRatio", "resolution"}


def prepare_field_ai(field, where):
    """校验一列的 `ai`，并就地补上默认的 model / aspectRatio / resolution。

    返回错误文案（None 表示通过）。只在 field 带了 `ai` 时调用。
    引用的列存不存在、类型对不对由服务端在建列前校验（它看得到整张表），这里只管形状和模型。
    """
    ai = field.get("ai")
    if not isinstance(ai, dict):
        return f"{where}.ai 必须是对象"
    if field.get("type") != "attachment":
        return f"{where} 带了 ai，但 type 是 {field.get('type')!r}。AI 出图只能配在 type 为 attachment 的列上"
    unknown = sorted(set(ai) - _AI_KEYS)
    if unknown:
        return f"{where}.ai 里有不认识的键：{', '.join(unknown)}。只支持：{', '.join(sorted(_AI_KEYS))}"
    if not str(ai.get("prompt") or "").strip():
        return f"{where}.ai.prompt 不能为空。用 {{列名}} 引用别的文本列，如「把参考图里的商品放进「{{场景}}」描述的场景里」"
    # referenceFields 可选（上游 2026-10-14 起参考图非必填）：不传 / 传 [] = 只按提示词出图
    refs = ai.get("referenceFields")
    if refs is not None:
        if not isinstance(refs, list) or not all(isinstance(r, str) and r for r in refs):
            return f"{where}.ai.referenceFields 必须是列名数组（取自 attachment 或 image 列）；不需要参考图就别传"
        if len(refs) > 9:
            return f"{where}.ai.referenceFields 最多 9 列"

    model = ai.setdefault("model", DEFAULT_IMAGE_MODEL)
    spec = IMAGE_MODELS.get(model)
    if spec is None:
        return (
            f"{where}.ai.model={model!r} 不在可用模型里：{', '.join(IMAGE_MODELS)}。"
            "如果是上游新上的模型，先在 scripts/image_models.py 和 references/ai.md 里加上"
        )
    ratio = ai.setdefault("aspectRatio", spec["ratios"][0])
    if ratio not in spec["ratios"]:
        return f"{where}.ai.aspectRatio={ratio!r} 不被 {model} 支持，可选：{', '.join(spec['ratios'])}"
    resolution = ai.setdefault("resolution", spec["resolutions"][0])
    if resolution not in spec["resolutions"]:
        return f"{where}.ai.resolution={resolution!r} 不被 {model} 支持，可选：{', '.join(spec['resolutions'])}"
    return None
