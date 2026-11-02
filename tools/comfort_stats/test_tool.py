import numpy as np
import pandas as pd

from tool import run


def test_band_shares_degree_hours_and_periods():
    t = pd.date_range("2026-01-01", periods=24 * 12, freq="5min", tz="UTC")
    hours = t.hour
    room = pd.Series(np.where(hours < 6, 19.0, 21.0), index=t)            # cold night 0-6, fine day
    r = run(room, 21.0, band=0.5, periods={"night": [22, 6], "day": [6, 22]}).set_index("period")
    assert r.loc["day", "in_band_pct"] == 100.0 and r.loc["day", "degree_hours_below"] == 0
    assert r.loc["night", "below_pct"] == 75.0                            # 6 of 8 night hours too cold
    assert abs(r.loc["night", "degree_hours_below"] - 6 * 1.5) < 0.01


def test_target_series_and_time_zone():
    t = pd.date_range("2026-01-01", periods=48, freq="1h", tz="UTC")
    room = pd.Series(20.0, index=t)
    target = pd.Series([20.0, 22.0], index=t[[0, 24]])
    r = run(room, target).iloc[0]
    assert 45 < r.in_band_pct < 55
    local = run(room, 20, periods={"morning": [6, 9]}, tz="Europe/Budapest").iloc[0]
    assert local.hours > 0
