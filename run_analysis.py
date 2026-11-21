from pathlib import Path
import sys
from src.aqi_gis.cleaning import load_and_clean
from src.aqi_gis.analysis import create_summaries
from src.aqi_gis.mapping import create_latest_map

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "data_date.csv"

def main():
    if not DATA.exists():
        sys.exit("Dataset not found. Download data_date.csv from Kaggle and place it in data/raw/data_date.csv")
    cleaned = load_and_clean(DATA)
    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(processed / "aqi_country_daily_clean.csv", index=False)

    create_summaries(cleaned, ROOT / "outputs" / "figures")
    unmatched = create_latest_map(cleaned, ROOT / "outputs" / "maps" / "global_aqi_latest.html")
    if unmatched:
        (ROOT / "outputs" / "unmatched_countries.csv").write_text(
            "Country\n" + "\n".join(f'"{name}"' for name in unmatched), encoding="utf-8"
        )
    print(f"Done. Cleaned records: {len(cleaned):,}; latest date: {cleaned['Date'].max().date()}")
    print("See data/processed/ and outputs/.")

if __name__ == "__main__":
    main()
