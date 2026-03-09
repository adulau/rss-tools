# RSS tools

Following an old idea from 2007, published in my ancient blog post titled [RSS Everything?](http://www.foo.be/cgi-bin/wiki.pl/2007-02-11_RSS_Everything), this set of tools is designed to work with RSS (Really Simple Syndication) in a manner consistent with the [Unix philosophy](http://en.wikipedia.org/wiki/Unix_philosophy).

The code committed in this repository was originally old Python code from 2007. It might break your PC, harm your cat, or cause the Flying Spaghetti Monster to lose a meatball.

As 2024 marks the resurgence of RSS and Atom[^1], I decided to update my rudimentary RSS tools to make them contemporary.

[Forks and pull requests](https://github.com/adulau/rss-tools) are more than welcome. Be warned: this code was initially created for experimenting with RSS workflows.

## Requirements

* Python 3
* feedparser
* requests (for `rssfind.py`)
* beautifulsoup4 + lxml (for `rssfind.py` and `rssmerge.py`)
* orjson (for `rssfind.py` JSON output)

## Tools

### rssfind

[`rssfind.py`](https://github.com/adulau/rss-tools/blob/master/bin/rssfind.py) discovers RSS/Atom feeds from a given URL.

It uses two techniques:

- Parsing HTML links (`<link rel="alternate">` and feed-looking `<a href>` values).
- Optional brute-force discovery of common feed paths via `--brute-force`.

By default, it only returns valid feeds that contain entries (strict mode). Use `--disable-strict` to include empty-but-discovered candidates.

```shell
Usage: Find RSS or Atom feeds from an URL
usage: rssfind.py [options]

Options:
  -h, --help            show this help message and exit
  -l LINK, --link=LINK  http link where to find one or more feed source(s)
  -d, --disable-strict  Include empty feeds in the list, default strict is enabled
  -b, --brute-force     Search RSS/Atom feeds by brute-forcing url path
                        (useful if the page is missing a link entry)
```

### rsscluster

[`rsscluster.py`](https://github.com/adulau/rss-tools/blob/master/bin/rsscluster.py) clusters items from an RSS feed within a fixed interval (in days). The `maxitem` parameter limits how many resulting cluster entries are kept.

```shell
rsscluster.py --interval 2 --maxitem 20 "http://paperbay.org/@a.rss" > adulau.xml
```

### rssmerge

[`rssmerge.py`](https://github.com/adulau/rss-tools/blob/master/bin/rssmerge.py) aggregates multiple RSS/Atom feeds and merges items in reverse chronological order. Use `--randomize` to shuffle merged items instead of sorting by date.

Supported output formats:

- `text`
- `phtml`
- `markdown`

Markdown output can include an extended summary/content block with:

- `--markdown-extended`
- `--markdown-extended-size`

```shell
python3 rssmerge.py --maxitem 30 --output markdown \
  "http://api.flickr.com/services/feeds/photos_public.gne?id=31797858@N00&lang=en-us&format=atom" \
  "http://www.foo.be/cgi-bin/wiki.pl?action=journal&tile=AdulauMessyDesk" \
  "http://paperbay.org/@a.rss" "http://infosec.exchange/@adulau.rss"
```

```shell
Usage: rssmerge.py [options] url

Options:
  -h, --help            show this help message and exit
  -m MAXITEM, --maxitem=MAXITEM
                        maximum item to list in the feed, default 200
  -s SUMMARYSIZE, --summarysize=SUMMARYSIZE
                        maximum size of the summary if a title is not present
  -o OUTPUT, --output=OUTPUT
                        output format (text, phtml, markdown), default text
  -r, --randomize       randomize merged items instead of date-sorted output
  --markdown-extended   include extended summary/content text in markdown output
  --markdown-extended-size=MARKDOWN_EXTENDED_SIZE
                        maximum size of extended text in markdown output, default 1000
```

#### Sample output from rssmerge

```markdown
- paperbay.org [harvesting society #street #streetphotography #paris #societ](https://paperbay.org/@a/111908018263388808) @Wed Feb 21 20:04:57 2024
- www.flickr.com [harvesting society](https://www.flickr.com/photos/adulau/53520731553/) @Wed Feb 21 19:48:15 2024
```

### rssdir

[`rssdir.py`](https://github.com/adulau/rss-tools/blob/master/bin/rssdir.py) converts a filesystem directory into a feed.

It now supports both output formats:

- RSS (default, `--rss`)
- Atom (`--atom`)

```shell
rssdir.py --prefix https://www.foo.be/cours/ . > rss.xml
rssdir.py --atom --prefix https://www.foo.be/cours/ . > atom.xml
```

```shell
Usage: rssdir.py [options] directory

Options:
  -h, --help            show this help message and exit
  -p PREFIX, --prefix=PREFIX
                        http prefix to be used for each entry, default none
  -t TITLE, --title=TITLE
                        set a title to the rss feed, default using prefix
  -l LINK, --link=LINK  http link set, default is prefix and none if prefix not set
  -m MAXITEM, --maxitem=MAXITEM
                        maximum item to list in the feed, default 32
  --rss                 generate RSS output (default format)
  --atom                generate Atom output
```

### rsscount

[`rsscount.py`](https://github.com/adulau/rss-tools/blob/master/bin/rsscount.py) counts feed entries per day across one or more input URLs. It is used to build statistics such as the [wiki creativity index](http://www.foo.be/cgi-bin/wiki.pl/WikiCreativityIndex).

```shell
python3 rsscount.py https://paperbay.org/@a.rss | sort
20240121	3
20240124	1
20240128	4
20240130	1
20240131	1
20240201	1
20240203	2
20240204	3
20240210	4
```

### rssinternetdraft (legacy)

[`rssinternetdraft.py`](https://github.com/adulau/rss-tools/blob/master/bin/rssinternetdraft.py) is a historical helper script to convert IETF Internet-Draft announcements from an mbox mailbox into RSS. It is currently legacy Python 2 style code and expects a local `/var/spool/mail/ietf` mailbox.

## License

rss-tools are open source/free software licensed under the permissive 2-clause BSD license.

Copyright 2007-2024 Alexandre Dulaunoy

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

[^1]: As web platforms continue to deteriorate in quality, and with the diminishing visibility across various pseudo-social networks coupled with the decline of RSS culture, the emergence of new open-source, federated networks using ActivityPub (an advanced RSS format) seems particularly timely. I believe that reviving open-source tools developed in 2007 for handling RSS is increasingly relevant. Many of these new federated platforms are revitalizing RSS, which is a trend that deserves encouragement and support.
