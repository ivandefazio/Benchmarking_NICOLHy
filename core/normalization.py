# core/normalization.py
import pandas as pd

def normalize(series, method="minmax", direction="maximize", target=None):
    series = series.astype(float)

    if method == "minmax":
        min_val, max_val = series.min(), series.max()
        if max_val == min_val:
            norm = pd.Series(100, index=series.index)
        else:
            norm = (series - min_val) / (max_val - min_val) * 100
        if direction == "minimize":
            norm = 100 - norm

    elif method == "target":
        if target is None or target == 0:
            return pd.Series(0, index=series.index)
        raw = (series / target) * 100 if direction == "maximize" else (target / series) * 100
        denom = raw.max() - raw.min()
        norm = (raw - raw.min()) / denom * 100 if denom != 0 else pd.Series(100, index=series.index)

    elif method == "qualitative":
        norm = series.map({1: 0, 2: 25, 3: 50, 4: 75, 5: 100})

    return norm