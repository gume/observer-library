import numpy as np
import pandas as pd

from tool import run


def simulate(a=0.02, b=0.025, c=0.02, days=5):
    n = days * 24 * 60
    t = pd.date_range("2026-01-01", periods=n, freq="1min", tz="UTC")
    out = 0 + 4 * np.sin(np.arange(n) / 1440 * 2 * np.pi)
    on = (np.arange(n) // 60) % 8 < 4                         # radiator circuit 4 h on, 4 h off
    supply = np.where(on, 50.0, np.nan)
    T = np.empty(n)
    T[0] = 20.0
    for k in range(n - 1):
        h = (supply[k] - T[k]) if on[k] else 0.0
        T[k + 1] = T[k] + (a * h - b * (T[k] - out[k]) + c) / 60
    idx = lambda v: pd.Series(v, index=t)
    return idx(np.round(T, 1)), idx(out), idx(supply), idx(on.astype(float))


def test_recovers_gain_loss_and_required_supply():
    room, out, supply, on = simulate()
    r = run(room, out, supply, active=on)
    assert abs(r["a"] - 0.02) < 0.004 and abs(r["b"] - 0.025) < 0.005
    assert r["sim_rmse_K"] < 0.6
    need = r["required_supply"]["0"]                          # 21 = (a*Ts + c)/(a + b) at 0 °C
    exact = 21 + (0.025 * 21 - 0.02) / 0.02
    assert abs(need - exact) < 4


def test_on_off_kind_and_errors():
    room, out, supply, on = simulate(days=3)
    r = run(room, out, on, heat_kind="on_off")
    assert r["a"] > 0 and r["b"] > 0
    assert "error" in run(room, out, on * 0, heat_kind="on_off")
