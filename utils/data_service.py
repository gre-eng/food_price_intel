"""
Single source of truth for loading data into the Streamlit app.
"""

import streamlit as st
from utils.wfp_loader import load_wfp, filter_mapped as filter_wfp
from utils.nbs_loader import load_all_nbs, filter_mapped as filter_nbs
from utils.alignment import wfp_monthly_national_average, nbs_monthly_national, combine_sources
from utils.commodity_mapper import MATCHED_PAIRS, get_canonical_label

WFP_CSV_PATH = "data/wfp_food_prices_nga.csv"
NBS_DIR_PATH = "data/nbs_monthly"


@st.cache_data
def load_all():
    wfp_raw = load_wfp(WFP_CSV_PATH)
    nbs_raw = load_all_nbs(NBS_DIR_PATH)

    wfp_mapped = filter_wfp(wfp_raw)
    nbs_mapped = filter_nbs(nbs_raw)

    wfp_monthly = wfp_monthly_national_average(wfp_mapped)
    nbs_monthly = nbs_monthly_national(nbs_mapped)

    combined = combine_sources(wfp_monthly, nbs_monthly)

    return {
        "wfp_raw": wfp_raw,
        "nbs_raw": nbs_raw,
        "wfp_monthly": wfp_monthly,
        "nbs_monthly": nbs_monthly,
        "combined": combined,
    }


def available_commodities():
    """Only commodities that exist in the verified crosswalk."""
    return [(cid, get_canonical_label(cid)) for cid in MATCHED_PAIRS.keys()]