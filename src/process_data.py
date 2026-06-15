import pandas as pd
from pathlib import Path


DATA_PATH = Path("data/observations.csv")


def load_observations():
    df = pd.read_csv(DATA_PATH)

    # Convert time columns into datetime values.
    df["start"] = pd.to_datetime(df["start"], errors="coerce")
    df["end"] = pd.to_datetime(df["end"], errors="coerce")

    # Calculate duration in minutes.
    df["duration_minutes"] = (
        df["end"] - df["start"]
    ).dt.total_seconds() / 60

    # Clean status text.
    df["status_text"] = df["status"].astype(str).str.lower()

    # Remove future scheduled observations because they have not happened yet.
    df = df[df["status_text"] != "future"].copy()

    def classify_success(status):
        status = str(status).lower()

        success_words = ["good", "success", "successful", "completed", "approved"]
        failure_words = ["bad", "failed", "failure", "unknown", "rejected", "future"]

        if any(word in status for word in success_words):
            return 1

        if any(word in status for word in failure_words):
            return 0

        return 0

    df["is_success"] = df["status_text"].apply(classify_success)

    # Create date column for daily charts.
    df["date"] = df["start"].dt.date

    return df


def calculate_summary(df):
    total_observations = len(df)

    if total_observations == 0:
        success_rate = 0
    else:
        success_rate = df["is_success"].mean() * 100

    unique_satellites = df["satellite"].nunique()
    unique_stations = df["station"].nunique()

    summary = {
        "total_observations": total_observations,
        "success_rate": round(success_rate, 2),
        "unique_satellites": unique_satellites,
        "unique_stations": unique_stations,
    }

    return summary


def satellite_reliability(df):
    result = (
        df.groupby("satellite")
        .agg(
            observations=("id", "count"),
            success_rate=("is_success", "mean"),
            avg_duration=("duration_minutes", "mean"),
        )
        .reset_index()
    )

    result["success_rate"] = (result["success_rate"] * 100).round(2)
    result["avg_duration"] = result["avg_duration"].round(2)

    return result.sort_values("observations", ascending=False)


def station_reliability(df):
    result = (
        df.groupby("station")
        .agg(
            observations=("id", "count"),
            success_rate=("is_success", "mean"),
            avg_duration=("duration_minutes", "mean"),
        )
        .reset_index()
    )

    result["success_rate"] = (result["success_rate"] * 100).round(2)
    result["avg_duration"] = result["avg_duration"].round(2)

    return result.sort_values("observations", ascending=False)


def add_health_score(satellite_df):
    df = satellite_df.copy()

    def calculate_score(row):
        score = row["success_rate"]

        # If there are very few observations, confidence is lower.
        if row["observations"] < 5:
            score -= 20

        # Very short observations may be less useful.
        if row["avg_duration"] < 2:
            score -= 10

        # Keep score between 0 and 100.
        score = max(0, min(100, score))

        return round(score, 1)

    df["health_score"] = df.apply(calculate_score, axis=1)

    return df