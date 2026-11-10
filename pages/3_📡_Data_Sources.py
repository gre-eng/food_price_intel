import streamlit as st
from utils.data_service import load_all
from utils.commodity_mapper import MATCHED_PAIRS

st.set_page_config(page_title="Data Sources", layout="wide")
st.title("Data Sources")

data = load_all()

st.subheader("WFP (long-term)")
st.write(f"Rows loaded: {len(data['wfp_raw']):,}")
st.write(f"Date range: {data['wfp_raw']['date'].min().date()} to {data['wfp_raw']['date'].max().date()}")

st.subheader("NBS (short-term)")
st.write(f"Rows loaded: {len(data['nbs_raw']):,}")
if not data["nbs_raw"].empty:
    st.write(f"Date range: {data['nbs_raw']['date'].min().date()} to {data['nbs_raw']['date'].max().date()}")

st.subheader("Commodity crosswalk - confirmed matches")
matched_table = [
    {"Commodity": cid, "WFP name": v["wfp"], "NBS name": v["nbs"]}
    for cid, v in MATCHED_PAIRS.items()
]
st.dataframe(matched_table, use_container_width=True)

st.subheader("Data handling notes")
st.markdown("""
- **Frequency alignment**: WFP is per-market/per-date; resampled to monthly national average.
  NBS already reports one monthly national average per item, used as-is.
- **Missing value treatment**: WFP monthly gaps are filled via linear interpolation
  (flagged internally as `is_interpolated`, never shown as if it were a reported value).
- **Sheet-name caveat**: 2 of the 16 uploaded NBS files have a mislabeled internal sheet tab
  name ("Selected Food Dec 2024") even though the data and filename are for a different month.
  The loader reads the report month from the column header text instead of the sheet name.
""")