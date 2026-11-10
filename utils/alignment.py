"""
Alignment utilities. Operates only on rows that already have a verified
commodity_canonical (i.e. output of wfp_loader.filter_mapped /
nbs_loader.filter_mapped).
"""

import pandas as pd


def wfp_monthly_national_average(wfp_df: pd.DataFrame) -> pd.DataFrame:
    """
    WFP data is per-market. Resample to monthly national average per
    commodity_canonical. Missing months are interpolated linearly -
    explicitly labeled as interpolated.
    """
    df = wfp_df.dropna(subset=["commodity_canonical", "price"]).copy()
    df = df.set_index("date").sort_index()

    monthly = (
        df.groupby("commodity_canonical")
        .resample("MS")["price"]
        .mean()
        .reset_index()
    )
    monthly["is_interpolated"] = False

    filled_frames = []
    for commodity, group in monthly.groupby("commodity_canonical"):
        group = group.set_index("date").sort_index()
        full_range = pd.date_range(group.index.min(), group.index.max(), freq="MS")
        group = group.reindex(full_range)
        was_missing = group["price"].isna()
        group["price"] = group["price"].interpolate(method="linear")
        group["is_interpolated"] = was_missing
        group["commodity_canonical"] = commodity
        group = group.reset_index().rename(columns={"index": "date"})
        filled_frames.append(group)

    return pd.concat(filled_frames, ignore_index=True) if filled_frames else monthly


def nbs_monthly_national(nbs_df: pd.DataFrame) -> pd.DataFrame:
    """
    NBS file already gives one national average per item per month -
    no resampling needed.
    """
    df = nbs_df.dropna(subset=["commodity_canonical", "price"]).copy()
    return (
        df[["date", "commodity_canonical", "price"]]
        .drop_duplicates(subset=["date", "commodity_canonical"])
        .sort_values(["commodity_canonical", "date"])
        .reset_index(drop=True)
    )


def combine_sources(wfp_monthly: pd.DataFrame, nbs_monthly: pd.DataFrame) -> pd.DataFrame:
    """Stack both sources into one long dataframe with a `source` column."""
    w = wfp_monthly[["date", "commodity_canonical", "price"]].copy()
    w["source"] = "WFP"
    n = nbs_monthly[["date", "commodity_canonical", "price"]].copy()
    n["source"] = "NBS"
    return pd.concat([w, n], ignore_index=True).sort_values(["commodity_canonical", "date"])