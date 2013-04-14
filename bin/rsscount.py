#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# a at foo dot be - Alexandre Dulaunoy - http://www.foo.be/cgi-bin/wiki.pl/RssAny
#
# rsscount.py is a simple script to count how many items in a RSS feed per day
#
# The output is epoch + the number of changes separated with a tab.
#
# This is used to build statistic like the wiki creativity index.             
#

import feedparser
import sys,os
import time
import datetime
from optparse import OptionParser


feedparser.USER_AGENT = "rsscount.py +http://www.foo.be/"


usage = "usage: %prog url(s)"
parser = OptionParser(usage)


(options, args) = parser.parse_args()

if args is None:
    print usage

 
counteditem = {}

for url in args:

        d = feedparser.parse(url)

        for el in d.entries:

		try:
                	eldatetime = datetime.datetime.fromtimestamp(time.mktime(el.modified_parsed))
		except AttributeError:
			# discard RSS without pubDate grrr...
			break
		
		
		eventdate = eldatetime.isoformat(' ').split(' ',1)
		edate = eventdate[0].replace("-","")

 		if counteditem.has_key(edate):
			counteditem[edate] = counteditem[edate] + 1
		else:
			counteditem[edate] = 1


for k in counteditem.keys():

	print unicode(k).encode("utf-8")+"\t"+ unicode(counteditem[k]).encode("utf-8")


