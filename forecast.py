import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from src.aqi_gis.cleaning import load_and_clean

def main():
    parser = argparse.ArgumentParser(description="Educational AQI baseline forecast")
    parser.add_argument("--country", default="Pakistan")
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()
    if args.days < 1:
        parser.error("--days must be at least 1")

    data_path = Path("data/raw/data_date.csv")
    if not data_path.exists():
        raise SystemExit("Dataset missing: add data/raw/data_date.csv first.")
    df = load_and_clean(data_path)
    series = (df[df["Country"].str.casefold() == args.country.casefold()]
                .set_index("Date")["AQI Value"].sort_index().asfreq("D"))
    if series.dropna().empty:
        raise SystemExit(f"No observations found for country: {args.country}")
    series = series.interpolate(limit=7).ffill().bfill()
    # Transparent baseline: repeat the most recent 7-day average.
    baseline = float(series.tail(7).mean())
    future_dates = pd.date_range(series.index.max() + pd.Timedelta(days=1), periods=args.days, freq="D")
    result = pd.DataFrame({"Date": future_dates, "Country": args.country,
                           "Forecast AQI": np.repeat(baseline, args.days),
                           "Method": "Last 7-day mean baseline"})
    out = Path("outputs/forecast")
    out.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / f"{args.country.lower().replace(' ', '_')}_forecast.csv", index=False)
    print(result.to_string(index=False))
    print("\nEducational baseline only; not a validated forecast or health advisory.")

if __name__ == "__main__":
    main()
