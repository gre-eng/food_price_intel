"""
Loader for the WFP Nigeria food prices file.

Verified real columns (from data/wfp_food_prices_nga.csv):
date, admin1, admin2, market, market_id, latitude, longitude, category,
commodity, commodity_id, unit, priceflag, pricetype, currency, price, usdprice

Verified real date range in the uploaded file: 2002-01-15 to 2026-04-15.
"""

import pandas as pd
from utils.commodity_mapper import map_commodity


def load_wfp(path: str) -> pd.DataFrame:
    """Load the raw WFP csv and tag rows with canonical commodity id where mapped."""
    df = pd.read_csv(path, low_memory=False)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["commodity_canonical"] = df["commodity"].apply(lambda x: map_commodity(x, "wfp"))
    df["source"] = "WFP"
    return df


def get_unmapped_wfp_commodities(df: pd.DataFrame) -> list:
    """Real unique commodity names present in the file that are not in our verified crosswalk."""
    return sorted(
        n for n in df["commodity"].dropna().unique()
        if map_commodity(n, "wfp") is None
    )


def filter_mapped(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows whose commodity has a verified canonical match."""
    return df[df["commodity_canonical"].notna()].copy()