---
name: linkfox-temu-category-search
description: 在已同步到本地库的 Temu 类目数据中按关键词检索类目中文名、英文名与类目 id，用于商品/店铺筛选的类目 id。当用户提到 Temu 类目、Temu category id、Temu 类目树、Temu 后台类目、temu 品类、syncTemuCategory（Temu 品类同步）后查询类目、Temu category search 时触发。即使用户未提及工具名，只要在本地已同步的 Temu 类目库里按关键词找类目 id，也应触发此技能。
---

# Temu 类目检索

## 要点

- **必填**：`keyword`（子串匹配类目中文名、英文名、类目 id）。
- **分页**：`page` 从 1 起；`pageSize` 默认 50、最大 200。
- 返回的 **`id` / `categoryId`** 可作为 Temu 商品查询的 `categoryHome`/`categoryBackend`、店铺查询的 `category` 等入参的类目标识（与具体工具 schema 一致即可）。

## 脚本（可选）

命令行调试：`python scripts/temu_category_search.py '<JSON>'`（需 `LINKFOXAGENT_API_KEY`）。详见 [references/api.md](references/api.md) 末尾。

## 参考

入参/出参表见 [references/api.md](references/api.md)。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## 积分消耗规则

不消耗积分。
