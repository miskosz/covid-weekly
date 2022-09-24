from collections import OrderedDict
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import pytz

import covid_weekly

"""
Merged SW+S and excluded countries with population < 100k:
    Monaco 39244
    Liechtenstein 38137
    Holy See 809
    San Marino 33938
    Andorra 77265
"""
regions = OrderedDict([
    # ("Northern Europe", ["Denmark", "Finland"]),
    ("Northern Europe", ["Denmark", "Finland", "Iceland", "Norway", "Sweden"]),
    ("Western Europe", ["Belgium", "France", "Ireland", "Luxembourg", "Netherlands", "United Kingdom"]),
    ("Central Europe", ["Austria", "Czechia", "Germany", "Hungary", "Poland", "Slovakia", "Slovenia", "Switzerland"]),
    ("Eastern Europe", ["Belarus", "Estonia", "Latvia", "Lithuania", "Moldova", "Ukraine"]),
    ("Southern and Southwestern Europe", ["Greece", "Italy", "Malta", "Portugal", "Spain"]),
    ("Southeastern Europe", ["Albania", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Montenegro", "North Macedonia", "Romania", "Serbia"]),
])

def compose_html(dataset: covid_weekly.Dataset) -> str:
    # Find last Sunday in the data.
    last_date = pd.to_datetime(dataset.confirmed.columns[-1])
    if last_date.dayofweek == 6:
        last_sunday = last_date
    else:
        last_sunday = last_date - pd.tseries.offsets.Week(weekday=6)


    html = """
    <!DOCTYPE html>
    <html>
    """

    html += """
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-WXQZGB6422"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-WXQZGB6422');
        </script>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Weekly confirmed COVID-19 cases per capita</title>
        <!--title>Weekly confirmed COVID-19 cases per capita and week-over-week percent increase</title-->
        <link rel="stylesheet" href="style.css"/>
        <link rel="icon" type="image/png" href="favicon.png"/>
    </head>
    """

    html += "<body>"

    html += f"""
    <h1>Weekly confirmed COVID-19 cases per capita</h1>

    <p>
    The graphs below show weekly progress of the coronavirus pandemic for European
    countries. The data is normalised per <span class="nowrap">100&thinsp;000</span>
    inhabitants, countries with smaller population are excluded. The graphs use a fixed
    scale and are organised by geographical region.
    </p>

    <p>
    The graphs show data until <strong>{last_sunday.strftime('%A, %B %-d %Y')}</strong> sourced
    from <a href="https://github.com/CSSEGISandData/COVID-19">Johns Hopkins University.</a>
    </p>

    <h4>Notes</h4>
    <ul>
        <li>Weeks span Monday&ndash;Sunday.
        <li>Geographical regions are according to <a href="https://www.cia.gov/library/publications/the-world-factbook/fields/276.html">
        CIA World Factbook.</a>
    </ul>
    \n"""

    territory_keys = sorted(
        [country for countries in regions.values() for country in countries]
    )
    html += "<h3 id='index'>Countries</h3>\n"
    html += "<div id='scroll'><a href='#index'>Back to index</a></div>\n"
    html += "<div id='country-list'>\n"
    for territory_key in territory_keys:
        iso3 = dataset.territories[territory_key]['iso3']
        html += f"<a href='#{iso3}'>{territory_key}</a><br />\n"
    html += "</div>\n"

    for region, countries in regions.items():
        html += f"<h2>{region}</h2>\n";
        for territory_key in countries:
            iso3 = dataset.territories[territory_key]['iso3']
            img_file = f"plots/{iso3}.png"

            html += f"<a name='{iso3}'><img src=./{img_file} /></a><br />\n"

    html += f"""
    <footer>
    Made by Michal with matplotlib and pandas.<br />
    Last updated {pd.Timestamp.now(tz=pytz.utc).strftime('%m/%d/%Y %H:%M %Z')}.
    </footer>
    """
    html += """
        <script>
        var scrollButton = document.getElementById("scroll");
        window.onscroll = function() {scrollFunction()};
        scrollFunction()

        function scrollFunction() {
          var indexOffset = document.getElementById("index").getBoundingClientRect().top;
          if (indexOffset < 0) {
            scrollButton.style.display = "block";
          } else {
            scrollButton.style.display = "none";
          }
        }
        </script>
    """
    html += "</body></html>"
    return html


def main():
    dataset = covid_weekly.Dataset()

    territory_keys = sorted(
        [country for countries in regions.values() for country in countries]
    )
    print(territory_keys)

    for territory_key in territory_keys:
        print(territory_key)
        img_file = f"build/plots/{dataset.territories[territory_key]['iso3']}.png"
        fig = covid_weekly.territory_plot(dataset=dataset, territory_key=territory_key)
        fig.savefig(img_file, dpi=150, bbox_inches='tight')
        plt.close(fig)

    html = compose_html(dataset=dataset)

    with open("build/index.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
