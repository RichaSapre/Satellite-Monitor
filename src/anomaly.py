from sklearn.ensemble import IsolationForest


def rule_based_anomalies(satellite_df):
    """
    Simple anomaly rules.

    This is the easy-to-explain version:
    - If a satellite has enough observations
    - And its success rate is low
    - Flag it
    """
    df = satellite_df.copy()

    df["anomaly_reason"] = ""

    df.loc[
        (df["observations"] >= 5) & (df["success_rate"] < 50),
        "anomaly_reason"
    ] = "Low success rate compared with expected communication reliability"

    anomalies = df[df["anomaly_reason"] != ""]

    return anomalies


def isolation_forest_anomalies(satellite_df):
    """
    Machine learning anomaly detection.

    Isolation Forest looks for rows that are unusual compared to others.
    """
    df = satellite_df.copy()

    # Always create these columns so app.py never crashes.
    df["ml_anomaly"] = 0
    df["is_ml_anomaly"] = 0

    features = df[["observations", "success_rate", "avg_duration"]].fillna(0)

    # If there is not enough data, return safely with no ML anomalies.
    if len(features) < 10:
        return df

    model = IsolationForest(
        contamination=0.1,
        random_state=42
    )

    predictions = model.fit_predict(features)

    # IsolationForest returns -1 for anomaly and 1 for normal.
    df["ml_anomaly"] = predictions
    df["is_ml_anomaly"] = df["ml_anomaly"].apply(lambda x: 1 if x == -1 else 0)

    return df
