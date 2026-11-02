import numpy as np
import pandas as pd


def _runs(labels):
    out, start = [], 0
    for i in range(1, len(labels) + 1):
        if i == len(labels) or labels[i] != labels[start]:
            out.append((start, i - 1, labels[start]))
            start = i
    return out


def run(series, resample="5min", smooth_min=30, rate_threshold=0.1, min_duration_min=45, min_change=0.2):
    s = series.dropna().sort_index().astype(float)
    if len(s) < 3:
        return pd.DataFrame(columns=["start", "end", "kind", "duration_h", "start_value", "end_value",
                                     "delta_K", "rate_K_per_h", "max_rate_K_per_h"])
    g = s.resample(resample).mean().interpolate(limit=6, limit_area="inside")
    sm = g.rolling(f"{int(smooth_min)}min", center=True, min_periods=1).mean()
    dt_h = pd.Timedelta(resample).total_seconds() / 3600
    w = max(1, int(round(smooth_min / 60 / dt_h / 2)))          # half window in bins
    slope = (sm.shift(-w) - sm.shift(w)) / (2 * w * dt_h)       # slope over the whole smoothing window
    slope = slope.fillna(sm.diff() / dt_h)
    vals, idx, sl = sm.to_numpy(), sm.index, slope.to_numpy()
    labels = np.where(sl > rate_threshold, 1, np.where(sl < -rate_threshold, -1, 0))
    labels[np.isnan(sl)] = 0
    # Too short or too small movements are flat; then join neighbours of the same kind.
    for a, b, lab in _runs(list(labels)):
        if lab != 0:
            dur_min = (idx[b] - idx[max(a - 1, 0)]).total_seconds() / 60
            if dur_min < min_duration_min or abs(vals[b] - vals[max(a - 1, 0)]) < min_change:
                labels[a:b + 1] = 0
    # Short flat pauses between two movements belong to the movement before them.
    runs = _runs(list(labels))
    for i in range(1, len(runs) - 1):
        a, b, lab = runs[i]
        if lab == 0 and runs[i - 1][2] != 0 and runs[i + 1][2] != 0:
            if (idx[b] - idx[a]).total_seconds() / 60 < min_duration_min:
                labels[a:b + 1] = runs[i - 1][2]          # a short turn-around plateau ends the previous segment
    rows = []
    names = {1: "rising", -1: "falling", 0: "flat"}
    for a, b, lab in _runs(list(labels)):
        a0 = max(a - 1, 0)                                    # a segment starts where the previous ends
        if np.isnan(vals[a0]) or np.isnan(vals[b]):
            continue
        dur_h = (idx[b] - idx[a0]).total_seconds() / 3600
        delta = vals[b] - vals[a0]
        seg = sl[a:b + 1]
        rows.append({"start": idx[a0], "end": idx[b], "kind": names[lab], "duration_h": round(dur_h, 2),
                     "start_value": round(vals[a0], 2), "end_value": round(vals[b], 2), "delta_K": round(delta, 2),
                     "rate_K_per_h": round(delta / dur_h, 3) if dur_h > 0 else np.nan,
                     "max_rate_K_per_h": round(float(np.nanmax(np.abs(seg))), 3) if np.isfinite(seg).any() else np.nan})
    return pd.DataFrame(rows)
