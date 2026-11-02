import numpy as np
import pandas as pd

from tool import run


def simulate(tau=40.0, g=0.05, hours=72, heated=None):
    t = pd.date_range("2026-01-01", periods=hours * 60, freq="1min", tz="UTC")
    out = 2 + 5 * np.sin(np.arange(len(t)) / 60 / 24 * 2 * np.pi)
    T = np.empty(len(t))
    T[0] = 21.0
    for k in range(len(t) - 1):
        heat = 0.8 if heated is not None and heated[k] else 0.0
        T[k + 1] = T[k] + (-(T[k] - out[k]) / tau + g + heat) / 60
    return pd.Series(np.round(T, 1), index=t), pd.Series(out, index=t)


def test_recovers_time_constant_and_gains():
    room, out = simulate()
    r = run(room, out)
    assert abs(r["tau_h"] - 40) < 4 and abs(r["gains_K_per_h"] - 0.05) < 0.03 and r["r2"] > 0.5


def test_mask_excludes_heated_periods():
    n = 72 * 60
    heated = (np.arange(n) // 60) % 12 < 3                    # heated 3 h every 12 h
    room, out = simulate(heated=heated)
    mask = pd.Series(~heated, index=room.index)
    r = run(room, out, mask=mask)
    assert abs(r["tau_h"] - 40) < 6
    assert "error" in run(room, out, min_diff=99)
