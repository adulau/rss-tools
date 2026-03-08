#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# a at foo dot be - Alexandre Dulaunoy - https://github.com/adulau/rss-tools
#
# Directory-to-feed converter.
#
# Walks a local directory tree and exposes file updates as either RSS (default)
# or Atom output. Designed for quick static publishing workflows.

import os, fnmatch
import socket
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


def date_as_atom(value):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(value))


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

    feed = ET.tostring(RSSroot, encoding="unicode")
    return feed


def build_atom(myitem, maxitem):

    atom_ns = "http://www.w3.org/2005/Atom"
    ET.register_namespace("", atom_ns)

    atom_root = ET.Element("{%s}feed" % atom_ns)

    ET.SubElement(atom_root, "{%s}title" % atom_ns).text = "RSS feed of " + str(title)

    ET.SubElement(atom_root, "{%s}link" % atom_ns, {"href": link})
    ET.SubElement(atom_root, "{%s}id" % atom_ns).text = link or (prefixurl + str(title))
    ET.SubElement(atom_root, "{%s}updated" % atom_ns).text = date_as_atom(time.time())
    ET.SubElement(atom_root, "{%s}generator" % atom_ns).text = (
        "A directory RSSified by rssdir.py " + version
    )

    for bloodyitem in myitem[0:maxitem]:

        atom_entry = ET.SubElement(atom_root, "{%s}entry" % atom_ns)
        ET.SubElement(atom_entry, "{%s}title" % atom_ns).text = bloodyitem[1]
        entry_url = prefixurl + bloodyitem[1]
        ET.SubElement(atom_entry, "{%s}link" % atom_ns, {"href": entry_url})
        ET.SubElement(atom_entry, "{%s}id" % atom_ns).text = entry_url
        ET.SubElement(atom_entry, "{%s}updated" % atom_ns).text = date_as_atom(
            bloodyitem[0]
        )
        ET.SubElement(atom_entry, "{%s}summary" % atom_ns).text = entry_url

    feed = ET.tostring(atom_root, encoding="unicode")
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
    help="set a title to the rss feed, default using directory and hostname",
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
parser.set_defaults(output_format="rss")
parser.add_option(
    "--rss",
    action="store_const",
    const="rss",
    dest="output_format",
    help="generate RSS output (default format)",
)
parser.add_option(
    "--atom",
    action="store_const",
    const="atom",
    dest="output_format",
    help="generate Atom output",
)

(options, args) = parser.parse_args()

if "--rss" in sys.argv and "--atom" in sys.argv:
    print("Please choose either --rss or --atom")
    parser.print_help()
    sys.exit(1)

if options.prefix is None:
    prefixurl = ""
else:
    prefixurl = options.prefix

if options.link is None:
    link = options.prefix
else:
    link = options.link

if options.maxitem is None:
    maxitem = 32
else:
    maxitem = options.maxitem

if not args:
    print("Missing directory")
    parser.print_help()
    sys.exit(0)

source_directory = args[0]

if options.title is None:
    directory_name = os.path.basename(os.path.abspath(source_directory))
    system_name = socket.gethostname()
    title = f"{directory_name} on {system_name}"
else:
    title = options.title

file_to_list = []
for x in all_files(source_directory):
    file_to_list.append(x)

mylist = date_files(file_to_list)

mylist.sort()
mylist.reverse()

if options.output_format == "atom":
    print(complete_feed(build_atom(mylist, maxitem)))
else:
    print(complete_feed(build_rss(mylist, maxitem)))
