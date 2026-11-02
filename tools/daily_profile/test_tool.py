import numpy as np
import pandas as pd

from tool import run


def test_hourly_profile_and_time_zone():
    t = pd.date_range("2026-01-05", periods=7 * 24 * 4, freq="15min", tz="UTC")
    v = 20 + np.where(t.hour == 3, -2.0, 0.0)
    p = run(pd.Series(v, index=t))
    assert p.loc[3, "mean"] == 18.0 and p.loc[4, "mean"] == 20.0 and p.loc[3, "days"] == 7
    local = run(pd.Series(v, index=t), tz="Europe/Budapest")          # UTC+1 in January
    assert local.loc[4, "mean"] == 18.0
    wk = run(pd.Series(v, index=t), by="weekday_hour")
    assert len(wk) == 7 * 24
