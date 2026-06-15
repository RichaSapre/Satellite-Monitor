# SignalWatch: Satellite Observation Reliability Dashboard

**Live App:** https://satellite-monitor-yvmk4dcgbrm3thisyz9rtm.streamlit.app/

SignalWatch is a Python-based satellite operations dashboard that analyzes open ground-station observation data from the SatNOGS network. I built this project to explore the software side of satellite communication, especially how data analysis and monitoring tools can help understand satellite observation reliability.

The idea behind SignalWatch is simple: satellites depend on ground stations to receive and track signals, but not every observation is equally successful. Some observations may fail, some ground stations may perform better than others, and certain patterns can point to unusual behavior. This dashboard collects observation data, calculates reliability metrics, and visualizes satellite and ground-station performance in a clean, operations-style interface.

## What the project does

SignalWatch analyzes satellite observation data and displays key reliability insights such as:

* Total observations analyzed
* Overall observation success rate
* Number of unique satellites and ground stations
* Satellite-level reliability
* Ground-station reliability
* Satellite health score
* Rule-based anomaly alerts
* Machine learning-based anomaly detection
* Raw observation data for deeper inspection

The goal is not to diagnose real satellite failures, but to show how open data can be turned into useful monitoring insights. It is inspired by the kind of reliability and operations work that matters in satellite communication systems.

## Why I built this

I wanted to build a project that connected my Python and data analysis skills with a real-world satellite communication use case. Instead of creating a basic satellite tracker, I wanted to focus on something closer to satellite operations: monitoring, reliability, anomaly detection, and decision-making.

Satellite connectivity is not only about satellites in orbit. It also depends on reliable ground infrastructure, consistent communication quality, and the ability to detect unusual patterns quickly. SignalWatch is my attempt to model a small part of that workflow using open-source tools and open satellite observation data.

## Tech Stack

* Python
* Streamlit
* Pandas
* NumPy
* Plotly
* Scikit-learn
* SatNOGS open data

## Main Features

### Mission Overview

The dashboard gives a quick summary of the dataset, including total observations, overall success rate, unique satellites, and unique ground stations.

### Satellite Reliability

SignalWatch groups observations by satellite and calculates success rate, observation count, and average observation duration.

### Satellite Health Score

I created a simple health score that combines success rate, number of observations, and average duration. This is not meant to represent actual satellite health, but rather a software-generated reliability indicator based on the available observation data.

### Ground Station Reliability

The dashboard also analyzes ground stations to show which ones have stronger observation performance based on the dataset.

### Anomaly Detection

SignalWatch includes two types of anomaly detection:

1. **Rule-based anomaly detection**
   This flags satellites with low success rates when there are enough observations to make the result meaningful.

2. **Machine learning anomaly detection**
   This uses Isolation Forest to identify unusual satellite observation patterns based on metrics like observation count, success rate, and average duration.

## Data Source

This project uses open satellite observation data from the SatNOGS network. SatNOGS is a global open-source network of ground stations that collect satellite observations.

Relevant APIs:

* SatNOGS Network API: https://docs.satnogs.org/projects/satnogs-network/en/stable/api.html
* SatNOGS DB API: https://docs.satnogs.org/projects/satnogs-db/en/stable/api.html

## How to Run Locally

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Fetch the latest observation data:

```bash
python src/fetch_data.py
```

Run the Streamlit app:

```bash
python -m streamlit run app.py
```

## What I Learned

Through this project, I learned how to work with open satellite observation data, clean real-world API data, build reliability metrics, create anomaly detection logic, and deploy a data dashboard using Streamlit. I also gained a better understanding of how software can support satellite operations by turning raw observation records into useful monitoring insights.

## Future Improvements

Some improvements I would like to add next:

* Show actual satellite names instead of only IDs
* Add ground-station location mapping
* Add historical trend comparison
* Improve anomaly explanations
* Add more advanced filtering by satellite, station, and date
* Use SatNOGS DB metadata to enrich the dashboard
* Add automated daily data refresh

## Project Link

You can view the deployed project here:

https://satellite-monitor-yvmk4dcgbrm3thisyz9rtm.streamlit.app/
