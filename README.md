RSS tools
=========

Following an old idea from 2007 published on my blog post called [RSS Everything?](http://www.foo.be/cgi-bin/wiki.pl/2007-02-11_RSS_Everything), this is a set of tools to
work on RSS (Really Simple Syndication) in an [Unix way](http://en.wikipedia.org/wiki/Unix_philosophy).

The code committed in this repository is old Python code from 2007, it might break your PC, kill your cat or the Flying Spaghetti Monster might loose a ball.  

Forks and pull requests more than welcome. You have been warned the code was just there to experiment RSS workflows.

Requirements
------------

* Python 2.x
* Feedparser

rsscluster.py
-------------

rsscluster.py is a simple script to cluster items from an rss feed based on a time interval (expressed in number of days).
The maxitem is the number of item maximum kept after the clustering. An example use is for del.icio.us/pinboard.in where 
you can have a lot of bookmarks during one day and you want to cluster them in one single item per a defined time slot in RSS or in (X)HTML.

    rsscluster.py --interval 2 --maxitem 20 "http://del.icio.us/rss/adulau" >adulau.xml

rsscount.py
-----------

rsscount.py is a simple script to count how many items are in a RSS feed per day. This is used to build the [wiki creativity index](http://www.foo.be/cgi-bin/wiki.pl/WikiCreativityIndex). There is no limit for url arguments.

    rsscount.py "<rss_url>" | sort

rssdir.py
---------

rssdir is a simply-and-dirty script to rssify any directory on the filesystem.

    rssdir.py --prefix http://www.foo.be/cours/ . >rss.xml

rssinternetdraft.py
-------------------

rssinternetdraft is a simple test to read a mbox file and generate an RSS from the subject.

rssmerge.py
-----------

rssmerge.py is a simple script to gather rss feed and merge them in reverse time order. Useful to keep track of recent events.

    python2.5 --maxitem 30 --output phtml "http://api.flickr.com/services/feeds/photos_public.gne?id=31797858@N00&lang=en-us&format=atom"  "http://www.foo.be/cgi-bin/wiki.pl?action=journal&tile=AdulauMessyDesk"
    
  
