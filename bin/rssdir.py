# rssdir.py
# a at foo dot be - Alexandre Dulaunoy - http://www.foo.be/cgi-bin/wiki.pl/RssAny
#
# rssdir is a simply-and-dirty script to rssify any directory on the filesystem.
#
# an example of use on the current directory :
#
# python3 /usr/local/bin/rssdir.py --prefix http://www.foo.be/cours/ . >rss.xml
#

import os, fnmatch
import time
import sys
import xml.etree.ElementTree as ET
from optparse import OptionParser

version = "0.2"

# recursive list file function from the ASPN cookbook
def all_files(root, patterns="*", single_level=False, yield_folders=False):
    patterns = patterns.split(";")
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break
        if single_level:
            break


def date_files(filelist):
    date_filename_list = []

    for filename in filelist:
        stats = os.stat(filename)
        last_update = stats[8]
        date_filename_tuple = last_update, filename
        date_filename_list.append(date_filename_tuple)
    return date_filename_list


def date_as_rfc(value):
    return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(value))


def build_rss(myitem, maxitem):

    RSSroot = ET.Element("rss", {"version": "2.0"})
    RSSchannel = ET.SubElement(RSSroot, "channel")

    ET.SubElement(RSSchannel, "title").text = "RSS feed of " + str(title)
    ET.SubElement(RSSchannel, "link").text = link
    ET.SubElement(RSSchannel, "description").text = (
        "A directory RSSified by rssdir.py " + version
    )
    ET.SubElement(RSSchannel, "generator").text = (
        "A directory RSSified by rssdir.py " + version
    )
    ET.SubElement(RSSchannel, "pubDate").text = date_as_rfc(time.time())

    for bloodyitem in myitem[0:maxitem]:

        RSSitem = ET.SubElement(RSSchannel, "item")
        ET.SubElement(RSSitem, "title").text = bloodyitem[1]
        ET.SubElement(RSSitem, "pubDate").text = date_as_rfc(bloodyitem[0])
        ET.SubElement(RSSitem, "description").text = prefixurl + bloodyitem[1]
        ET.SubElement(RSSitem, "guid").text = prefixurl + bloodyitem[1]

    RSSfeed = ET.ElementTree(RSSroot)
    feed = ET.tostring(RSSroot)
    return feed


def complete_feed(myfeed):

    myheader = '<?xml version="1.0"?>'
    return myheader + str(myfeed)


usage = "usage: %prog [options] directory"
parser = OptionParser(usage)

parser.add_option(
    "-p",
    "--prefix",
    dest="prefix",
    default="",
    help="http prefix to be used for each entry, default none",
)
parser.add_option(
    "-t",
    "--title",
    dest="title",
    help="set a title to the rss feed, default using prefix",
    type="string",
)
parser.add_option(
    "-l",
    "--link",
    dest="link",
    help="http link set, default is prefix and none if prefix not set",
)
parser.add_option(
    "-m",
    "--maxitem",
    dest="maxitem",
    help="maximum item to list in the feed, default 32",
    default=32,
    type="int",
)

(options, args) = parser.parse_args()

if options.prefix is None:
    prefixurl = ""
else:
    prefixurl = options.prefix

if options.link is None:
    link = options.prefix
else:
    link = options.link

if options.title is None:
    title = options.prefix
else:
    title = options.title

if options.maxitem is None:
    maxitem = 32
else:
    maxitem = options.maxitem

if not args:
    parser.print_help()
    sys.exit(0)

file_to_list = []
for x in all_files(args[0]):
    file_to_list.append(x)

mylist = date_files(file_to_list)

mylist.sort()
mylist.reverse()

print(complete_feed(build_rss(mylist, maxitem)))
