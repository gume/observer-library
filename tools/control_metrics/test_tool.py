import numpy as np
import pandas as pd

from tool import run


def test_heat_up_overshoot_and_effort():
    idx = pd.date_range("2026-01-01", periods=721, freq="10s", tz="UTC")          # 2 h
    t = np.arange(721) * 10.0
    v = np.where(t < 600, 25 + t / 60, 35 + 1.0 * np.exp(-(t - 600) / 300))      # reaches 35 after 10 min, +1 K
    pos = np.concatenate([np.linspace(40, 70, 60), np.full(60, 70), np.linspace(70, 55, 30), np.full(571, 55)])
    r = run(pd.Series(v, idx), 35.0, pd.Series(pos, idx), band_k=0.5)
    assert r["time_to_setpoint_s"] == 570 and r["setpoints"] == 1 and r["never_reached"] == 0
    assert 0.9 < r["overshoot_k"] <= 1.0
    assert abs(r["travel_pct_h"] - 45 / 2) < 1 and r["starts_h"] == 1.0 and r["reversals_h"] == 0.5


def test_setpoint_change_and_supply():
    idx = pd.date_range("2026-01-01", periods=360, freq="10s", tz="UTC")
    sp = pd.Series(np.where(np.arange(360) < 180, 35.0, 30.0), idx)
    v = pd.Series(np.where(np.arange(360) < 200, 35.0, 30.0), idx)
    sup = pd.Series(np.where(np.arange(360) < 300, 60.0, 31.0), idx)
    r = run(v, sp, supply=sup)
    assert r["setpoints"] == 2 and r["mean_time_to_setpoint_s"] == 100      # 0 s and 200 s
    assert r["rmse_supplied_k"] == 0.0 and r["rmse_k"] == 0.0


def test_too_little_data():
    idx = pd.date_range("2026-01-01", periods=2, freq="10s", tz="UTC")
    assert "error" in run(pd.Series([1.0, 2.0], idx), 30)
