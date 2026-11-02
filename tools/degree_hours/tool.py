import pandas as pd


def run(outdoor, base=15.0, tz="UTC"):
    s = outdoor.dropna().sort_index().astype(float)
    h = s.resample("1h").mean().interpolate(limit=2, limit_area="inside").dropna()
    local = h.tz_convert(tz) if h.index.tz is not None else h
    day = local.index.normalize()
    g = local.groupby(day)
    out = pd.DataFrame({"mean": g.mean().round(2), "min": g.min().round(2), "max": g.max().round(2),
                        "degree_hours": (base - local).clip(lower=0).groupby(day).sum().round(1),
                        "coverage_h": g.count()})
    out.index.name = "date"
    return out
