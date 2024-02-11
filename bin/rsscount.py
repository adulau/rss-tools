#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# a at foo dot be - Alexandre Dulaunoy - http://www.foo.be/cgi-bin/wiki.pl/RssAny
#
# rsscount.py is a simple script to count how many items in a RSS feed per day
#
# The output is epoch + the number of changes separated with a tab.
#
# This is used to build statistic like the wiki creativity index.
#

import feedparser
import sys, os
import time
import datetime
from optparse import OptionParser

feedparser.USER_AGENT = "rsscount.py +https://github.com/adulau/rss-tools"

usage = "usage: %prog url(s)"
parser = OptionParser(usage)

(options, args) = parser.parse_args()

if args is None:
    print(usage)

counteditem = {}

for url in args:

    d = feedparser.parse(url)
    for el in d.entries:

        if "modified_parsed" in el:
            eldatetime = datetime.datetime.fromtimestamp(
                time.mktime(el.modified_parsed)
            )
        else:
            eldatetime = datetime.datetime.fromtimestamp(
                time.mktime(el.published_parsed)
            )
        eventdate = eldatetime.isoformat(" ").split(" ", 1)
        edate = eventdate[0].replace("-", "")

        if edate in counteditem:
            counteditem[edate] = counteditem[edate] + 1
        else:
            counteditem[edate] = 1


for k in list(counteditem.keys()):

    print(f"{k}\t{counteditem[k]}")
