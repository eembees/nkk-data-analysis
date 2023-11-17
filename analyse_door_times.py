#!/usr/bin/python
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pytz


DATA_DIR = Path("./data")
OUTPUT_DIR = Path("./output")

copenhagen = pytz.timezone("Europe/Copenhagen")

WEEKDAYS = [
    "Mandag",
    "Tirsdag",
    "Onsdag",
    "Torsdag",
    "Fredag",
    "Lørdag",
    "Søndag",
]


def make_hourly_distribution_from_series(series: pd.Series) -> pd.Series:
    return (series.dt.__getattribute__("hour")).value_counts().sort_index()


def make_morning_members_hourly_plot(
    df: pd.DataFrame,
) -> Tuple[plt.Figure, plt.Axes]:
    f, a = plt.subplots()
    series = df[df.token_type == 2].tid
    d = make_hourly_distribution_from_series(series)
    a.bar(d.index, d.values)
    a.set_title("Morgenmedlemmers timevis fordeling (total)")
    a.set_xlabel("Time")
    a.set_ylabel("Antal")
    # plt.show()
    f.savefig(OUTPUT_DIR / "morning_members_hourly.png", dpi=300)
    return f, a


def make_morning_members_daily_hourly_plot(
    df: pd.DataFrame,
) -> Tuple[plt.Figure, plt.Axes]:
    f, a = plt.subplots(nrows=7, sharex=True, figsize=(8, 12))
    for i in range(7):
        series = df[(df.token_type == 2) & (df.weekday == i)].tid
        d = make_hourly_distribution_from_series(series)
        a[i].bar(d.index, d.values)
        a[i].set_ylabel(WEEKDAYS[i])

    f.suptitle("Morgenmedlemmers timevis fordeling (daglig)")
    # plt.show()
    f.savefig(OUTPUT_DIR / "morning_members_daily_hourly.png", dpi=300)
    return f, a


def make_all_members_daily_hourly_plot(
    df: pd.DataFrame,
) -> Tuple[plt.Figure, plt.Axes]:
    f, a = plt.subplots(
        nrows=7, 
        sharex=True, 
        sharey=True, 
        figsize=(8, 12)
    )
    a[-1].set_xticks(range(5, 23))
    for i in range(7):
        series1 = df[(df.token_type == 1) & (df.weekday == i)].tid
        series2 = df[(df.token_type == 2) & (df.weekday == i)].tid
        d1 = make_hourly_distribution_from_series(series1)
        d2 = make_hourly_distribution_from_series(series2)
        a[i].bar(d1.index, d1.values, label="Alm.")
        a[i].bar(d2.index, d2.values, label="Morgen", bottom = d1[d1.index.isin(d2.index)].values)
        a[i].set_ylabel(WEEKDAYS[i])
        a[i].axvline(x=14.5 if i < 5 else 11.5, color="r", label="Morgenmedlems-grænse")
    a[0].legend(loc="upper left")

    f.suptitle(
        f"Medlemmers timevis fordeling (pr ugedag): \nPERIODE: {df.tid.min().date()}  ---  {df.tid.max().date()}"
    )
    f.savefig(OUTPUT_DIR / "all_members_daily_hourly.png", dpi=300)
    return f, a


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)

    csv_file_list = list(DATA_DIR.glob("*.csv"))
    csv_file = csv_file_list[0]
    print(csv_file)

    df = pd.read_csv(csv_file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["datetime"] = pd.to_datetime(df["timestamp"], utc=True)
    df["tid"] = df.datetime.dt.tz_convert(copenhagen)

    # FILTER ONLY STUFF AFTER SEPT 1st
    df = df[df.tid.dt.month > 8]

    # ADD cosmetic stuff here
    for _el in ["weekday", "hour"]:
        df[_el] = df.datetime.dt.__getattribute__(_el)

    # PLOT MAKIN
    make_morning_members_hourly_plot(df)
    plt.close("all")
    make_morning_members_daily_hourly_plot(df)
    plt.close("all")
    make_all_members_daily_hourly_plot(df)
