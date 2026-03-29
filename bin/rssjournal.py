#!/usr/bin/env python
# -*- coding: utf-8 -*-
# a at foo dot be - Alexandre Dulaunoy - https://github.com/adulau/rss-tools
#
# Feed-to-journal utility.
#
# Fetches RSS/Atom entries, stores them in per-day Markdown journal pages,
# and updates a yearly Markdown index. Existing Markdown files are read before
# writing so old content is preserved and duplicate entries are avoided.

import datetime
import hashlib
import html
import os
import re
import time
from collections import defaultdict
from optparse import OptionParser
from urllib.parse import urlparse

import feedparser
from bs4 import BeautifulSoup

feedparser.USER_AGENT = "rssjournal.py +https://github.com/adulau/rss-tools"


LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_entry_epoch(entry):
    for date_attr in ("modified_parsed", "published_parsed", "updated_parsed"):
        parsed_date = getattr(entry, date_attr, None)
        if parsed_date:
            return int(time.mktime(parsed_date))
    return 0


def sanitize_title(entry, summarysize):
    if "title" in entry:
        return html.unescape(entry.title)
    cleantext = BeautifulSoup(getattr(entry, "summary", ""), "lxml").text
    return cleantext[: int(summarysize)]


def read_existing_links(path):
    if not os.path.exists(path):
        return set()
    links = set()
    with open(path, "r", encoding="utf-8") as fobj:
        for line in fobj:
            for match in LINK_PATTERN.finditer(line):
                links.add(match.group(1))
    return links


def build_front_matter(title):
    return f"---\nlayout: page\ntitle: {title}\n---\n\n"


def ensure_daily_file(path, day_key, title_prefix):
    if os.path.exists(path):
        return
    with open(path, "w", encoding="utf-8") as fobj:
        fobj.write(build_front_matter(f"{day_key}{title_prefix}"))


def append_new_entries(path, day_key, entries, title_prefix):
    ensure_daily_file(path, day_key, title_prefix)
    existing_links = read_existing_links(path)

    new_lines = []
    for entry in entries:
        if entry["link"] in existing_links:
            continue
        timestamp = datetime.datetime.fromtimestamp(entry["epoch"]).strftime("%H:%M:%S")
        domain = urlparse(entry["link"]).netloc
        line = f'- [{entry["title"]}]({entry["link"]}) @ {timestamp} ({domain})\n'
        new_lines.append(line)

    if not new_lines:
        return 0

    with open(path, "a", encoding="utf-8") as fobj:
        if os.path.getsize(path) > 0:
            fobj.write("\n")
        fobj.writelines(new_lines)
    return len(new_lines)


def list_day_files(destination, year):
    prefix = f"{year}-"
    pages = []
    for filename in os.listdir(destination):
        if not filename.endswith(".md"):
            continue
        if filename == f"{year}.md":
            continue
        if filename.startswith(prefix):
            pages.append(filename)
    pages.sort()
    return pages


def count_links(path):
    return len(read_existing_links(path))


def update_year_index(destination, year, title_prefix):
    pages = list_day_files(destination, year)
    index_path = os.path.join(destination, f"{year}.md")

    with open(index_path, "w", encoding="utf-8") as fobj:
        fobj.write(build_front_matter(f"{year}{title_prefix}"))
        if not pages:
            fobj.write("No entries yet.\n")
            return

        for page in pages:
            full_path = os.path.join(destination, page)
            page_day = page[:-3]
            entries_count = count_links(full_path)
            fobj.write(f"- [{page_day}]({page}) - {entries_count} item(s)\n")


def collect_entries(urls, summarysize):
    allitem = {}

    for url in urls:
        parsed_feed = feedparser.parse(url)
        for el in parsed_feed.entries:
            if "link" not in el:
                continue
            epoch = parse_entry_epoch(el)
            if epoch == 0:
                continue

            h = hashlib.md5()
            h.update(el.link.encode("utf-8"))
            linkkey = h.hexdigest()
            allitem[linkkey] = {
                "link": str(el.link),
                "epoch": int(epoch),
                "title": sanitize_title(el, summarysize),
            }

    return list(allitem.values())


def write_journal(entries, destination, maxitem, title_prefix):
    day_entries = defaultdict(list)

    sorted_entries = sorted(entries, key=lambda x: x["epoch"], reverse=True)
    if maxitem:
        sorted_entries = sorted_entries[:maxitem]

    for entry in sorted_entries:
        day_key = datetime.datetime.fromtimestamp(entry["epoch"]).strftime("%Y-%m-%d")
        day_entries[day_key].append(entry)

    updated = []
    os.makedirs(destination, exist_ok=True)

    for day_key, items in sorted(day_entries.items(), reverse=True):
        file_path = os.path.join(destination, f"{day_key}.md")
        added = append_new_entries(file_path, day_key, items, title_prefix)
        if added:
            updated.append((day_key, added))

    years = {day.split("-")[0] for day in day_entries.keys()}
    for year in years:
        update_year_index(destination, year, title_prefix)

    return updated


usage = "usage: %prog [options] url"
parser = OptionParser(usage)

parser.add_option(
    "-m",
    "--maxitem",
    dest="maxitem",
    default=200,
    help="maximum item to process from merged feed entries, default 200",
)
parser.add_option(
    "-s",
    "--summarysize",
    dest="summarysize",
    default=60,
    help="maximum size of the summary if a title is not present",
)
parser.add_option(
    "-d",
    "--destination",
    dest="destination",
    default=".",
    help="destination directory for markdown journal files, default current directory",
)
parser.add_option(
    "-p",
    "--title-prefix",
    dest="title_prefix",
    default=" Journal",
    help='title suffix for generated markdown pages, default " Journal"',
)

(options, args) = parser.parse_args()

if not args:
    parser.error("at least one RSS/Atom URL is required")

entries = collect_entries(args, int(options.summarysize))
changes = write_journal(
    entries,
    options.destination,
    int(options.maxitem),
    options.title_prefix,
)

for day, count in changes:
    print(f"updated {day}.md with {count} new item(s)")

if not changes:
    print("no updates required")
