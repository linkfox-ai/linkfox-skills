#!/usr/bin/env python3
"""Run the named Lazada products operations."""
from _operations import main

API_PATH = "/lazada/products"
SLUG = "linkfox-lazada-store-product"
# Base64 encoded size plus 8 KiB for the JSON request envelope.
FILE_LIMITS = {"uploadImage": 1_406_296, "uploadVideoBlock": 4_202_496}
OPERATIONS = {
    "getCategoryTree": False,
    "getCategoryAttributes": False,
    "listBrands": False,
    "listWarehouses": False,
    "getProductQcStatus": False,
    "getImageMigrationResult": False,
    "getVideo": False,
    "getVideoQuota": False,
    "createProduct": True,
    "updateProduct": True,
    "updatePriceQuantity": True,
    "updateSellableQuantity": True,
    "adjustSellableQuantity": True,
    "removeProduct": True,
    "migrateImage": True,
    "migrateImages": True,
    "uploadImage": True,
    "initVideoUpload": True,
    "uploadVideoBlock": True,
    "completeVideoUpload": True,
    "removeVideo": True,
    "deactivateProduct": True,
}


if __name__ == "__main__":
    raise SystemExit(main(API_PATH, SLUG, OPERATIONS, file_limits=FILE_LIMITS))
