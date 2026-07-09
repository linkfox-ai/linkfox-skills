---
name: linkfox-temu-add-product-us
description: Temu 美国站发品（Add Product）API，经 LinkFox 网关转发 Partner US 商品接口：V2发品(temu.local.goods.v2.add)、类目属性、规格、图片上传、商品列表/详情/编辑、类目映射、SKU库存、供货价等。当用户提到 Temu 美国站发品、Temu US Add Product、goods.list、goods.detail、temu.local.goods.v2.add、商品类目映射、SKU库存、供货价、Partner US 发品文档 时触发。订单/物流请用其他 Temu skill。
---

# Temu 美国站发品 API（Partner US）

本 skill（`linkfox-temu-add-product-us`）覆盖 Partner Platform for US **Product** 菜单（`menu_code=fb16b05f7a904765aac4af3a24b87d4a`）下 **19 个商品接口**：**4 个 V2 推荐发品** + **15 个标准商品 API**（查询、编辑、类目、库存、价格等）。

**网关（本 skill 内置）**：

| 能力 | 方法 | 网关路径 |
|------|------|----------|
| 商品 OpenAPI（全部 `us_goods_*`、`temu_us_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载（`temu_us_file_download`） | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

商品 `type` 写在 Body，**不是** URL 路径。

> **不是订单 skill**：订单、发货、物流见 `linkfox-temu-order-us` 或其它履约类 skill。

## 调用方式

- **API 端点**：`POST /temu/proxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-add-product-us-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `us` | Partner US |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose（storeKey） | `product-inventory` | 酷鸟卖家助手 token |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`

## Scripts

### V2 推荐发品

| 脚本 | type |
|------|------|
| `us_goods_attrs.py` | `temu.local.product.attributes.get` |
| `us_goods_variation.py` | `temu.local.product.variation.get` |
| `us_goods_image_upload.py` | `temu.local.goods.image.v2.upload` |
| `us_goods_add.py` | `temu.local.goods.v2.add` |

### 查询 / 编辑 / 类目 / 库存

| 脚本 | type |
|------|------|
| `us_goods_list.py` | `temu.goods.list.get` |
| `us_goods_detail.py` | `temu.goods.detail.get` |
| `us_goods_update.py` | `temu.goods.update` |
| `us_goods_edit_property.py` | `temu.goods.edit.property` |
| `us_goods_edit_sensitive.py` | `temu.goods.edit.sensitive.attr` |
| `us_goods_migrate.py` | `temu.goods.migrate` |
| `us_goods_cats.py` | `bg.goods.cats.get` |
| `us_goods_attrs_bg.py` | `bg.goods.attrs.get` |
| `us_goods_parent_spec.py` | `bg.glo.goods.parentspec.get` |
| `us_goods_brand.py` | `bg.glo.goods.brand.get` |
| `us_goods_category_mapping.py` | `bg.goods.category.mapping` |
| `us_goods_stock_get.py` | `bg.btg.goods.stock.quantity.get` |
| `us_goods_stock_update.py` | `bg.btg.goods.stock.quantity.update` |
| `us_goods_price_list.py` | `temu.goods.price.list.get` |
| `us_goods_add_legacy.py` | `temu.goods.add` |
| `temu_us_proxy.py` | 任意 `type` |
| `temu_us_file_download.py` | 加签文件下载 |

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 商品列表
python scripts/us_goods_list.py '{"accessToken":"TOKEN","page":1,"pageSize":20}'

# 类目映射
python scripts/us_goods_category_mapping.py '{
  "accessToken":"TOKEN",
  "goodsName":"测试商品",
  "goodsNameEn":"Test Product"
}'

# V2 发品流程
python scripts/us_goods_attrs.py '{"accessToken":"TOKEN","params":{"catId":12345}}'
python scripts/us_goods_image_upload.py '{"accessToken":"TOKEN","params":{"image":"<BASE64>"}}'
python scripts/us_goods_add.py '{"accessToken":"TOKEN","params":{"..."}}'
```

**Feedback：** `skillName`：`linkfox-temu-add-product-us`

## 网关与授权脚本

| 脚本 | 说明 |
|------|------|
| `check_linkfox_token.py` | 校验 LinkFox 用户 Token |
| `temu_token_guide.py` | Temu accessToken 后台授权步骤 |
| `save_temu_access_token.py` | 保存 accessToken 到本地 |
| `list_temu_access_tokens.py` | 列出已保存 token |
| `get_temu_access_token.py` | 读取已保存 token |
| `temu_proxy.py` | 通用网关转发（多 site） |
| `temu_file_download.py` | 加签文件下载（多 site） |

授权说明：[references/access-token.md](./references/access-token.md)

