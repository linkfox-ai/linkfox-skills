"""查找引用列（type: "lookup"）的本地预检。createTable / addTable / addFields 三条共用。

只拦"形状填错"这一类：键名、必填项、计算方式拼写。被引用的表在不在、列名对不对、
计算方式与列类型配不配，只有服务端知道，那些交给服务端报（报错同样是能照着改的中文）。
"""

# 与服务端 smartTableLookupComputeModes 一致（页面「计算方式」那 7 项）
COMPUTE_MODES = ("raw", "unique", "sum", "count", "average", "max", "min")

LOOKUP_KEYS = ("tableId", "fieldName", "conditions", "conjunction", "computeMode")
CONDITION_KEYS = ("fieldName", "operator", "value", "valueFromField")


def check_field_lookup(field, where):
    """校验一列的 type/lookup 搭配。没问题返回 None，否则返回一句人话。"""
    is_lookup = field.get("type") == "lookup"
    has_lookup = "lookup" in field
    if not is_lookup:
        if has_lookup:
            return f"{where} 带了 lookup，但 type 是 {field.get('type')!r}。lookup 只能配在 type 为 lookup 的列上"
        return None
    if not has_lookup:
        return (
            f"{where} 的 type 是 lookup，必须提供 lookup："
            '{"tableId": "被引用的表", "fieldName": "取哪一列", "conditions": [...], "computeMode": "raw"}'
        )

    lookup = field["lookup"]
    if not isinstance(lookup, dict):
        return f"{where}.lookup 必须是对象"
    unknown = [k for k in lookup if k not in LOOKUP_KEYS]
    if unknown:
        # 服务端是 strict 的，拼错的键会被拒；本地先拦是为了省一次往返
        return f"{where}.lookup 里有不认识的键：{unknown}。只认：{', '.join(LOOKUP_KEYS)}"

    table_id = lookup.get("tableId")
    if not table_id or not str(table_id).startswith("tbl"):
        return (
            f"{where}.lookup.tableId 必须是被引用表的 tableId（tbl 开头），收到 {table_id!r}。"
            "只能引用你自己创建的表：用 smart_table.py listMyTables 找"
        )
    if not lookup.get("fieldName"):
        return f"{where}.lookup.fieldName 缺失：要从被引用表里取哪一列（列名）"

    mode = lookup.get("computeMode", "raw")
    if mode not in COMPUTE_MODES:
        return f"{where}.lookup.computeMode={mode!r} 不支持。可用：{', '.join(COMPUTE_MODES)}"
    conj = lookup.get("conjunction", "and")
    if conj not in ("and", "or"):
        return f"{where}.lookup.conjunction 只能是 and 或 or，收到 {conj!r}"

    conditions = lookup.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        return (
            f"{where}.lookup.conditions 必填（非空数组，查找条件是页面上的保存必填项）。"
            '按行匹配写成 [{"fieldName": "SKU", "operator": "is", "valueFromField": "SKU"}]'
        )
    for i, cond in enumerate(conditions):
        at = f"{where}.lookup.conditions[{i}]"
        if not isinstance(cond, dict):
            return f"{at} 必须是对象"
        unknown = [k for k in cond if k not in CONDITION_KEYS]
        if unknown:
            return f"{at} 里有不认识的键：{unknown}。只认：{', '.join(CONDITION_KEYS)}"
        if not cond.get("fieldName") or not cond.get("operator"):
            return f"{at} 必须有 fieldName（被引用表的列）和 operator"
        if "value" in cond and "valueFromField" in cond:
            return f"{at} 的 value 和 valueFromField 只能给一个：要么跟固定值比，要么跟本表某一列比"
    return None
