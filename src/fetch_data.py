import requests
import pandas as pd
from pathlib import Path


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OBSERVATIONS_URL = "https://network.satnogs.org/api/observations/"


def fetch_by_status(status, limit=200):
    params = {
        "format": "json",
        "status": status,
    }

    response = requests.get(OBSERVATIONS_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data[:limit]


def fetch_observations():
    observations = []

    for status in ["good", "bad", "unknown"]:
        try:
            observations.extend(fetch_by_status(status, limit=200))
        except requests.RequestException as error:
            print(f"Could not fetch status={status}: {error}")

    return observations


def save_observations():
    observations = fetch_observations()

    rows = []

    for obs in observations:
        rows.append(
            {
                "id": obs.get("id"),
                "satellite": obs.get("norad_cat_id") or obs.get("satellite"),
                "station": obs.get("station") or obs.get("ground_station"),
                "start": obs.get("start"),
                "end": obs.get("end"),
                "status": obs.get("status", "unknown"),
                "transmitter": obs.get("transmitter"),
                "archive": obs.get("archive"),
                "waterfall": obs.get("waterfall"),
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        print("No observations fetched.")
    else:
        df = df[df["status"].astype(str).str.lower() != "future"].copy()
        df = df.drop_duplicates(subset=["id"])

    output_path = DATA_DIR / "observations.csv"
    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} observations to {output_path}")

    if not df.empty:
        print(df["status"].value_counts(dropna=False))
        print(df.head())


if __name__ == "__main__":
    save_observations()
