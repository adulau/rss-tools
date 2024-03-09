#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# a at foo dot be - Alexandre Dulaunoy - https://git.foo.be/adulau/rss-tools
#
# rssmerge.py is a simple script designed to aggregate RSS feeds and merge them in reverse chronological order.
# It outputs the merged content in text, HTML, or Markdown format. This tool is useful for tracking recent events
# from various feeds and publishing them on your website.
#
# Sample usage:
#
# python3 rssmerge.py "https://git.foo.be/adulau.rss"  "http://api.flickr.com/services/feeds/photos_public.gne?id=31797858@N00&lang=en-us&format=atom"
#  "https://github.com/adulau.atom" -o markdown --maxitem 20

import feedparser
import sys, os
import time
import datetime
import hashlib
from optparse import OptionParser
import html
from bs4 import BeautifulSoup
from urllib.parse import urlparse

feedparser.USER_AGENT = "rssmerge.py +https://github.com/adulau/rss-tools"


def RenderMerge(itemlist, output="text"):
    i = 0
    if output == "text":
        for item in itemlist:
            i = i + 1
            # Keep consistent datetime representation if not use allitem[item[1]]['updated']
            link = allitem[item[1]]["link"]
            title = html.escape(allitem[item[1]]["title"])
            timestamp = datetime.datetime.fromtimestamp(
                allitem[item[1]]["epoch"]
            ).ctime()
            print(f'{i}:{title}:{timestamp}:{link}')

            if i == int(options.maxitem):
                break

    if output == "phtml":
        print("<ul>")
        for item in itemlist:
            i = i + 1
            # Keep consistent datetime representation if not use allitem[item[1]]['updated']
            link = allitem[item[1]]["link"]
            title = html.escape(allitem[item[1]]["title"])
            timestamp = datetime.datetime.fromtimestamp(
                allitem[item[1]]["epoch"]
            ).ctime()
            print(f'<li><a href="{link}"> {title}</a> --- (<i>{timestamp}</i>)</li>')
            if i == int(options.maxitem):
                break
        print("</ul>")

    if output == "markdown":
        for item in itemlist:
            i = i + 1
            title = html.escape(allitem[item[1]]["title"])
            link = allitem[item[1]]["link"]
            timestamp = datetime.datetime.fromtimestamp(
                allitem[item[1]]["epoch"]
            ).ctime()
            domain = urlparse(allitem[item[1]]["link"]).netloc
            print(f'- {domain} [{title}]({link}) @{timestamp}')
            if i == int(options.maxitem):
                break


usage = "usage: %prog [options] url"
parser = OptionParser(usage)

parser.add_option(
    "-m",
    "--maxitem",
    dest="maxitem",
    default=200,
    help="maximum item to list in the feed, default 200",
)
parser.add_option(
    "-s",
    "--summarysize",
    dest="summarysize",
    default=60,
    help="maximum size of the summary if a title is not present",
)
parser.add_option(
    "-o",
    "--output",
    dest="output",
    default="text",
    help="output format (text, phtml, markdown), default text",
)

# 2007-11-10 11:25:51
pattern = "%Y-%m-%d %H:%M:%S"

(options, args) = parser.parse_args()

allitem = {}

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
        elepoch = int(time.mktime(time.strptime(str(eldatetime), pattern)))
        h = hashlib.md5()
        h.update(el.link.encode("utf-8"))
        linkkey = h.hexdigest()
        allitem[linkkey] = {}
        allitem[linkkey]["link"] = str(el.link)
        allitem[linkkey]["epoch"] = int(elepoch)
        allitem[linkkey]["updated"] = el.updated
        if "title" in el:
            allitem[linkkey]["title"] = html.unescape(el.title)
        else:
            cleantext = BeautifulSoup(el.summary, "lxml").text
            allitem[linkkey]["title"] = cleantext[: options.summarysize]

itemlist = []

for something in list(allitem.keys()):
    epochkeytuple = (allitem[something]["epoch"], something)
    itemlist.append(epochkeytuple)

itemlist.sort()
itemlist.reverse()

RenderMerge(itemlist, options.output)
