#!/usr/bin/python3
# [rssfind.py](https://github.com/adulau/rss-tools/blob/master/bin/rssfind.py) is a simple script designed to discover RSS or Atom feeds from a given URL.
#
# It employs two techniques:
#
# - The first involves searching for direct link references to the feed within the HTML page.
# - The second uses a brute-force approach, trying a series of known paths for feeds to determine if they are valid RSS or Atom feeds.
#
# The script returns an array in JSON format containing all the potential feeds it discovers.

import sys
import urllib.parse
from optparse import OptionParser
import random

import feedparser
import orjson as json
import requests
from bs4 import BeautifulSoup as bs4

brute_force_urls = [
    "index.xml",
    "feed/index.php",
    "feed.xml",
    "feed.atom",
    "feed.rss",
    "feed.json",
    "feed.php",
    "feed.asp",
    "posts.rss",
    "blog.xml",
    "atom.xml",
    "podcasts.xml",
    "main.atom",
    "main.xml",
]
random.shuffle(brute_force_urls)


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


def brutefindfeeds(url=None, disable_strict=False):
    if url is None:
        return None
    found_urls = []
    found_valid_feeds = []
    parsed_url = urllib.parse.urlparse(url)
    for path in brute_force_urls:
        url = f"{parsed_url.scheme}://{parsed_url.hostname}/{path}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            found_urls.append(url)
    for url in list(set(found_urls)):
        f = feedparser.parse(url)
        if f.entries:
            if url not in found_valid_feeds:
                found_valid_feeds.append(url)
    if disable_strict:
        return list(set(found_urls))
    else:
        return found_valid_feeds


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

parser.add_option(
    "-b",
    "--brute-force",
    action="store_true",
    default=False,
    help="Search RSS/Atom feeds by brute-forcing url path (useful if the page is missing a link entry)",
)

(options, args) = parser.parse_args()

if not options.link:
    print("Link/url missing - -l option")
    parser.print_help()
    sys.exit(0)

if not options.brute_force:
    print(
        json.dumps(
            findfeeds(url=options.link, disable_strict=options.disable_strict)
        ).decode("utf-8")
    )
else:
    print(
        json.dumps(
            brutefindfeeds(url=options.link, disable_strict=options.disable_strict)
        ).decode("utf-8")
    )
