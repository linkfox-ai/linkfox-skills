#!/usr/bin/env python3
"""Run the named Lazada marketing operations."""
from _operations import main

API_PATH = "/lazada/marketing"
SLUG = "linkfox-lazada-store-marketing"
OPERATIONS = {
    "listVouchers": False,
    "getVoucher": False,
    "createVoucher": True,
    "updateVoucher": True,
    "activateVoucher": True,
    "deactivateVoucher": True,
    "listVoucherProducts": False,
    "addVoucherSkus": True,
    "removeVoucherSkus": True,
    "listFreeShipping": False,
    "getFreeShipping": False,
    "createFreeShipping": True,
    "updateFreeShipping": True,
    "activateFreeShipping": True,
    "deactivateFreeShipping": True,
    "listFreeShippingProducts": False,
    "addFreeShippingSkus": True,
    "removeFreeShippingSkus": True,
    "listFreeShippingRegions": False,
    "listShippingOptions": False,
    "listFlexiCombo": False,
    "getFlexiCombo": False,
    "createFlexiCombo": True,
    "updateFlexiCombo": True,
    "activateFlexiCombo": True,
    "deactivateFlexiCombo": True,
    "listFlexiComboProducts": False,
    "addFlexiComboSkus": True,
    "removeFlexiComboSkus": True,
    "listSponsoredMaxCampaigns": False,
    "getSponsoredMaxOverview": False,
    "getSponsoredMaxMetric": False,
    "createSponsoredMaxCampaign": True,
    "updateSponsoredMaxCampaign": True,
    "setSponsoredMaxCampaignStatus": True,
}


if __name__ == "__main__":
    raise SystemExit(main(API_PATH, SLUG, OPERATIONS))
