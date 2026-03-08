#!/usr/bin/python3
#
# a at foo dot be - Alexandre Dulaunoy - https://github.com/adulau/rss-tools
# RSS/Atom feed discovery utility.
#
# Discovery strategy:
# - Parse HTML for declared alternate feed links and feed-looking anchors.
# - Optionally brute-force common feed URL paths.
#
# Output is a JSON array of discovered URLs. In strict mode (default), only
# feeds with entries are returned.

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

    try:
        response = requests.get(
            url, headers=headers, timeout=10, allow_redirects=True
        )
    except requests.RequestException:
        return []
    raw = response.text
    base_url = response.url
    results = []
    discovered_feeds = []
    html = bs4(raw, features="lxml")
    feed_urls = html.findAll("link", rel="alternate")
    if feed_urls:
        for f in feed_urls:
            tag = f.get("type", None)
            if tag:
                tag = tag.lower()
                if (
                    "feed" in tag
                    or "rss" in tag
                    or "atom" in tag
                    or "xml" in tag
                ):
                    href = f.get("href", None)
                    if href:
                        discovered_feeds.append(
                            urllib.parse.urljoin(base_url, href)
                        )

    ahreftags = html.findAll("a")

    for a in ahreftags:
        href = a.get("href", None)
        if href:
            href_lower = href.lower()
            if (
                "feed" in href_lower
                or "rss" in href_lower
                or "atom" in href_lower
                or "xml" in href_lower
            ):
                discovered_feeds.append(urllib.parse.urljoin(base_url, href))

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
    try:
        base_response = requests.get(
            url, headers=headers, timeout=10, allow_redirects=True
        )
    except requests.RequestException:
        return []
    parsed_url = urllib.parse.urlparse(base_response.url)
    for path in brute_force_urls:
        url = f"{parsed_url.scheme}://{parsed_url.hostname}/{path}"
        try:
            r = requests.get(
                url, headers=headers, timeout=10, allow_redirects=True
            )
        except requests.RequestException:
            continue
        if r.status_code == 200:
            found_urls.append(r.url)
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
    action="store_true",
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

feeds = findfeeds(url=options.link, disable_strict=options.disable_strict)

if options.brute_force:
    brute_force_feeds = brutefindfeeds(
        url=options.link, disable_strict=options.disable_strict
    )
    feeds = list(set(feeds + brute_force_feeds))

print(json.dumps(feeds).decode("utf-8"))
