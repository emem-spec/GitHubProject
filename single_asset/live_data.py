import requests 
import pandas as pd 
from datetime import datetime

def get_eurusd_live() -> pd.Series:
    url="https://www.freeforexapi.com/api/live"
    params={"pairs": "EURUSD"}
    resp= requests.get(url,params=params, timeout=5)
    resp.raise_for_status()
    data=resp.json()

    quote=data["rates"]["EURUSD"]
    rate=float(quote["rate"])
    ts=int(quote["timestamp"])
    dt=datetime.utcfromtimestamp(ts)

    return pd.Series({"rate": rate, "timestamp": ts, "datetime": dt})
