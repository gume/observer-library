import numpy as np
import pandas as pd


def run(room, outdoor, heat, heat_kind="supply_temp", active=None, resample="15min", smooth_min=60, target=21.0,
        design_outdoor=(-10, -5, 0, 5, 10)):
    rs = lambda s: s.dropna().sort_index().astype(float).resample(resample).mean()
    df = pd.concat([rs(room).rename("T"), rs(outdoor).rename("To"), rs(heat).rename("H")], axis=1)
    df["To"] = df["To"].interpolate(limit=8, limit_area="inside")
    df["T"] = df["T"].interpolate(limit=4, limit_area="inside")
    df["Ts"] = df["T"].rolling(f"{int(smooth_min)}min", center=True, min_periods=1).mean()
    if heat_kind == "supply_temp":
        h = (df["H"] - df["Ts"]).clip(lower=0)
        if active is not None:
            act = rs(active).reindex(df.index).fillna(0) >= 0.5
            h = h.where(act, 0.0)
        df["h"] = h
    elif heat_kind in ("power", "on_off"):
        df["h"] = df["H"]
    else:
        return {"error": "heat_kind is supply_temp, power or on_off"}
    dt_h = pd.Timedelta(resample).total_seconds() / 3600
    df["dTdt"] = df["Ts"].diff().shift(-1) / dt_h
    d = df[["dTdt", "h", "Ts", "To"]].dropna()
    if len(d) < 24 or d["h"].std() == 0:
        return {"error": "not enough data with both heated and unheated periods (need variation of the heating drive)"}
    X = np.column_stack([d["h"], -(d["Ts"] - d["To"]), np.ones(len(d))])
    (a, b, c), *_ = np.linalg.lstsq(X, d["dTdt"].to_numpy(), rcond=None)
    if a <= 0 or b <= 0:
        return {"error": f"implausible fit (a={a:.4g}, b={b:.4g}): the data may lack heated periods or outdoor variation",
                "points": int(len(d))}
    pred = X @ np.array([a, b, c])
    ss = float(((d["dTdt"] - d["dTdt"].mean()) ** 2).sum())
    r2 = 1 - float(((d["dTdt"] - pred) ** 2).sum()) / ss if ss > 0 else None
    # Free-run simulation over the longest stretch without gaps.
    full = df[["T", "To", "H", "h"]].dropna()
    breaks = (full.index.to_series().diff() > pd.Timedelta(resample) * 1.5).cumsum()
    seg = full[breaks == breaks.value_counts().idxmax()]
    sim = np.empty(len(seg))
    sim[0] = seg["T"].iloc[0]
    for k in range(len(seg) - 1):
        hk = max(seg["H"].iloc[k] - sim[k], 0) if heat_kind == "supply_temp" and seg["h"].iloc[k] > 0 else seg["h"].iloc[k]
        sim[k + 1] = sim[k] + dt_h * (a * hk - b * (sim[k] - seg["To"].iloc[k]) + c)
    out = {"a": round(a, 5), "b": round(b, 5), "c": round(c, 4), "tau_h": round(1 / b, 1),
           "r2": None if r2 is None else round(r2, 3),
           "sim_rmse_K": round(float(np.sqrt(np.mean((sim - seg["T"].to_numpy()) ** 2))), 3),
           "sim_hours": round(len(seg) * dt_h, 1), "points": int(len(d))}
    hm, tom = float(d["h"].mean()), float(d["To"].mean())
    if heat_kind == "supply_temp":
        on = d[d["h"] > 0]
        if len(on):
            # Steady state with the circuit running at its mean supply temperature, at the mean outdoor temperature.
            ts_mean = float((on["h"] + on["Ts"]).mean())
            out["steady_state_K"] = round((a * ts_mean + b * tom + c) / (a + b), 2)
            out["steady_state_at"] = {"supply": round(ts_mean, 1), "outdoor": round(tom, 1)}
        out["required_supply"] = {str(t_o): round(target + (b * (target - t_o) - c) / a, 1) for t_o in design_outdoor}
        out["required_supply_target"] = target
    else:
        out["steady_state_K"] = round(tom + (a * hm + c) / b, 2)
    return out
