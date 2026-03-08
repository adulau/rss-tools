#!/usr/bin/env python
# -*- coding: utf-8 -*-
# a at foo dot be - Alexandre Dulaunoy - https://github.com/adulau/rss-tools
#
# RSS/Atom daily counter.
#
# Reads one or more feeds and prints per-day counts using YYYYMMDD<TAB>COUNT.
# Useful as a simple input for trend/statistics tooling.

import feedparser
import time
import datetime
from optparse import OptionParser

feedparser.USER_AGENT = "rsscount.py +https://github.com/adulau/rss-tools"

usage = "usage: %prog url(s)"
parser = OptionParser(usage)

(options, args) = parser.parse_args()

if not args:
    parser.print_help()
    raise SystemExit(1)

counteditem = {}

for url in args:

    d = feedparser.parse(url)
    for el in d.entries:

        parsed_date = getattr(el, "modified_parsed", None) or getattr(
            el, "published_parsed", None
        ) or getattr(el, "updated_parsed", None)
        if not parsed_date:
            continue
        eldatetime = datetime.datetime.fromtimestamp(time.mktime(parsed_date))
        eventdate = eldatetime.isoformat(" ").split(" ", 1)
        edate = eventdate[0].replace("-", "")

        if edate in counteditem:
            counteditem[edate] = counteditem[edate] + 1
        else:
            counteditem[edate] = 1


for k in list(counteditem.keys()):

    print(f"{k}\t{counteditem[k]}")
