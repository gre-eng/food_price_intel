import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_service import load_all, available_commodities
from utils.forecasting import forecast_holt_winters, forecast_arima

st.set_page_config(page_title="Forecast AI", layout="wide")
st.title("Forecast AI")
st.caption("Drag the timeline below the chart to zoom. Click legend items to toggle lines. "
           "Forecast is a statistical projection of historical patterns only - not a guarantee.")

data = load_all()
commodities = available_commodities()
labels = [label for _, label in commodities]
ids = [cid for cid, _ in commodities]

c1, c2, c3 = st.columns(3)
with c1:
    selected_label = st.selectbox("Commodity", labels)
with c2:
    source_choice = st.radio("Series", ["WFP (long-term)", "NBS (short-term)"], horizontal=True)
with c3:
    method = st.radio("Method", ["Holt-Winters", "ARIMA"], horizontal=True,
                       help="ARIMA shows a real shaded confidence band. Holt-Winters does not produce one natively in statsmodels, so none is faked here.")

periods = st.slider("Months to project forward", 1, 12, 6)
selected_id = ids[labels.index(selected_label)]
source_key = "WFP" if source_choice.startswith("WFP") else "NBS"

combined = data["combined"]
series_df = combined[
    (combined["commodity_canonical"] == selected_id) & (combined["source"] == source_key)
].sort_values("date")

if series_df.empty:
    st.warning("No data available for this commodity/source combination.")
else:
    series = series_df.set_index("date")["price"]
    series.index = pd.DatetimeIndex(series.index)

    min_required = 6
    if len(series) < min_required:
        st.warning(f"Only {len(series)} data points available - too few for a reliable forecast (need at least {min_required}).")
    else:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=series.index, y=series.values,
                mode="lines", name="Historical",
                line=dict(color="#2563eb", width=2.5),
                hovertemplate="%{x|%b %Y}: ₦%{y:,.0f} per unit<extra>Historical</extra>",
            ))

            if method == "Holt-Winters":
                forecast, used_seasonal = forecast_holt_winters(series, periods=periods)
                if not used_seasonal:
                    st.info("Not enough history for a seasonal model - used trend-only Holt-Winters instead.")
                fig.add_trace(go.Scatter(
                    x=forecast.index, y=forecast.values,
                    mode="lines+markers", name="Forecast",
                    line=dict(color="#dc2626", width=2.5, dash="dash"),
                    hovertemplate="%{x|%b %Y}: ₦%{y:,.0f} per unit<extra>Forecast</extra>",
                ))
            else:
                pred_mean, conf_int = forecast_arima(series, periods=periods)
                lower = conf_int.iloc[:, 0]
                upper = conf_int.iloc[:, 1]

                fig.add_trace(go.Scatter(
                    x=list(pred_mean.index) + list(pred_mean.index[::-1]),
                    y=list(upper.values) + list(lower.values[::-1]),
                    fill="toself", fillcolor="rgba(220,38,38,0.15)",
                    line=dict(color="rgba(255,255,255,0)"),
                    name="Confidence band", showlegend=True,
                    hoverinfo="skip",
                ))
                fig.add_trace(go.Scatter(
                    x=pred_mean.index, y=pred_mean.values,
                    mode="lines+markers", name="Forecast",
                    line=dict(color="#dc2626", width=2.5, dash="dash"),
                    hovertemplate="%{x|%b %Y}: ₦%{y:,.0f} per unit<extra>Forecast</extra>",
                ))

            fig.update_layout(
                title=f"{selected_label} ({source_choice}) - {periods}-month forecast",
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
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(count=5, label="5y", step="year", stepmode="backward"),
                            dict(step="all", label="All"),
                        ])
                    ),
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Forecast could not be computed: {e}")