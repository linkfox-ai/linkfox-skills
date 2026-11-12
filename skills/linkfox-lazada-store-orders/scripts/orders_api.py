#!/usr/bin/env python3
"""Run the named Lazada orders operations."""
from _operations import main

API_PATH = "/lazada/orders"
SLUG = "linkfox-lazada-store-orders"
OPERATIONS = {
    "getShipmentProviders": False,
    "getShippingLabel": False,
    "getOrderTrace": False,
    "validateOrderCancellation": False,
    "listReverseOrders": False,
    "getReverseOrder": False,
    "listReverseOrderReasons": False,
    "listReverseOrderHistory": False,
    "listReviewHistory": False,
    "getReviews": False,
    "packOrder": True,
    "repackOrder": True,
    "readyToShip": True,
    "confirmDbsDelivery": True,
    "markDbsDeliveryFailed": True,
    "deliverDigitalOrder": True,
    "cancelOrder": True,
    "decideOrderCancellation": True,
    "updateReverseOrder": True,
    "decideOnlyRefund": True,
    "replyReview": True,
}


def has_shipping_label(data):
    if not isinstance(data, dict):
        return False
    if any(isinstance(data.get(field), str) and data[field].strip() for field in ("file", "pdf_url")):
        return True
    return any(has_shipping_label(data.get(field)) for field in ("data", "result"))


if __name__ == "__main__":
    raise SystemExit(main(API_PATH, SLUG, OPERATIONS, private_operations={"getShippingLabel"},
                          response_checks={"getShippingLabel": has_shipping_label}))
