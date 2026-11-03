import numpy as np
import pandas as pd


def run(value, setpoint, position=None, supply=None, band_k=0.5, supply_margin_k=5.0, move_eps=0.05):
    if not isinstance(setpoint, pd.Series):
        setpoint = pd.Series(float(setpoint), index=value.index)
    cols = {"v": value, "sp": setpoint}
    if position is not None:
        cols["pos"] = position
    if supply is not None:
        cols["sup"] = supply
    df = pd.concat({k: pd.to_numeric(s, errors="coerce") for k, s in cols.items()}, axis=1).sort_index()
    df["sp"] = df["sp"].ffill()
    df = df.dropna(subset=["v", "sp"])
    if len(df) < 3:
        return {"error": "fewer than 3 points with a value and a setpoint"}
    t = (df.index - df.index[0]).total_seconds().to_numpy() if isinstance(df.index, pd.DatetimeIndex) \
        else np.asarray(df.index, float) - float(df.index[0])
    hours = float(t[-1] - t[0]) / 3600 or float("nan")
    v, sp = df["v"].to_numpy(float), df["sp"].to_numpy(float)
    reached, waiting, step_t, over = [], True, t[0], 0.0
    after = np.zeros(len(v), bool)
    for i in range(len(v)):
        if i and sp[i] != sp[i - 1]:
            if waiting:
                reached.append(None)
            waiting, step_t = True, t[i]
        if waiting and abs(v[i] - sp[i]) <= band_k:
            reached.append(float(t[i] - step_t))
            waiting = False
        if not waiting:
            after[i] = True
            over = max(over, v[i] - sp[i])
    if waiting:
        reached.append(None)
    err = (v - sp)[after]
    out = {"hours": round(hours, 3),
           "rmse_k": round(float(np.sqrt(np.mean(err ** 2))), 3) if len(err) else None,
           "rmse_supplied_k": None,
           "overshoot_k": round(float(over), 2),
           "time_to_setpoint_s": reached[0],
           "mean_time_to_setpoint_s": round(float(np.mean([r for r in reached if r is not None]))) if any(
               r is not None for r in reached) else None,
           "setpoints": len(reached), "never_reached": sum(1 for r in reached if r is None),
           "in_band_share": round(float(np.mean(np.abs(v - sp) <= band_k)), 3)}
    if "sup" in df:
        ok = after & (df["sup"].to_numpy(float) >= sp + supply_margin_k)
        e = (v - sp)[ok]
        out["rmse_supplied_k"] = round(float(np.sqrt(np.mean(e ** 2))), 3) if len(e) else None
    if "pos" in df:
        p = df["pos"].interpolate(limit_area="inside").to_numpy(float)
        if np.nanmax(p) <= 1.0:
            p = p * 100.0
        d = np.diff(p)
        d = np.where(np.isfinite(d), d, 0.0)
        direction = np.where(d > move_eps, 1, np.where(d < -move_eps, -1, 0))
        starts = reversals = 0
        prev = last = 0
        for s in direction:
            if s and s != prev:
                starts += 1
                if last and s != last:
                    reversals += 1
                last = s
            prev = s
        out.update(travel_pct_h=round(float(np.sum(np.abs(d[direction != 0]))) / hours, 1),
                   starts_h=round(starts / hours, 1), reversals_h=round(reversals / hours, 1))
    return out
