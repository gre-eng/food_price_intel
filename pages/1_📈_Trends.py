import streamlit as st
import plotly.graph_objects as go
from utils.data_service import load_all, available_commodities

st.set_page_config(page_title="Trends", layout="wide")
st.title("Food Price Trends")
st.caption("Drag the handles below the chart to zoom into a time range. Click legend items to show/hide a line. Hover anywhere on the chart to read exact values.")

data = load_all()
commodities = available_commodities()
labels = [label for _, label in commodities]
ids = [cid for cid, _ in commodities]

selected_label = st.selectbox("Commodity", labels, help="Only commodities with a verified WFP <-> NBS match are shown.")
selected_id = ids[labels.index(selected_label)]

combined = data["combined"]
subset = combined[combined["commodity_canonical"] == selected_id].sort_values("date")

if subset.empty:
    st.warning("No data available for this commodity.")
else:
    pivot = subset.pivot(index="date", columns="source", values="price")
    rolling = pivot.rolling(3, min_periods=1).mean()

    colors = {"WFP": "#2563eb", "NBS": "#dc2626"}

    fig = go.Figure()
    for src in pivot.columns:
        color = colors.get(src, "#888888")
        fig.add_trace(go.Scatter(
            x=pivot.index, y=pivot[src],
            mode="lines", name=f"{src} - actual",
            line=dict(width=1, color=color),
            opacity=0.35,
            hovertemplate="%{x|%b %Y}: ₦%{y:,.0f} per unit<extra>" + src + " actual</extra>",
        ))
        fig.add_trace(go.Scatter(
            x=rolling.index, y=rolling[src],
            mode="lines", name=f"{src} - 3-month average",
            line=dict(width=3, color=color),
            hovertemplate="%{x|%b %Y}: ₦%{y:,.0f} per unit<extra>" + src + " 3-mo avg</extra>",
        ))

    fig.update_layout(
        title=f"{selected_label} - price per standard unit (₦ Naira)",
        xaxis_title="Date",
        yaxis_title="Price (₦ Naira)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, x=0),
        height=550,
        template="plotly_white",
        xaxis=dict(
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(step="all", label="All"),
                ])
            ),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption("WFP = long-term wholesale market series (2002-present). NBS = monthly national average, "
               "Selected Food Price Watch (Jan 2025-present). Faint lines = raw monthly value; bold lines = 3-month rolling average.")