#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# a at foo dot be - Alexandre Dulaunoy - https://github.com/adulau/rss-tools
#
# RSS/Atom activity grapher.
#
# Reads one or more RSS/Atom feeds and generates a PNG calendar heatmap where
# each day intensity represents the number of entries published on that day.

import calendar
import datetime
import time
from collections import defaultdict
from optparse import OptionParser

import feedparser
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.gridspec import GridSpec

feedparser.USER_AGENT = "rssgraph.py +https://github.com/adulau/rss-tools"


def parse_yyyymmdd(value):
    """Parse YYYYMMDD date strings."""
    return datetime.datetime.strptime(value, "%Y%m%d").date()


def collect_daily_counts(urls):
    """Collect counts per day from feeds."""
    counts = defaultdict(int)

    for url in urls:
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            parsed_date = (
                getattr(entry, "modified_parsed", None)
                or getattr(entry, "published_parsed", None)
                or getattr(entry, "updated_parsed", None)
            )

            if not parsed_date:
                continue

            entry_date = datetime.datetime.fromtimestamp(time.mktime(parsed_date)).date()
            counts[entry_date] += 1

    return counts


def month_matrix(year, month, counts):
    """Return a matrix (6 weeks x 7 weekdays) for one month."""
    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(year, month)

    matrix = [[None for _ in range(7)] for _ in range(6)]
    for widx, week in enumerate(weeks):
        for didx, day in enumerate(week):
            if day.month == month:
                matrix[widx][didx] = counts.get(day, 0)

    return matrix


def render_year(fig, parent_spec, year, counts, cmap_name, max_value):
    """Render one year as a 3x4 month panel."""
    year_grid = parent_spec.subgridspec(4, 4, height_ratios=[0.16, 1, 1, 1], hspace=0.35)
    title_ax = fig.add_subplot(year_grid[0, :])
    title_ax.set_axis_off()
    title_ax.set_title(str(year), fontsize=15, pad=2)

    cmap = cm.get_cmap(cmap_name).copy()
    cmap.set_bad(color="#f1f1f1")

    for month in range(1, 13):
        row = ((month - 1) // 4) + 1
        col = (month - 1) % 4
        axis = fig.add_subplot(year_grid[row, col])

        matrix = month_matrix(year, month, counts)
        masked = [[float("nan") if v is None else v for v in week] for week in matrix]

        axis.imshow(masked, cmap=cmap, vmin=0, vmax=max_value, aspect="auto")
        axis.set_title(calendar.month_abbr[month], fontsize=10, pad=4)
        axis.set_xticks(range(7))
        axis.set_xticklabels(["M", "T", "W", "T", "F", "S", "S"], fontsize=7)
        axis.set_yticks([])
        axis.tick_params(length=0)

        for spine in axis.spines.values():
            spine.set_visible(False)


def render_calendar(counts, output, title, cmap_name, date_from=None, date_to=None):
    """Create and save activity heatmap PNG file."""
    if not counts:
        raise ValueError("No dated entries found in provided feeds.")

    all_dates = sorted(counts.keys())
    start = date_from or all_dates[0]
    end = date_to or all_dates[-1]

    if start > end:
        raise ValueError("Start date is after end date.")

    filtered = {d: c for d, c in counts.items() if start <= d <= end}
    if not filtered:
        raise ValueError("No entries found in selected date range.")

    years = list(range(start.year, end.year + 1))
    max_value = max(filtered.values())

    fig = plt.figure(figsize=(13, max(4.5, len(years) * 4.4)))
    outer = GridSpec(len(years), 1, figure=fig, hspace=0.36)

    if title:
        fig.suptitle(title, fontsize=18, y=0.998)

    for idx, year in enumerate(years):
        render_year(fig, outer[idx], year, filtered, cmap_name, max_value)

    scalar = cm.ScalarMappable(cmap=cm.get_cmap(cmap_name), norm=plt.Normalize(vmin=0, vmax=max_value))
    cbar = fig.colorbar(scalar, ax=fig.axes, fraction=0.012, pad=0.01)
    cbar.set_label("Entries per day")

    fig.tight_layout(rect=(0, 0, 1, 0.985 if title else 1))
    fig.savefig(output, dpi=200)
    plt.close(fig)


def main():
    usage = "usage: %prog [options] url(s)"
    parser = OptionParser(usage)
    parser.add_option(
        "-o",
        "--output",
        dest="output",
        default="rss-activity.png",
        help="output PNG filename, default rss-activity.png",
    )
    parser.add_option(
        "-t",
        "--title",
        dest="title",
        default="RSS/Atom activity heatmap",
        help="graph title, default 'RSS/Atom activity heatmap'",
    )
    parser.add_option(
        "-c",
        "--cmap",
        dest="cmap",
        default="YlGn",
        help="matplotlib colormap name, default YlGn",
    )
    parser.add_option(
        "--from",
        dest="date_from",
        default=None,
        help="start date filter (YYYYMMDD)",
    )
    parser.add_option(
        "--to",
        dest="date_to",
        default=None,
        help="end date filter (YYYYMMDD)",
    )

    (options, args) = parser.parse_args()

    if not args:
        parser.print_help()
        raise SystemExit(1)

    date_from = parse_yyyymmdd(options.date_from) if options.date_from else None
    date_to = parse_yyyymmdd(options.date_to) if options.date_to else None

    counts = collect_daily_counts(args)
    render_calendar(
        counts,
        output=options.output,
        title=options.title,
        cmap_name=options.cmap,
        date_from=date_from,
        date_to=date_to,
    )


if __name__ == "__main__":
    main()
