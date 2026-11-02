import pandas as pd

from tool import run


def test_degree_hours_per_day():
    t = pd.date_range("2026-01-01", periods=48, freq="1h", tz="UTC")
    out = pd.Series([5.0] * 24 + [20.0] * 24, index=t)
    d = run(out, base=15)
    assert list(d["degree_hours"]) == [240.0, 0.0] and list(d["coverage_h"]) == [24, 24]
    assert d["mean"].iloc[0] == 5.0
