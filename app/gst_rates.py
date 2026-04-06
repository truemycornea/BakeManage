# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""GST HSN-code to slab mapping used by the GST engine."""

from __future__ import annotations

# HSN prefix → GST slab percentage (0 / 5 / 12 / 18 / 28)
# Covers common bakery / FMCG HSN codes. Unmatched codes default to 18%.
HSN_GST_RATES: dict[str, int] = {
    # 0% — essential food items
    "0401": 0,  # Milk and cream
    "0402": 0,  # Milk powder
    "0403": 0,  # Yogurt, buttermilk
    "0406": 0,  # Cheese
    "0701": 0,  # Potatoes
    "0702": 0,  # Tomatoes
    "1001": 0,  # Wheat
    "1006": 0,  # Rice
    "1101": 0,  # Wheat or meslin flour
    "1102": 0,  # Cereal flours (other)
    "1701": 0,  # Cane or beet sugar
    "0901": 0,  # Coffee (raw)
    "0902": 0,  # Tea
    # 5% — packaged foods / bakery raw materials
    "0409": 5,  # Natural honey
    "0805": 5,  # Citrus fruits
    "1904": 5,  # Breakfast cereals
    "1905": 5,  # Bread, pastry, cakes, biscuits (branded packaged)
    "2009": 5,  # Fruit juices
    "2101": 5,  # Extracts of coffee, tea
    "2103": 5,  # Sauces, condiments
    "2106": 5,  # Food preparations (branded/packaged)
    "0811": 5,  # Frozen fruits
    "1507": 5,  # Soya-bean oil
    "1511": 5,  # Palm oil
    "1512": 5,  # Sunflower oil
    "1513": 5,  # Coconut oil
    "1514": 5,  # Rapeseed oil
    "1516": 5,  # Hydrogenated fats / vanaspati
    "0405": 5,  # Butter and other fats of milk
    # 12% — semi-processed / packaged baked goods
    "1806": 12,  # Chocolate
    "1901": 12,  # Malt extract, infant food preparations
    "2105": 12,  # Ice cream
    "2202": 12,  # Packaged water / beverages
    # 18% — processed snacks, confectionery
    "1704": 18,  # Sugar confectionery (no cocoa)
    "2001": 18,  # Vegetables prepared in vinegar
    "2005": 18,  # Other prepared vegetables
    "2008": 18,  # Fruits, nuts (otherwise prepared)
    "2201": 18,  # Waters (not in containers)
    "2203": 18,  # Beer made from malt
    # 28% — luxury / specific items
    "2402": 28,  # Cigars
    "2403": 28,  # Other tobacco
}

_DEFAULT_RATE = 18  # fallback GST rate for unknown HSN codes


def get_gst_rate(hsn_code: str) -> int:
    """Return GST slab (%) for a given HSN code.

    Matches on the first 4 characters of the HSN code; falls back to
    _DEFAULT_RATE (18%) for unmapped codes.
    """
    prefix = (hsn_code or "").strip()[:4]
    if prefix in HSN_GST_RATES:
        return HSN_GST_RATES[prefix]
    # Try 2-digit chapter match
    chapter = prefix[:2]
    for key, rate in HSN_GST_RATES.items():
        if key.startswith(chapter):
            return rate
    return _DEFAULT_RATE
