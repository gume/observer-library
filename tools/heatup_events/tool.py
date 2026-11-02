import numpy as np
import pandas as pd


def run(room, heating, target=None, min_off_min=60, window_h=6, rise_threshold=0.2, smooth_min=20):
    T = room.dropna().sort_index().astype(float).resample("5min").mean().interpolate(limit=6, limit_area="inside")
    T = T.rolling(f"{int(smooth_min)}min", center=True, min_periods=1).mean()
    on = (heating.dropna().sort_index().astype(float) >= 0.5).astype(int)
    starts, off_since, prev = [], None, None
    for t, v in on.items():
        if v == 0 and (prev is None or prev == 1):
            off_since = t
        if v == 1 and prev == 0 and off_since is not None and (t - off_since).total_seconds() >= min_off_min * 60:
            starts.append(t)
        prev = v
    rows = []
    for s in starts:
        end = s + pd.Timedelta(hours=window_h)
        w = T.loc[s:end].dropna()
        if len(w) < 6:
            continue
        t0 = float(w.iloc[0])
        running_min = w.cummin()
        rising = w[(w - running_min) >= rise_threshold]
        delay = (rising.index[0] - s).total_seconds() / 60 if len(rising) else np.nan
        rate = np.nan
        if len(rising):
            lo_t = w.loc[:rising.index[0]].idxmin()
            peak_t = w.loc[lo_t:].idxmax()
            seg = w.loc[lo_t:peak_t]
            if len(seg) >= 3:
                x = (seg.index - seg.index[0]).total_seconds() / 3600
                rate = float(np.polyfit(x, seg.to_numpy(), 1)[0])
        h_on = on.loc[s:end]
        ran = h_on.reindex(pd.date_range(s, end, freq="1min"), method="ffill").fillna(0).mean() * window_h
        row = {"start": s, "room_at_start": round(t0, 2), "delay_min": None if np.isnan(delay) else round(delay, 0),
               "rate_K_per_h": None if np.isnan(rate) else round(rate, 3), "rise_K": round(float(w.max()) - t0, 2),
               "peak": round(float(w.max()), 2), "heating_h": round(float(ran), 2), "time_to_target_min": np.nan}
        if target is not None:
            tg = target.sort_index().ffill().reindex(w.index, method="ffill") if isinstance(target, pd.Series) \
                else pd.Series(float(target), index=w.index)
            hit = w[w >= tg]
            if len(hit):
                row["time_to_target_min"] = round((hit.index[0] - s).total_seconds() / 60, 0)
        rows.append(row)
    return pd.DataFrame(rows, columns=["start", "room_at_start", "delay_min", "rate_K_per_h", "rise_K", "peak",
                                       "heating_h", "time_to_target_min"])
