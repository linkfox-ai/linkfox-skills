# Partner Global — Promotion 接口目录

Partner Platform for **Global** 菜单：**Promotion / 电商促销**（与 US 版对齐的 **6** 个 `bg.promotion.*` `type`）。

文档根 `menu_code`（与 `linkfox-temu-fulfillment-global` 等一致）：`7289390cfd724be4a196f11ebe45a896`。

本 skill 经 `temu_global_proxy`（`POST /temu/proxy`）调用，默认 **`site=global`**、**`tokenPurpose=product-inventory`**。

> Global Partner 各子菜单 `sub_menu_code` 请在 [partner-global.temu.com](https://partner-global.temu.com/documentation) 按 `type` 打开后补全。

## 已接入（6）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| — | `bg.promotion.activity.query` | `global_promotion_activity_query.py` | [apis/bg-promotion-activity-query.md](./apis/bg-promotion-activity-query.md) |
| — | `bg.promotion.activity.candidate.goods.query` | `global_promotion_activity_candidate_goods_query.py` | [apis/bg-promotion-activity-candidate-goods-query.md](./apis/bg-promotion-activity-candidate-goods-query.md) |
| — | `bg.promotion.activity.goods.query` | `global_promotion_activity_goods_query.py` | [apis/bg-promotion-activity-goods-query.md](./apis/bg-promotion-activity-goods-query.md) |
| — | `bg.promotion.activity.goods.enroll` | `global_promotion_activity_goods_enroll.py` | [apis/bg-promotion-activity-goods-enroll.md](./apis/bg-promotion-activity-goods-enroll.md) |
| — | `bg.promotion.activity.goods.operation.query` | `global_promotion_activity_goods_operation_query.py` | [apis/bg-promotion-activity-goods-operation-query.md](./apis/bg-promotion-activity-goods-operation-query.md) |
| — | `bg.promotion.activity.goods.update` | `global_promotion_activity_goods_update.py` | [apis/bg-promotion-activity-goods-update.md](./apis/bg-promotion-activity-goods-update.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `bg.promotion.activity.query` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.promotion.activity.candidate.goods.query` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.promotion.activity.goods.query` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.promotion.activity.goods.enroll` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.promotion.activity.goods.operation.query` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.promotion.activity.goods.update` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |

## 上游 OpenAPI（Global）

`POST` https://openapi-b-global.temu.com/openapi/router（经 LinkFox 网关 `site=global` 转发）

## 通用脚本

| 脚本 | 说明 |
|------|------|
| `temu_global_proxy.py` | 任意 `type` + `params` |
| `temu_global_file_download.py` | 加签文件下载 |

## 相关 skill

| 能力 | skill |
|------|--------|
| **促销/营销活动**（本 skill） | **`linkfox-temu-promotion-global`** |
| 商品管理 | `linkfox-temu-manage-product-global` |
| 价格 | `linkfox-temu-price-global` |
| 广告 Ads | `linkfox-temu-ads-global` |
| 订单 | `linkfox-temu-order-global` |
| 美国站促销 | `linkfox-temu-promotion-us` |
| 欧洲站促销 | `linkfox-temu-promotion-eu` |

## Token 说明

建议使用 **`tokenPurpose=product-inventory`**。详见 [access-token.md](./access-token.md)。
