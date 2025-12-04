from pathlib import Path
import pandas as pd
from single_asset.live_data import get_eurusd_live

DATA_FILE = Path("data/eurusd_live.csv")

def main():
    quote = get_eurusd_live()
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if DATA_FILE.exists():
        df=pd.read_csv(DATA_FILE, parse_dates=["datetime"])
    else :
        df=pd.DataFrame(columns=["rate", "timestamp", "datetime"])

    df=pd.concat([df, quote.to_frame().T], ignore_index=True)
    df=df.drop_duplicates(subset=["timestamp"]).sort_values("datetime")
    df.to_csv(DATA_FILE, index=false)



if __name__ == "__main__":
    main()
