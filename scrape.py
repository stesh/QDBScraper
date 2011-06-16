#!/usr/bin/env python

__author__ == 'Stephen Shaw <stesh@netsoc.tcd.ie>'

import sys
import codecs
import re

from datetime import datetime
from htmlentitydefs import name2codepoint

from BeautifulSoup import BeautifulSoup, Tag


class Quote(object):
    def __init__(self, filename):
        with codecs.open(filename, 'r', 'utf-8') as infile:
            html = infile.read()
            self.soup = BeautifulSoup(html)
    
    
    def blockquotes(self):
        return self.soup.findAll('blockquote')

    def spans(self):
        return self.soup.findAll('span')

    def upvotes(self):
        return int(self.spans()[2].string[1:])
        
    def downvotes(self):
        return int(self.spans()[3].span.string)

    def number(self):
        return int(self.spans()[1].string[1:])

    def submission_date(self):
        subdate = self.spans()[5].string
        return datetime.strptime(subdate, "%Y-%m-%d %H:%M %Z")
        

    def contents(self):
        blockquote = self.soup.blockquote.p.contents
        blockquote = [unhtml(x.strip()) for x in blockquote if not isinstance(x, Tag)]
        return u'\n'.join(blockquote)

    def notes(self):
        div = self.soup.findAll('div', {'class': 'quote-notes'})
        if len(div) > 0:
            contents = div[0].contents[1].contents[1].strip()
            return unhtml(contents)
        else:
            return None

    def tags(self):
        div = self.soup.findAll('div', {'class': 'quote-tags'})
        return [link.string for link in div[0].findAll('a')] if len(div) > 0 else []


def unhtml(text):
    entity = re.compile("&#?[\w]+;")
    unientity = re.compile("&#x?[0-9A-F]+;")
    txt = text[:]
    matches = set(re.findall(entity, text))
    for m in matches:
        if m[1:-1] in name2codepoint.keys():
            codepoint = name2codepoint[m[1:-1]]
        elif unientity.match(m):
            (base, cut) = (16,3) if 'x' in m else (10,2)
            codepoint = int(m[cut:-1], base) 
        txt = re.sub(m, unichr(codepoint), txt)
    txt = re.sub(re.compile("\xa0+"), u" ", txt)
    return txt

            

def main():
    filenames = sys.argv[1:]
    for filename in filenames:
        quote = Quote(filename)
        print quote.contents()
        print quote.submission_date()

if __name__ == '__main__':
    sys.exit(main())
