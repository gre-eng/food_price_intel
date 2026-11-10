import streamlit as st
from utils.data_service import load_all, available_commodities

st.set_page_config(page_title="Data Explorer", layout="wide")
st.title("Data Explorer")

data = load_all()
combined = data["combined"].copy()
combined["year"] = combined["date"].dt.year

commodities = available_commodities()
labels = ["All"] + [label for _, label in commodities]
ids = [cid for cid, _ in commodities]

years = sorted(combined["year"].dropna().unique().tolist())

col1, col2, col3 = st.columns(3)
with col1:
    year_choice = st.selectbox("Year", ["All"] + years)
with col2:
    commodity_choice = st.selectbox("Commodity", labels)
with col3:
    source_choice = st.selectbox("Source", ["All", "WFP", "NBS"])

filtered = combined.copy()
if year_choice != "All":
    filtered = filtered[filtered["year"] == year_choice]
if commodity_choice != "All":
    cid = ids[labels.index(commodity_choice) - 1]
    filtered = filtered[filtered["commodity_canonical"] == cid]
if source_choice != "All":
    filtered = filtered[filtered["source"] == source_choice]

label_map = dict(commodities)
filtered_display = filtered.copy()
filtered_display["commodity"] = filtered_display["commodity_canonical"].map(label_map)

st.write(f"{len(filtered_display)} rows")
st.dataframe(
    filtered_display[["date", "commodity", "source", "price"]].sort_values("date"),
    use_container_width=True,
)

st.caption("Region/state-level filtering is not available here: the matched WFP/NBS comparison does not "
           "carry a region column - that detail exists separately in each file's 'Zone All item' sheet, "
           "which is not yet wired into this view.")