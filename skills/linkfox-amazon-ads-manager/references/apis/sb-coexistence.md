# Sponsored Brands V3 / V4 共存与路由

## 版本边界

| 调用入口 | 适用结构 | 用途 |
|---|---|---|
| `scripts/sb/v4/` | `LEGACY` 或 `MULTI_AD_GROUP` | 默认入口；新建活动、多广告组、Ad/Creative 管理 |
| `scripts/sb/v3/` | 仅 `LEGACY` | 历史活动兼容 |
| `scripts/sb/*.py` | 同 V4 | V4 兼容入口；调用时优先使用 `scripts/sb/v4/` |

新业务默认使用 V4。只有用户明确要求 V3，或已确认 Campaign 为 Legacy 时，才使用 V3。

## 不自动回落

脚本不执行 `V4 失败 → V3 重试`。Amazon 返回非 2xx 时，保留状态码和响应体交给调用方判断。原因：

1. API 版本不等于 Campaign 结构；
2. Multi-Ad-Group Campaign 无法无损转换成 V3；
3. 自动回落会掩盖权限、参数或资源状态错误；
4. V3 读取 V4 活动可能造成多 Ad Group 数据截断。

当顶层参数或 `payload` 内出现 `campaignStructure=MULTI_AD_GROUP` / `isMultiAdGroupsEnabled=true`（含 `"true"`/`1` 等写法）时，V3 脚本会在发请求前返回：

```json
{
  "code": "SB_V4_CAMPAIGN_NOT_SUPPORTED",
  "message": "This campaign uses the Sponsored Brands V4 multi-ad-group structure. Use scripts/sb/v4 instead of V3."
}
```

脚本没有本地 Campaign 数据库；如果调用方未提供结构信息，无法仅凭 `campaignId` 可靠判断结构。因此 Agent 应先用 V4 `list_campaigns.py` 查询 `isMultiAdGroupsEnabled`，再决定是否允许使用 V3。

## Amazon 路径与脚本版本不是一回事

Amazon 的 Campaign / Ad Group / Ad 主资源有明确 V4 路径：

```text
sb/v4/campaigns/**
sb/v4/adGroups/**
sb/v4/ads/**
```

但 Keyword 与 Product Target 仍使用共享资源路径：

```text
sb/keywords
sb/targets
sb/targets/list
```

这些共享路径可以通过 `campaignId + adGroupId` 管理多广告组活动。为让调用意图明确，本 skill 在 `sb/v3/` 和 `sb/v4/` 都提供 keyword/target 入口；两者底层调用同一 Amazon 资源：

- `sb/v3/*`：声明调用方已确认是 Legacy；
- `sb/v4/*`：声明按 V4 Campaign/Ad Group 结构管理；
- 输出中的 `amazonResourceVersion` 会标记共享资源类别，例如 keyword 的 `V3_SHARED_TARGETING` 或 target 的 `SHARED_TARGETING`。

这不是 V4 自动降级，也不会在失败后切换版本。

## Creative 边界

- V3 Legacy Campaign 的 Creative 是 Campaign payload 的组成部分，没有独立的 V3 Creative CRUD 脚本。
- V4 使用 Ad 与独立 Creative Version：
  - `sb/v4/list_ads.py`
  - `sb/v4/create_ads.py`
  - `sb/v4/list_creatives.py`（必须传 `adId`，不是全账号 Creative 列表）
  - `sb/v4/create_creatives.py`

SB V4 Creative 支持查询 Creative Version 与创建新版本，没有通用 `update_creatives.py`；不要把 Creative Version 管理描述成完整 CRUD。

不要伪造不存在的 `sb/v3/creatives` 或 `sb/v4/keywords` Amazon 路径。

## 决策流程

```text
新建 / 多 Ad Group / Ad / Creative
  → scripts/sb/v4/

关键词或 Target
  → 默认 scripts/sb/v4/
  → 仅在已确认 Legacy 或用户明确要求 V3 时使用 scripts/sb/v3/

V3 + MULTI_AD_GROUP
  → 拒绝并提示使用 V4

任一版本调用失败
  → 返回原错误；不自动重试另一版本
```
