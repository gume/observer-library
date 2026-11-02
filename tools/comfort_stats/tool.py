import numpy as np
import pandas as pd


def run(room, target, band=0.5, periods=None, tz="UTC"):
    T = room.dropna().sort_index().astype(float).resample("5min").mean().interpolate(limit=6, limit_area="inside").dropna()
    if isinstance(target, pd.Series):
        tg = target.dropna().sort_index().astype(float).reindex(T.index.union(target.index)).ffill().reindex(T.index)
    else:
        tg = pd.Series(float(target), index=T.index)
    df = pd.DataFrame({"T": T, "tg": tg}).dropna()
    hours = df.index.tz_convert(tz).hour if df.index.tz is not None else df.index.hour
    rows = []
    for name, (h0, h1) in (periods or {"all": [0, 24]}).items():
        sel = (hours >= h0) & (hours < h1) if h0 < h1 else (hours >= h0) | (hours < h1)
        d = df[sel]
        if d.empty:
            rows.append({"period": name, "hours": 0})
            continue
        dt_h = 5 / 60
        diff = d["T"] - d["tg"]
        rows.append({"period": name, "hours": round(len(d) * dt_h, 1), "mean": round(d["T"].mean(), 2),
                     "min": round(d["T"].min(), 2), "max": round(d["T"].max(), 2),
                     "in_band_pct": round(100 * (diff.abs() <= band).mean(), 1),
                     "below_pct": round(100 * (diff < -band).mean(), 1),
                     "above_pct": round(100 * (diff > band).mean(), 1),
                     "degree_hours_below": round(float((-(diff + band)).clip(lower=0).sum() * dt_h), 2)})
    return pd.DataFrame(rows)
