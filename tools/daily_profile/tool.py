import pandas as pd


def run(series, by="hour", tz="UTC", resample="15min"):
    s = series.dropna().sort_index().astype(float).resample(resample).mean().dropna()
    local = s.tz_convert(tz) if s.index.tz is not None else s
    keys = [local.index.hour] if by == "hour" else [local.index.dayofweek, local.index.hour]
    names = ["hour"] if by == "hour" else ["weekday", "hour"]
    g = local.groupby(keys)
    out = pd.DataFrame({"mean": g.mean().round(2), "p10": g.quantile(0.1).round(2), "p90": g.quantile(0.9).round(2),
                        "days": local.groupby(keys).apply(lambda x: x.index.normalize().nunique())})
    out.index.names = names
    return out
