from typing import Any, Dict

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


class Dataset:
    confirmed: pd.DataFrame
    territories: Dict[str, Dict[str, Any]]

    def __init__(self):
        self.confirmed = pd.read_csv("time_series_covid19_confirmed_global.csv").fillna(value={"Province/State": "NULL"})
        territories_raw = pd.read_csv("UID_ISO_FIPS_LookUp_Table.csv").fillna(value={"Province_State": "NULL"})
        self.territories = territories_raw.set_index('Combined_Key').T.to_dict()


def _territory_confirmed_per100k(dataset: Dataset, territory_key: str) -> pd.Series:
    territory = dataset.territories[territory_key]
    population = territory["Population"]

    selector_confirmed = (
        (dataset.confirmed["Country/Region"] == territory["Country_Region"]) & \
        (dataset.confirmed["Province/State"] == territory["Province_State"])
    )
    row = dataset.confirmed[selector_confirmed]
    # Start displaying data from the week following Sunday Feb 23.
    total = row.loc[:,"2/23/20":].squeeze()
    return total / population * 100000


def _weekly_series(total: pd.Series) -> pd.Series:
    """
    weekly = total[this Sunday] - total[last Sunday]
    label = this Sunday
    """
    total_np = total.to_numpy()
    weekly = total_np[7::7]-total_np[:-7:7]  # Sundays
    index = total.index[7::7]  # Sundays
    return pd.Series(weekly, index)


def _date_to_days(date: pd.Timestamp):
    date0 = pd.Timestamp("2020-03-01")
    return (date - date0).days


def _date_fmt(date_str: str):
    dt = pd.to_datetime(date_str)
    if dt.month == 1:
        return dt.strftime("%b \'%y")
    return dt.strftime("%b")


def _set_yticks(ax: matplotlib.axis.Axis, ymax: int, ytickstep: int):
    ax.set_ylim([0, ymax])
    ax.set_yticks(np.arange(ytickstep, ymax + 1, ytickstep))
    ax.yaxis.grid(True)
    ax.yaxis.set_ticks_position('none')


def _set_xticks(ax: matplotlib.axis.Axis, series: pd.Series):
    month_starts = pd.date_range(series.index[0], series.index[-1], freq='MS')
    month_mids = month_starts + pd.DateOffset(days=14)

    # Month labels
    xticks = [_date_to_days(d) for d in month_mids]
    xticklabels = [_date_fmt(d) for d in month_mids]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, rotation=90)
    ax.xaxis.set_ticks_position('none')

    # Year gridlines
    minor_ticks = [_date_to_days(pd.Timestamp(d)) for d in ["2021-01-01", "2022-01-01"]]
    ax.set_xticks(minor_ticks, minor=True)
    ax.xaxis.grid(True, which="minor")

    # Limits
    ax.set_xlim([0, max(xticks)])


def _bar_plot(ax: matplotlib.axis.Axis, series: pd.Series, color: str) -> None:
    x = [_date_to_days(pd.Timestamp(d)) for d in series.index]
    y = list(series)
    ax.bar(x, y, width=6)


def territory_plot(dataset: Dataset, territory_key: str) -> matplotlib.figure.Figure:
    total = _territory_confirmed_per100k(dataset=dataset, territory_key=territory_key)
    weekly = _weekly_series(total=total)

    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["charter", "Georgia", "Cambria", "Times New Roman", "Times", "serif"]
    plt.rcParams["font.size"] = 11

    # figure = plt.figure(figsize=(10, 8))
    # spec = matplotlib.gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])

    # ax0 = figure.add_subplot(spec[0])
    figure = plt.figure(figsize=(10, 5))
    ax0 = figure.add_subplot(111)
    _bar_plot(ax0, weekly, "steelblue")
    _set_yticks(ax0, ymax=3000, ytickstep=250)
    _set_xticks(ax0, weekly)
    ax0.set_title(f"New cases weekly per 100k inhabitants (current: {weekly[-1]:.0f})", pad=12)

    # ax1 = figure.add_subplot(spec[1])
    # _bar_plot(ax=ax1, series=rate, color="steelblue")  # tab:blue slategrey
    # ax1.set_ylim([-1.0, 2.0])
    # ax1.yaxis.set_major_formatter(ticker.FuncFormatter(_rate_fmt))
    # ax1.set_title(f"Week-over-week percent increase (current: {_rate_fmt(rate[-1])})", pad=12)

    figure.suptitle(territory_key, fontsize=20, y=0.93)
    figure.tight_layout(pad=1.8)
    figure.patch.set_facecolor('white')
    return figure