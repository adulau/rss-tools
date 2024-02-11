# RSS tools

Following an old idea from 2007, published in my ancient blog post titled [RSS Everything?](http://www.foo.be/cgi-bin/wiki.pl/2007-02-11_RSS_Everything), this set of tools is designed to work with RSS (Really Simple Syndication) in a manner consistent with the [Unix philosophy](http://en.wikipedia.org/wiki/Unix_philosophy).

The code committed in this repository was originally old Python code from 2007. It might break your PC, harm your cat, or cause the Flying Spaghetti Monster to lose a meatball.

As 2024 marks the resurgence of RSS and Atom, I decided to update my rudimentary RSS tools to make them contemporary.

[Forks and pull requests](https://github.com/adulau/rss-tools) are more than welcome. Be warned: this code was initially created for experimenting with RSS workflows.

## Requirements

* Python 3 
* Feedparser

## Tools

### rsscluster

[rsscluster.py](https://github.com/adulau/rss-tools/blob/master/bin/rsscluster.py) is a simple script that clusters items from an RSS feed based on a specified time interval, expressed in days.
The `maxitem` parameter defines the maximum number of items to keep after clustering. This script can be particularly useful for platforms like Mastodon, where a user might be very active in a single day and you want to cluster their activity into a single RSS item for a defined time slot.

~~~shell
rsscluster.py --interval 2 --maxitem 20 "http://paperbay.org/@a.rss" > adulau.xml
~~~

### rssmerge

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

`python3 rssmerge.py --maxitem 5 --output markdown "http://api.flickr.com/services/feeds/photos_public.gne?id=31797858@N00&lang=en-us&format=atom"  "http://www.foo.be/cgi-bin/wiki.pl?action=journal&tile=AdulauMessyDesk" "http://paperbay.org/@a.rss" "http://infosec.exchange/@adulau.rss"`

#### Sample output

- [harvesting society #street #streetphotography #paris #societ](https://paperbay.org/@a/111908018263388808)
- [harvesting society](https://www.flickr.com/photos/adulau/53520731553/)
- [late in the night#bynight #leica #streetphotography #street ](https://paperbay.org/@a/111907960149305774)
- [late in the night](https://www.flickr.com/photos/adulau/53520867709/)
- [geography of illusion#photography #art #photo #bleu #blue #a](https://paperbay.org/@a/111907911876620745)


### rssdir

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

### rsscount

[rsscount.py](https://github.com/adulau/rss-tools/blob/master/bin/rsscount.py) is a straightforward script designed to count the number of items in an RSS feed per day. It is utilized to construct the [wiki creativity index](http://www.foo.be/cgi-bin/wiki.pl/WikiCreativityIndex). The script accepts an unlimited number of URL arguments. It can be used to feed statistical tools.

~~~shell
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
~~~

## License

rss-tools are open source/free software licensed under the permissive 2-clause BSD license.

Copyright 2007-2024 Alexandre Dulaunoy

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Scripts which need to be converted and are there for historical purpose

rssinternetdraft.py
-------------------

rssinternetdraft is a simple test to read a mbox file and generate an RSS from the subject.

