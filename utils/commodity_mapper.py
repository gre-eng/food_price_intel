"""
Commodity crosswalk between WFP and NBS naming conventions.

Every name in MATCHED_PAIRS was taken verbatim from the real uploaded files:
  - WFP names: unique values of `commodity` in wfp_food_prices_nga.csv
  - NBS names: unique values of `Item Label` across all 16 monthly NBS xlsx files

Only pairs that clearly refer to the same underlying commodity are included.
Anything ambiguous (different unit, different specification, or no
counterpart at all) is intentionally left OUT of this map and instead
listed in UNMAPPED_WFP / UNMAPPED_NBS below, so the loader can surface it
in the UI instead of silently guessing.
"""

# canonical_id -> {"wfp": "<exact WFP commodity string>", "nbs": "<exact NBS Item Label string>"}
MATCHED_PAIRS = {
    "rice_local":        {"wfp": "Rice (local)",                       "nbs": "Rice Local, short-Grained"},
    "rice_imported":     {"wfp": "Rice (imported)",                    "nbs": "Rice Long-Grained (Imported)"},
    "maize_white":       {"wfp": "Maize (white)",                      "nbs": "Maize (Corn) Grains (White) sold loose"},
    "gari_white":        {"wfp": "Gari (white)",                       "nbs": "Garri white"},
    "gari_yellow":       {"wfp": "Cassava meal (gari, yellow)",         "nbs": "Garri Yellow"},
    "yam":               {"wfp": "Yam",                                "nbs": "Yam Tuber"},
    "beans_white":       {"wfp": "Beans (white)",                      "nbs": "Beans white"},
    "oil_palm":          {"wfp": "Oil (palm)",                         "nbs": "Palm oil, 75cl"},
    "oil_vegetable":     {"wfp": "Oil (vegetable)",                    "nbs": "Vegetable Oil, 75cl"},
    "tomatoes":          {"wfp": "Tomatoes",                           "nbs": "Tomatoes, fresh"},
    "onions":            {"wfp": "Onions",                             "nbs": "Onions, fresh"},
    "watermelons":       {"wfp": "Watermelons",                        "nbs": "Watermelon whole, medium size fresh"},
    "beef":              {"wfp": "Meat (beef)",                        "nbs": "Beef Boneless"},
}

# WFP commodities with no NBS counterpart in the uploaded files (left unmapped on purpose)
UNMAPPED_WFP = [
    "Maize", "Maize (yellow)", "Maize flour", "Rice (milled, local)",
    "Sorghum", "Sorghum (brown)", "Sorghum (white)", "Millet", "Wheat",
    "Yam (Abuja)", "Beans (red)", "Beans (niebe)", "Cowpeas",
    "Cowpeas (brown)", "Cowpeas (white)", "Groundnuts", "Groundnuts (shelled)",
    "Eggs", "Fish", "Meat (goat)", "Milk (powder)", "Sugar", "Salt",
    "Seasoning (maggi cube)", "Fuel (diesel)", "Fuel (petrol-gasoline)",
    "Bananas", "Oranges", "Spinach", "Bread",
]

# NBS commodities with no WFP counterpart in the uploaded files (left unmapped on purpose)
UNMAPPED_NBS = [
    "Agric hen eggs", "Agric hen eggs,", "Agric hen eggs, (a Crate of 30 pieces)",
    "Beans Brown", "Bread (sliced), 450g", "Bread (unsliced), 450g",
    "Carrots, fresh", "Cat fresh fish", "Chicken Wings", "Chicken feet",
    "Chicken meat (Frozen)", "Cray fish small white", "Dried fish, Bonga",
    "Ginger, fresh", "Goat Meat Bone in", "Groundnut oil, 75cl",
    "Groundnuts, roasted,75cl bottle", "Irish Potatoe", "Local Rice (Broken)",
    "Mackerel, Frozen", "Plantain (ripe)", "Plantain (unripe)",
    "Semovita, Prepacked (1kg)", "Smoked fish (Mackerel)", "Sweet potatoes",
    "Tilapia fresh fish (Epiya)", "Tin Milk-Evaporated, Peak Milk, 150g",
    "Tin Milk-Evaporated, Three Crown Milk, 160g", "Titus, frozen",
    "Vegetable Oil, 75cl",
    "Wheat Flour, Prepacked (2kg)",
]


def build_lookup():
    """Flatten MATCHED_PAIRS into {(source, exact_name): canonical_id}."""
    lookup = {}
    for canon, sources in MATCHED_PAIRS.items():
        lookup[("wfp", sources["wfp"])] = canon
        lookup[("nbs", sources["nbs"])] = canon
    return lookup


LOOKUP = build_lookup()


def map_commodity(name: str, source: str):
    """
    Exact match only - no fuzzy matching, no guessing.
    Returns canonical_id if name is in our verified crosswalk, else None.
    `source` must be 'wfp' or 'nbs'.
    """
    return LOOKUP.get((source, name))


def get_canonical_label(canonical_id: str) -> str:
    """Human-readable label for a canonical commodity id."""
    labels = {
        "rice_local": "Rice (Local)",
        "rice_imported": "Rice (Imported)",
        "maize_white": "Maize (White)",
        "gari_white": "Gari / Garri (White)",
        "gari_yellow": "Gari / Garri (Yellow / Cassava meal)",
        "yam": "Yam",
        "beans_white": "Beans (White)",
        "oil_palm": "Palm Oil",
        "oil_vegetable": "Vegetable Oil",
        "tomatoes": "Tomatoes",
        "onions": "Onions",
        "watermelons": "Watermelon",
        "beef": "Beef",
    }
    return labels.get(canonical_id, canonical_id)