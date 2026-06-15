import requests
import pandas as pd
from pathlib import Path


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OBSERVATIONS_URL = "https://network.satnogs.org/api/observations/"


def fetch_observations(limit=500):
    """
    Fetch completed SatNOGS observations instead of future scheduled ones.
    """
    params = {
        "format": "json",
        "status": "good",
    }

    response = requests.get(OBSERVATIONS_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data[:limit]


def save_observations():
    observations = fetch_observations(limit=500)

    rows = []

    for obs in observations:
        rows.append({
            "id": obs.get("id"),
            "satellite": obs.get("norad_cat_id") or obs.get("satellite"),
            "station": obs.get("station") or obs.get("ground_station"),
            "start": obs.get("start"),
            "end": obs.get("end"),
            "status": obs.get("status", "unknown"),
            "transmitter": obs.get("transmitter"),
            "archive": obs.get("archive"),
            "waterfall": obs.get("waterfall"),
        })

    df = pd.DataFrame(rows)

    output_path = DATA_DIR / "observations.csv"
    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} observations to {output_path}")
    print(df.head())
    print(df.columns)


if __name__ == "__main__":
    save_observations()