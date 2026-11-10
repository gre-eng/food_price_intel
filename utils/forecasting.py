"""
Forecasting utilities using statsmodels Holt-Winters and ARIMA.
"""

import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA


def forecast_holt_winters(series: pd.Series, periods: int = 6, seasonal_periods: int = 12):
    """
    series: pd.Series indexed by monthly date, no NaNs.
    Falls back to non-seasonal trend-only model if not enough data.
    """
    used_seasonal = True
    if len(series) >= 2 * seasonal_periods:
        model = ExponentialSmoothing(
            series, trend="add", seasonal="add", seasonal_periods=seasonal_periods
        ).fit()
    else:
        used_seasonal = False
        model = ExponentialSmoothing(series, trend="add", seasonal=None).fit()

    forecast = model.forecast(periods)
    return forecast, used_seasonal


def forecast_arima(series: pd.Series, periods: int = 6, order=(1, 1, 1)):
    model = ARIMA(series, order=order).fit()
    result = model.get_forecast(periods)
    return result.predicted_mean, result.conf_int()