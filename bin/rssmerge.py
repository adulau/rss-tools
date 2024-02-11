#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# a at foo dot be - Alexandre Dulaunoy - http://www.foo.be/cgi-bin/wiki.pl/RssAny
#
# rssmerge.py is a simple script to gather rss feed and merge them in reverse
#             time order. Useful to keep track of recent events.
#
# this is still an early prototype and assume that you have full control of the
# remote rss feeds (if not you may have some security issues).
#
# TODO : - rss 2.0 and atom output
#        - full html output
#
# example of use :
#  python3 rssmerge.py --output phtml --maxitem 20 "http://www.foo.be/cgi-bin/wiki.pl?action=journal&tile=AdulauMessyDesk"
#   "http://api.flickr.com/services/feeds/photos_public.gne?id=31797858@N00&lang=en-us&format=atom" "http://a.6f2.net/cgi-bin/gitweb.cgi?
#   p=adulau/.git;a=rss" "http://www.librarything.com/rss/reviews/adulau"  > /tmp/test.inc

import feedparser
import sys, os
import time
import datetime
import hashlib
from optparse import OptionParser
import html
from bs4 import BeautifulSoup

feedparser.USER_AGENT = "rssmerge.py +http://www.foo.be/"


def RenderMerge(itemlist, output="text"):

    i = 0

    if output == "text":
        for item in itemlist:
            i = i + 1
            # Keep consistent datetime representation if not use allitem[item[1]]['updated']
            timetuple = datetime.datetime.fromtimestamp(allitem[item[1]]["epoch"])
            print(
                str(i)
                + ":"
                + allitem[item[1]]["title"]
                + ":"
                + timetuple.ctime()
                + ":"
                + allitem[item[1]]["link"]
            )

            if i == int(options.maxitem):
                break

    if output == "phtml":
        print("<ul>")
        for item in itemlist:
            i = i + 1
            # Keep consistent datetime representation if not use allitem[item[1]]['updated']
            timetuple = datetime.datetime.fromtimestamp(allitem[item[1]]["epoch"])
            print(
                '<li><a href="'
                + str(str(allitem[item[1]]["link"]))
                + '">'
                + str(str(html.escape(allitem[item[1]]["title"])))
                + "</a> --- (<i>"
                + timetuple.ctime()
                + "</i>)</li>"
            )
            if i == int(options.maxitem):
                break
        print("</ul>")

    if output == "markdown":
        for item in itemlist:
            i = i + 1
            timetuple = datetime.datetime.fromtimestamp(allitem[item[1]]["epoch"])
            print(
                "- ["
                + str(html.escape(allitem[item[1]]["title"]))
                + "]("
                + str(allitem[item[1]]["link"])
                + ")"
            )
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

    # print url

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

            print(allitem[linkkey]["title"])


itemlist = []

for something in list(allitem.keys()):
    epochkeytuple = (allitem[something]["epoch"], something)
    itemlist.append(epochkeytuple)

itemlist.sort()
itemlist.reverse()

RenderMerge(itemlist, options.output)
