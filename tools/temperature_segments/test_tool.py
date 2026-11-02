import numpy as np
import pandas as pd

from tool import run


def test_flat_rise_fall_with_rates():
    t = pd.date_range("2026-01-01", periods=11 * 60, freq="1min", tz="UTC")
    v = np.r_[np.full(120, 20.0), np.linspace(20, 22, 180), np.linspace(22, 20.5, 360)]
    v = np.round(v + np.random.default_rng(0).normal(0, 0.03, len(v)), 1)     # 0.1 K steps and noise
    seg = run(pd.Series(v, index=t))
    kinds = list(seg["kind"])
    assert kinds[:3] == ["flat", "rising", "falling"]
    rise = seg[seg.kind == "rising"].iloc[0]
    fall = seg[seg.kind == "falling"].iloc[0]
    assert 0.5 < rise.rate_K_per_h < 0.85 and 1.6 < rise.delta_K < 2.2
    assert -0.32 < fall.rate_K_per_h < -0.18


def test_noise_only_is_flat():
    t = pd.date_range("2026-01-01", periods=600, freq="1min", tz="UTC")
    v = 21 + np.random.default_rng(1).normal(0, 0.05, 600)
    assert set(run(pd.Series(v, index=t))["kind"]) == {"flat"}
