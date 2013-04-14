#
# quick-and-dirty(tm) script to gather IETF Internet-Draft announce
# from a mbox and to generate a nice RSS feed of the recent announce.
#
# for more information : http://www.foo.be/ietf/id/

import mailbox
import time
import re
import xml.etree.ElementTree as ET

date_rfc2822 = "%a, %d %b %Y %H:%M:%S"

tmsg = []

def date_as_rfc(value):
        return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(value))

def build_rss(myitem,maxitem):

        RSSroot = ET.Element( 'rss', {'version':'2.0'} )
        RSSchannel = ET.SubElement( RSSroot, 'channel' )

        ET.SubElement( RSSchannel, 'title' ).text = 'Latest Internet-Draft (IDs) Published - IETF - custom RSS feed'
        ET.SubElement( RSSchannel, 'link' ).text = 'http://www.foo.be/ietf/id/' 
        ET.SubElement( RSSchannel, 'description' ).text = 'Latest Internet-Draft (IDs) Published - IETF - custom RSS feed' 
        ET.SubElement( RSSchannel, 'generator' ).text = 'rssany extended for parsing IETF IDs - http://www.foo.be/cgi-bin/wiki.pl/RssAny'
#        ET.SubElement( RSSchannel, 'pubDate' ).text = date_as_rfc(time.time())
        ET.SubElement( RSSchannel, 'pubDate' ).text = date_as_rfc(time.time()-10000)

        for bloodyitem in myitem[0:maxitem]:
                RSSitem = ET.SubElement ( RSSchannel, 'item' )
                ET.SubElement( RSSitem, 'title' ).text = bloodyitem[1]
                ET.SubElement( RSSitem, 'pubDate' ).text = date_as_rfc(bloodyitem[0])
                ET.SubElement( RSSitem, 'description').text = '<pre>'+bloodyitem[2]+'</pre>'
                ET.SubElement( RSSitem, 'guid').text = "http://tools.ietf.org/html/"+bloodyitem[3]
                ET.SubElement( RSSitem, 'link').text = "http://tools.ietf.org/html/"+bloodyitem[3]
        RSSfeed = ET.ElementTree(RSSroot)
        feed = ET.tostring(RSSroot)
        return feed

for message in mailbox.mbox('/var/spool/mail/ietf'):
    subject = message['subject']
    date = message['date']
    date_epoch = int(time.mktime(time.strptime(date[0:-12], date_rfc2822))) 
    message_id = message['Message-Id']
    body =  message.get_payload()[0].get_payload()
    id = subject.split(":")[1].split(".")[0]
    tmsg.append([date_epoch,subject,body,id])

tmsg.sort()
tmsg.reverse()
print build_rss(tmsg,100)
