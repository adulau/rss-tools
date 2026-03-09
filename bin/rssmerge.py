#!/usr/bin/env python
# -*- coding: utf-8 -*-
# a at foo dot be - Alexandre Dulaunoy - https://github.com/adulau/rss-tools
#
# Feed merger utility.
#
# Aggregates entries from multiple RSS/Atom feeds, sorts by date, and prints the
# merged stream as text, pseudo-HTML list output, or Markdown. Markdown can
# optionally include an extended content/summary excerpt.

import feedparser
import time
import datetime
import hashlib
import random
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
            if options.markdown_extended:
                extended_text = allitem[item[1]].get("extended", "")
                if extended_text:
                    print(f"  > {extended_text[: int(options.markdown_extended_size)]}")
            if i == int(options.maxitem):
                break


def extract_extended_text(entry):
    if "content" in entry and len(entry.content):
        raw_text = entry.content[0].value
    else:
        raw_text = getattr(entry, "summary", "")
    cleantext = BeautifulSoup(raw_text, "lxml").text
    return " ".join(cleantext.split())


def parse_entry_epoch(entry):
    for date_attr in ("modified_parsed", "published_parsed", "updated_parsed"):
        parsed_date = getattr(entry, date_attr, None)
        if parsed_date:
            return int(time.mktime(parsed_date))
    return 0


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
parser.add_option(
    "-r",
    "--randomize",
    action="store_true",
    dest="randomize",
    default=False,
    help="randomize merged items instead of date-sorted output",
)
parser.add_option(
    "--markdown-extended",
    action="store_true",
    dest="markdown_extended",
    default=False,
    help="include extended summary/content text in markdown output",
)
parser.add_option(
    "--markdown-extended-size",
    dest="markdown_extended_size",
    default=1000,
    help="maximum size of extended text in markdown output, default 1000",
)

(options, args) = parser.parse_args()

allitem = {}

for url in args:
    d = feedparser.parse(url)

    for el in d.entries:
        elepoch = parse_entry_epoch(el)
        h = hashlib.md5()
        h.update(el.link.encode("utf-8"))
        linkkey = h.hexdigest()
        allitem[linkkey] = {}
        allitem[linkkey]["link"] = str(el.link)
        allitem[linkkey]["epoch"] = int(elepoch)
        allitem[linkkey]["updated"] = getattr(el, "updated", "")
        if "title" in el:
            allitem[linkkey]["title"] = html.unescape(el.title)
        else:
            cleantext = BeautifulSoup(getattr(el, "summary", ""), "lxml").text
            allitem[linkkey]["title"] = cleantext[: int(options.summarysize)]
        allitem[linkkey]["extended"] = extract_extended_text(el)

itemlist = []

for something in list(allitem.keys()):
    epochkeytuple = (allitem[something]["epoch"], something)
    itemlist.append(epochkeytuple)

itemlist.sort()
itemlist.reverse()

if options.randomize:
    random.shuffle(itemlist)

RenderMerge(itemlist, options.output)
