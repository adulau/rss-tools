#!/usr/bin/python3

import sys
import urllib.parse
from optparse import OptionParser

import feedparser
import orjson as json
import requests
from bs4 import BeautifulSoup as bs4


def findfeeds(url=None, disable_strict=False):
    if url is None:
        return None

    raw = requests.get(url, headers=headers).text
    results = []
    discovered_feeds = []
    html = bs4(raw, features="lxml")
    feed_urls = html.findAll("link", rel="alternate")
    if feed_urls:
        for f in feed_urls:
            tag = f.get("type", None)
            if tag:
                if "feed" in tag or "rss" in tag or "xml" in tag:
                    href = f.get("href", None)
                    if href:
                        discovered_feeds.append(href)

    parsed_url = urllib.parse.urlparse(url)
    base = f"{parsed_url.scheme}://{parsed_url.hostname}"
    ahreftags = html.findAll("a")

    for a in ahreftags:
        href = a.get("href", None)
        if href:
            if "feed" in href or "rss" in href or "xml" in href:
                discovered_feeds.append(f"{base}{href}")

    for url in list(set(discovered_feeds)):
        f = feedparser.parse(url)
        if f.entries:
            if url not in results:
                results.append(url)

    if disable_strict:
        return list(set(discovered_feeds))
    else:
        return results


version = "0.2"

user_agent = f"rssfind.py {version} +https://github.com/adulau/rss-tools"

feedparser.USER_AGENT = user_agent


headers = {"User-Agent": user_agent}

usage = "Find RSS or Atom feeds from an URL\nusage: %prog [options]"

parser = OptionParser(usage)

parser.add_option(
    "-l",
    "--link",
    dest="link",
    help="http link where to find one or more feed source(s)",
)

parser.add_option(
    "-d",
    "--disable-strict",
    action="store_false",
    default=False,
    help="Include empty feeds in the list, default strict is enabled",
)

(options, args) = parser.parse_args()

if not options.link:
    print("URL missing")
    parser.print_help()
    sys.exit(0)

print(
    json.dumps(findfeeds(options.link, disable_strict=options.disable_strict)).decode(
        "utf-8"
    )
)
