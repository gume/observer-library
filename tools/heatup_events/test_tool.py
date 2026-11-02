import numpy as np
import pandas as pd

from tool import run


def test_delay_rate_and_target():
    t = pd.date_range("2026-01-01", periods=12 * 60, freq="1min", tz="UTC")
    heat = pd.Series(np.where((np.arange(len(t)) >= 120) & (np.arange(len(t)) < 360), 1, 0), index=t)
    T = np.full(len(t), 19.0)
    for k in range(1, len(t)):                                  # 30 min dead time, then +0.6 K/h while on
        T[k] = T[k - 1] + (0.6 / 60 if 150 <= k < 390 else -0.1 / 60)
    room = pd.Series(np.round(T, 1), index=t)
    ev = run(room, heat, target=20.5)
    assert len(ev) == 1
    e = ev.iloc[0]
    assert 20 <= e.delay_min <= 60 and 0.45 < e.rate_K_per_h < 0.75
    assert 3.5 <= e.heating_h <= 4.2 and e.rise_K > 1.5
    assert 150 <= e.time_to_target_min <= 330


def test_requires_off_time_before_a_start():
    t = pd.date_range("2026-01-01", periods=300, freq="1min", tz="UTC")
    heat = pd.Series(np.where(np.arange(300) % 40 < 20, 1, 0), index=t)     # 20 min off only
    assert run(pd.Series(20.0, index=t), heat, min_off_min=60).empty
