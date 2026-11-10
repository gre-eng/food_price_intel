import streamlit as st
import pandas as pd
from utils.data_service import load_all, available_commodities
from utils.nbs_loader import get_unmapped_nbs_commodities
from utils.wfp_loader import get_unmapped_wfp_commodities

st.set_page_config(page_title="Food Price Intelligence System", layout="wide")

st.title("🥇 Food Price Intelligence System (Nigeria)")
st.caption("Long-term trend: WFP VAM | Short-term movement: NBS Selected Food Price Watch")

data = load_all()

unmapped_wfp = get_unmapped_wfp_commodities(data["wfp_raw"])
unmapped_nbs = get_unmapped_nbs_commodities(data["nbs_raw"])

if unmapped_wfp or unmapped_nbs:
    with st.expander(f"⚠️ {len(unmapped_wfp) + len(unmapped_nbs)} commodity names are NOT mapped between sources (see Data Sources tab for full list)"):
        st.write(f"WFP-only (no NBS match): {len(unmapped_wfp)}")
        st.write(f"NBS-only (no WFP match): {len(unmapped_nbs)}")

commodities = available_commodities()
labels = [label for _, label in commodities]
ids = [cid for cid, _ in commodities]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Long-term trend (WFP)")
    wfp_pivot = data["wfp_monthly"].pivot(index="date", columns="commodity_canonical", values="price")
    wfp_pivot.columns = [dict(commodities).get(c, c) for c in wfp_pivot.columns]
    st.line_chart(wfp_pivot)

with col2:
    st.subheader("Short-term movement (NBS)")
    nbs_pivot = data["nbs_monthly"].pivot(index="date", columns="commodity_canonical", values="price")
    nbs_pivot.columns = [dict(commodities).get(c, c) for c in nbs_pivot.columns]
    st.line_chart(nbs_pivot)

st.subheader("Summary statistics (matched commodities only)")
summary = data["combined"].groupby(["commodity_canonical", "source"])["price"].describe()
summary.index = summary.index.set_levels(
    [dict(commodities).get(c, c) for c in summary.index.levels[0]], level=0
)
st.dataframe(summary)

st.subheader("Bar chart: latest available price by commodity")
latest = data["combined"].sort_values("date").groupby(["commodity_canonical", "source"]).tail(1)
latest = latest.copy()
latest["label"] = latest["commodity_canonical"].map(dict(commodities))
st.bar_chart(latest.pivot(index="label", columns="source", values="price"))