# SQL Server Logs Analysis

This project implements an ETL (Extract, Transform, Load) pipeline in Python using DuckDB to process and analyze log records (in JSON format). The system extracts the data, calculates usage and performance metrics, and generates detailed reports in CSV files.

## Description

The `main.py` script performs the following operations:

1.  **Data Loading**: Imports logs from `data/logs.json`.
2.  **Metrics Calculation**:
    *   Most requested endpoints.
    *   Error analysis (Status Code >= 500).
    *   Endpoint performance (average time, P50/P95 percentiles, max).
    *   Traffic trends by hour.
    *   Top 3 slowest requests.
    *   Daily requests comparison.
3.  **Report Generation**: Saves results in the `output/` folder.

## Requirements

*   Python 3.x
*   [DuckDB](https://duckdb.org/)

## Installation

1.  Clone this repository or download the files.
2.  Install the necessary dependencies:

```bash
pip install -r requirements.txt
```

## File Structure

```
├── data/
│   └── logs.json       # Input file with logs 
├── output/             # Directory where CSV reports are saved
├── main.py             # Main analysis script
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
```

## Usage

Ensure you have the logs file at `data/logs.json` and execute the main script:

```bash
python main.py
```
## Docker
```
docker build -t trends-techs .
docker run trends-techs
```

## Output

The resulting files will be saved in the `output/` folder:

*   `endpoints_metrics.csv`: Top 10 endpoints by number of requests.
*   `errors_metrics.csv`: Statistics of endpoints with server errors (500+).
*   `performance_metrics.csv`: Latency metrics and percentiles by endpoint.
*   `trend_hour.csv`: Request volume and errors grouped by hour.
*   `slowest_requests.csv`: The 3 slowest requests recorded.
*   `daily_metrics.csv`: Daily traffic comparison with respect to the previous day.

## Autor
[Josue Armenta] - [2026-01-13]
