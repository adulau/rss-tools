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
SOURCE_PATTERN = re.compile(r"^- Source:\s+`([^`]+)`\s*$")
DAY_FILE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def html_to_markdown(text):
    if not text:
        return ""

    # Some Atom feeds (e.g. Flickr) store HTML content with escaped tags
    # in <content type="html"> payloads. Unescape a few times so the parser
    # can see real HTML nodes such as <a> and <img>.
    normalized = text
    for _ in range(3):
        unescaped = html.unescape(normalized)
        if unescaped == normalized:
            break
        normalized = unescaped

    soup = BeautifulSoup(normalized, "lxml")
    root = soup.body if soup.body else soup

    def render(node):
        if isinstance(node, str):
            return html.unescape(node)

        name = (node.name or "").lower()
        children = "".join(render(child) for child in node.children)

        if name in {"strong", "b"}:
            return f"**{children.strip()}**" if children.strip() else ""
        if name in {"em", "i"}:
            return f"*{children.strip()}*" if children.strip() else ""
        if name == "code":
            return f"`{children.strip()}`" if children.strip() else ""
        if name == "a":
            label = children.strip() or node.get("href", "")
            href = node.get("href", "")
            return f"[{label}]({href})" if href else label
        if name == "img":
            src = node.get("src", "").strip()
            alt = html.unescape(node.get("alt", "")).strip()
            if src:
                return f"![{alt}]({src})"
            return ""
        if name == "br":
            return "\n"
        if name in {"p", "div"}:
            content = children.strip()
            return f"{content}\n\n" if content else ""
        if name in {"ul", "ol"}:
            return f"{children}\n" if children.strip() else ""
        if name == "li":
            content = children.strip()
            return f"- {content}\n" if content else ""
        if name in {"script", "style"}:
            return ""
        return children

    markdown = "".join(render(child) for child in root.children)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
    return markdown


def compact_markdown_description(text, max_words=60):
    if not text:
        return ""

    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Keep list items readable but remove deep indentation/noise.
        lines.append(stripped if stripped.startswith("- ") else stripped.lstrip("- ").strip())

    if not lines:
        return ""

    compact = " ".join(lines)
    # Keep embedded images in summary output so photo-centric feeds are useful.
    compact = re.sub(r"\s*!\[", " ![", compact)
    compact = re.sub(r"\]\(([^)]+)\)", r"](\1)", compact)
    words = compact.split()
    if len(words) <= max_words:
        return compact
    return f'{" ".join(words[:max_words])}…'


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
    if int(summarysize) > 0:
        return cleantext[: int(summarysize)]
    return cleantext


def extract_entry_description(entry):
    html_payload = ""

    if "content" in entry and entry.content:
        for content in entry.content:
            value = getattr(content, "value", "")
            if value:
                html_payload = value
                break

    if not html_payload:
        html_payload = getattr(entry, "summary", "") or getattr(entry, "description", "")

    markdown_description = html_to_markdown(html_payload)

    if markdown_description:
        return markdown_description

    # Fallback for media-first Atom feeds that only expose enclosure links.
    for link in getattr(entry, "links", []):
        if getattr(link, "rel", "") == "enclosure" and getattr(link, "href", ""):
            media_type = getattr(link, "type", "")
            if media_type.startswith("image/") or not media_type:
                return f"![{sanitize_title(entry, 0)}]({link.href})"

    return ""


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
        new_lines.append(f'### [{entry["title"]}]({entry["link"]})\n\n')
        new_lines.append(f"- Source: `{domain}`\n")
        new_lines.append(f"- Time: `{timestamp}`\n")
        compact_description = compact_markdown_description(entry["description"])
        if compact_description:
            new_lines.append(f"- Summary: {compact_description}\n")
        new_lines.append("\n---\n\n")

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


def count_sources(path):
    sources = defaultdict(int)
    if not os.path.exists(path):
        return sources

    with open(path, "r", encoding="utf-8") as fobj:
        for raw_line in fobj:
            match = SOURCE_PATTERN.match(raw_line.strip())
            if match:
                sources[match.group(1)] += 1
    return sources


def update_year_index(destination, year, title_prefix, link_extension):
    pages = list_day_files(destination, year)
    index_path = os.path.join(destination, f"{year}.md")
    source_stats = defaultdict(int)
    total_items = 0

    with open(index_path, "w", encoding="utf-8") as fobj:
        fobj.write(build_front_matter(f"{year}{title_prefix}"))
        if not pages:
            fobj.write("No entries yet.\n")
            return

        fobj.write("## Yearly statistics\n\n")
        for page in pages:
            full_path = os.path.join(destination, page)
            page_day = page[:-3]
            entries_count = count_links(full_path)
            total_items += entries_count
            for source, source_count in count_sources(full_path).items():
                source_stats[source] += source_count
            fobj.write(
                f"- [{page_day}]({page_day}{link_extension}) - {entries_count} item(s)\n"
            )

        fobj.write("\n")
        fobj.write(f"- Total entries: {total_items}\n")
        fobj.write(f"- Active days: {len(pages)}\n")
        fobj.write(f"- Distinct sources: {len(source_stats)}\n")

        if source_stats:
            fobj.write("\n### Source breakdown\n\n")
            for source, count in sorted(
                source_stats.items(), key=lambda item: (-item[1], item[0])
            ):
                fobj.write(f"- `{source}`: {count} item(s)\n")


def list_years_from_days(destination):
    years = set()
    for filename in os.listdir(destination):
        if DAY_FILE_PATTERN.match(filename):
            years.add(filename[:4])
    return sorted(years)


def update_global_index(destination, years, title_prefix, link_extension):
    index_path = os.path.join(destination, "index.md")
    with open(index_path, "w", encoding="utf-8") as fobj:
        fobj.write(build_front_matter(f"Journal index{title_prefix}"))
        fobj.write(
            "This is an automatic journal generated from RSS/Atom feeds.\n\n"
        )
        if not years:
            fobj.write("No yearly pages yet.\n")
            return

        for year in sorted(years, reverse=True):
            day_files = list_day_files(destination, year)
            item_count = 0
            for day_file in day_files:
                item_count += count_links(os.path.join(destination, day_file))
            fobj.write(
                f"- [{year}]({year}{link_extension}) - {len(day_files)} day(s), "
                f"{item_count} item(s)\n"
            )


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
                "description": extract_entry_description(el),
            }

    return list(allitem.values())


def write_journal(entries, destination, maxitem, title_prefix, link_extension):
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

    years = list_years_from_days(destination)
    for year in years:
        update_year_index(destination, year, title_prefix, link_extension)
    update_global_index(destination, years, title_prefix, link_extension)

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
    default=0,
    help=(
        "optional max length for fallback summary text when a title is "
        "missing (0 keeps full text, default 0)"
    ),
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
parser.add_option(
    "-e",
    "--extension",
    dest="extension",
    default=".html",
    help='extension used for day links in the yearly index, default ".html"',
)

(options, args) = parser.parse_args()

if not args:
    parser.error("at least one RSS/Atom URL is required")

entries = collect_entries(args, int(options.summarysize))
link_extension = options.extension if options.extension.startswith(".") else f".{options.extension}"
changes = write_journal(
    entries,
    options.destination,
    int(options.maxitem),
    options.title_prefix,
    link_extension,
)

for day, count in changes:
    print(f"updated {day}.md with {count} new item(s)")

if not changes:
    print("no updates required")
