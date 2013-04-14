#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# a at foo dot be - Alexandre Dulaunoy - http://www.foo.be/cgi-bin/wiki.pl/RssAny
#
# rsscluster.py is a simple script to cluster items from an rss feed based on a
#               time interval (expressed in number of days). The maxitem is the
#               number of item maximum after the clustering.
#
# an example use is for del.icio.us where you can have a lot of bookmarks during
# one day and you want to cluster them in one single item in RSS or in (X)HTML.
#               
# example of use : 
#  python2.5 rsscluster.py --interval 5 --maxitem 20 "http://del.icio.us/rss/adulau" >adulau.xml

import feedparser
import sys,os
import time
import datetime
import xml.etree.ElementTree as ET
import hashlib
from optparse import OptionParser

#print sys.stdout.encoding 
version = "0.2"

feedparser.USER_AGENT = "rsscluster.py "+ version + " +http://www.foo.be/"


def date_as_rfc(value):
	return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(value))


def build_rss(myitem,maxitem):

	RSSroot = ET.Element( 'rss', {'version':'2.0'} )
	RSSchannel = ET.SubElement( RSSroot, 'channel' )

	ET.SubElement( RSSchannel, 'title' ).text = 'RSS cluster of ' + str(url) +' per '+options.interval+' days'
	ET.SubElement( RSSchannel, 'link' ).text = str(url)
	ET.SubElement( RSSchannel, 'description' ).text = 'RSS cluster of ' + str(url) +' per '+options.interval+' days'
	ET.SubElement( RSSchannel, 'generator' ).text = 'by rsscluster.py ' + version
	ET.SubElement( RSSchannel, 'pubDate' ).text = date_as_rfc(time.time())

	for bloodyitem in myitem[0:maxitem]:

		RSSitem = ET.SubElement ( RSSchannel, 'item' )
		ET.SubElement( RSSitem, 'title' ).text = 'clustered data of ' + date_as_rfc(float(bloodyitem[0])) +" for "+ str(url)
		ET.SubElement( RSSitem, 'pubDate' ).text = date_as_rfc(float(bloodyitem[0]))
		ET.SubElement( RSSitem, 'description').text = bloodyitem[1]
        h = hashlib.md5()
        h.update(bloodyitem[1])
        ET.SubElement( RSSitem, 'guid').text = h.hexdigest()

	RSSfeed = ET.ElementTree(RSSroot)
	feed = ET.tostring(RSSroot)
	return feed


def complete_feed(myfeed):

	myheader = '<?xml version="1.0"?>'
	return myheader + str(myfeed)

def DaysInSec(val):

    return int(val)*24*60*60

usage = "usage: %prog [options] url"
parser = OptionParser(usage)

parser.add_option("-m","--maxitem",dest="maxitem",help="maximum item to list in the feed, default 200")
parser.add_option("-i","--interval",dest="interval",help="time interval expressed in days, default 1 day")

#2007-11-10 11:25:51
pattern = '%Y-%m-%d %H:%M:%S'

(options, args) = parser.parse_args()

if options.interval == None:
        options.output = 1

if options.maxitem == None:
        options.maxitem = 200


if len(args) != 1:
    parser.print_help()
    parser.error("incorrect number of arguments")

allitem = {}
url = args[0]

d = feedparser.parse(url)

interval = DaysInSec(options.interval)

previousepoch = []
clusteredepoch = []
tcluster = []

for el in d.entries:

    eldatetime = datetime.datetime.fromtimestamp(time.mktime(el.modified_parsed))
    elepoch = int(time.mktime(time.strptime(unicode(eldatetime), pattern)))

    if len(previousepoch):

        #print el.link, int(previousepoch[0])-int(elepoch), interval

        if len(clusteredepoch):
            value = clusteredepoch.pop()
        else:
            value = ""

        clusteredepoch.append(value+" <a href=\""+el.link+"\">"+el.title+"</a>")


        if not ((int(previousepoch[0])-int(elepoch)) < interval):

            value = clusteredepoch.pop()

            starttimetuple = datetime.datetime.fromtimestamp(previousepoch[0])
            endttimetuple = datetime.datetime.fromtimestamp(previousepoch.pop())
            clusteredepoch.append(value+ " from: "+unicode(starttimetuple.ctime())+" to: "+unicode(endttimetuple.ctime()))
            startdatelist = unicode(previousepoch[0]),unicode(clusteredepoch[len(clusteredepoch)-1])
            tcluster.append(startdatelist)
            del previousepoch[0:len(previousepoch)]
            del clusteredepoch[0:len(clusteredepoch)]
    else:
            clusteredepoch.append(" <a href=\""+el.link+"\">"+el.title+"</a>")
    previousepoch.append(elepoch)

# if last cluster list was not complete, we add the time period information.
if len(previousepoch):
    value = clusteredepoch.pop()
    starttimetuple = datetime.datetime.fromtimestamp(previousepoch[0])
    endttimetuple = datetime.datetime.fromtimestamp(previousepoch.pop())
    clusteredepoch.append(value+ " from: "+unicode(starttimetuple.ctime())+" to: "+unicode(endttimetuple.ctime()))
    del previousepoch[0:len(previousepoch)]


tcluster.sort()
tcluster.reverse()
print complete_feed(build_rss(tcluster,int(options.maxitem)))



