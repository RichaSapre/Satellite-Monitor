import pandas as pd
from pathlib import Path


DATA_PATH = Path("data/observations.csv")


def load_observations():
    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "id",
        "satellite",
        "station",
        "start",
        "end",
        "status",
        "transmitter",
        "archive",
        "waterfall",
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = None

    df["start"] = pd.to_datetime(df["start"], errors="coerce")
    df["end"] = pd.to_datetime(df["end"], errors="coerce")

    df["duration_minutes"] = (
        df["end"] - df["start"]
    ).dt.total_seconds() / 60

    df["duration_minutes"] = df["duration_minutes"].fillna(0)

    df["status_text"] = df["status"].astype(str).str.lower()

    df = df[df["status_text"] != "future"].copy()

    df["satellite"] = df["satellite"].fillna("Unknown Satellite").astype(str)
    df["station"] = df["station"].fillna("Unknown Station").astype(str)

    def classify_success(status):
        status = str(status).lower()

        success_words = [
            "good",
            "success",
            "successful",
            "completed",
            "approved",
        ]

        failure_words = [
            "bad",
            "failed",
            "failure",
            "unknown",
            "rejected",
            "future",
        ]

        if any(word in status for word in success_words):
            return 1

        if any(word in status for word in failure_words):
            return 0

        return 0

    df["is_success"] = df["status_text"].apply(classify_success)

    df["date"] = df["start"].dt.date

    return df


def calculate_summary(df):
    total_observations = len(df)

    if total_observations == 0:
        success_rate = 0
        unique_satellites = 0
        unique_stations = 0
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


def empty_reliability_table(group_column):
    return pd.DataFrame(
        columns=[
            group_column,
            "observations",
            "success_rate",
            "avg_duration",
        ]
    )


def satellite_reliability(df):
    if df.empty or "satellite" not in df.columns:
        return empty_reliability_table("satellite")

    result = (
        df.groupby("satellite", dropna=False)
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
    if df.empty or "station" not in df.columns:
        return empty_reliability_table("station")

    result = (
        df.groupby("station", dropna=False)
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

    if df.empty:
        df["health_score"] = []
        return df

    def calculate_score(row):
        score = row["success_rate"]

        if row["observations"] < 5:
            score -= 20

        if row["avg_duration"] < 2:
            score -= 10

        score = max(0, min(100, score))

        return round(score, 1)

    df["health_score"] = df.apply(calculate_score, axis=1)

    return df
