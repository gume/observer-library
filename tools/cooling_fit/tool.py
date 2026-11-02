import numpy as np
import pandas as pd


def run(room, outdoor, mask=None, resample="15min", smooth_min=60, min_diff=3.0, at_diff=10.0):
    r = room.dropna().sort_index().astype(float).resample(resample).mean()
    o = outdoor.dropna().sort_index().astype(float).resample(resample).mean().interpolate(limit=8, limit_area="inside")
    df = pd.concat([r.rename("room"), o.rename("out")], axis=1)
    df["room"] = df["room"].interpolate(limit=4, limit_area="inside")
    df["room"] = df["room"].rolling(f"{int(smooth_min)}min", center=True, min_periods=1).mean()
    dt_h = pd.Timedelta(resample).total_seconds() / 3600
    df["dTdt"] = df["room"].diff().shift(-1) / dt_h                     # forward difference over one bin
    df["diff"] = df["room"] - df["out"]
    keep = df["diff"] >= min_diff
    if mask is not None:
        m = mask.dropna().sort_index().astype(float).resample(resample).min()   # whole bin not heated
        keep &= m.reindex(df.index).fillna(0) >= 1
    d = df[keep].dropna()
    if len(d) < 12:
        return {"error": f"only {len(d)} usable points (need 12): longer unheated periods or a smaller min_diff"}
    X = np.column_stack([-d["diff"].to_numpy(), np.ones(len(d))])
    (k, g), *_ = np.linalg.lstsq(X, d["dTdt"].to_numpy(), rcond=None)
    if k <= 0:
        return {"error": "no cooling found: the room does not cool towards the outdoor temperature in these periods "
                         "(heated, or other heat sources dominate)", "points": int(len(d))}
    pred = X @ np.array([k, g])
    ss = float(((d["dTdt"] - d["dTdt"].mean()) ** 2).sum())
    r2 = 1 - float(((d["dTdt"] - pred) ** 2).sum()) / ss if ss > 0 else None
    return {"tau_h": round(1 / k, 1), "loss_per_h": round(k, 5), "gains_K_per_h": round(g, 4),
            "cooling_K_per_h_at": {"diff_K": at_diff, "rate": round(k * at_diff - g, 3)},
            "r2": None if r2 is None else round(r2, 3), "points": int(len(d)), "hours": round(len(d) * dt_h, 1),
            "mean_diff_K": round(float(d["diff"].mean()), 2)}
