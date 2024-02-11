# RSS tools

Following an old idea from 2007, published in my blog post titled [RSS Everything?](http://www.foo.be/cgi-bin/wiki.pl/2007-02-11_RSS_Everything), this set of tools is designed to work with RSS (Really Simple Syndication) in a manner consistent with the [Unix philosophy](http://en.wikipedia.org/wiki/Unix_philosophy).

The code committed in this repository was originally old Python code from 2007. It might break your PC, harm your cat, or cause the Flying Spaghetti Monster to lose a meatball.

As 2024 marks the resurgence of RSS and Atom, I decided to update my rudimentary RSS tools to make them contemporary.

[Forks and pull requests](https://github.com/adulau/rss-tools) are more than welcome. Be warned: this code was initially created for experimenting with RSS workflows.

## Requirements

* Python 3 
* Feedparser

## rsscluster

[rsscluster.py](https://github.com/adulau/rss-tools/blob/master/bin/rsscluster.py) is a simple script that clusters items from an RSS feed based on a specified time interval, expressed in days.
The `maxitem` parameter defines the maximum number of items to keep after clustering. This script can be particularly useful for platforms like Mastodon, where a user might be very active in a single day and you want to cluster their activity into a single RSS item for a defined time slot.

~~~shell
rsscluster.py --interval 2 --maxitem 20 "http://paperbay.org/@a.rss" > adulau.xml
~~~

## rssmerge

[rssmerge.py](https://github.com/adulau/rss-tools/blob/master/bin/rssmerge.py) is a simple script designed to aggregate RSS feeds and merge them in reverse chronological order. It outputs the merged content in text, HTML, or Markdown format. This tool is useful for tracking recent events from various feeds and publishing them on your website.

~~~shell
python3 rssmerge.py --maxitem 30 --output markdown "http://api.flickr.com/services/feeds/photos_public.gne?id=31797858@N00&lang=en-us&format=atom"  "http://www.foo.be/cgi-bin/wiki.pl?action=journal&tile=AdulauMessyDesk" "http://paperbay.org/@a.rss" "http://infosec.exchange/@adulau.rss"
~~~

~~~shell
Usage: rssmerge.py [options] url

Options:
  -h, --help            show this help message and exit
  -m MAXITEM, --maxitem=MAXITEM
                        maximum item to list in the feed, default 200
  -s SUMMARYSIZE, --summarysize=SUMMARYSIZE
                        maximum size of the summary if a title is not present
  -o OUTPUT, --output=OUTPUT
                        output format (text, phtml, markdown), default text
~~~

## rssdir

[rssdir.py](https://github.com/adulau/rss-tools/blob/master/bin/rssdir.py) is a simple and straightforward script designed to convert any directory on the filesystem into an RSS feed.

~~~shell
rssdir.py --prefix https://www.foo.be/cours/ . >rss.xml
~~~

~~~shell
Usage: rssdir.py [options] directory

Options:
  -h, --help            show this help message and exit
  -p PREFIX, --prefix=PREFIX
                        http prefix to be used for each entry, default none
  -t TITLE, --title=TITLE
                        set a title to the rss feed, default using prefix
  -l LINK, --link=LINK  http link set, default is prefix and none if prefix
                        not set
  -m MAXITEM, --maxitem=MAXITEM
                        maximum item to list in the feed, default 32
~~~

## Scripts which need to be converted an are there for historical purpose

rsscount.py
-----------

rsscount.py is a simple script to count how many items are in a RSS feed per day. This is used to build the [wiki creativity index](http://www.foo.be/cgi-bin/wiki.pl/WikiCreativityIndex). There is no limit for url arguments.

    rsscount.py "<rss_url>" | sort

rssinternetdraft.py
-------------------

rssinternetdraft is a simple test to read a mbox file and generate an RSS from the subject.

