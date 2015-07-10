#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Sample Script
    Version 0.1
"""

from optparse import OptionParser
from time import sleep

import logging
import json
import re
import requests
import shutil
import sys

FORMAT = '%(asctime)-15s - %(message)s'
LOGGER = logging.getLogger('scriptlogger')
LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter(FORMAT))
LOGGER.addHandler(ch)


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36'
    }

def parse_page(url):
    ''' Parses a given HTML string to find img URL and the link to the next page
        returns: (img_url, next_page_url)
    '''
    image = ""
    title = ""
    next_url = ""

    r = requests.get(url, headers=HEADERS)
    LOGGER.debug("Parsing %s ..." % url)
    if r.text:
        clean_html = r.text.replace("\n", "")
        try:
            m = re.search(r'src="(?P<url>http://cdn\d\.cad-comic\.com/comics/cad-[0-9]{8}-[a-f0-9]{5}\..+)" alt="(?P<title>.+?)" title=', clean_html)
            image = m.group('url')
            title = m.group('title')
            LOGGER.debug("'%s' - %s" % (m.group('title'), m.group('url')))
        except AttributeError as e:
            LOGGER.error("Faild parsing page!")
            LOGGER.error(r.text)
            raise e
            sys.exit(1)

        try:
            m2 = re.search(r'href="(?P<next_url>/cad/\d{8})" class="nav-next"', clean_html)
            next_url = "http://www.cad-comic.com" + m2.group('next_url')
            LOGGER.debug("Next page: %s" % next_url)
        except AttributeError as e:
            LOGGER.debug("Last page. No link to next comic.")

    else:
        LOGGER.error("Couldn't fetch %s" % url)

    return (image, title, next_url)

def save_img(url):
    ''' Fetches and saves the img to the local FS
    '''
    filename = url.split("/")[-1]
    LOGGER.debug("saving image as %s" % filename)

    r = requests.get(url, headers=HEADERS, stream=True)
    if r.raw:
        with open(filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)
            f.close()

def main():
    parser = OptionParser()
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="print debug messages")
    (options, args) = parser.parse_args()

    if options.verbose:
        LOGGER.setLevel(logging.DEBUG)

    if len(sys.argv) > 1:
        metadata = {}
        url = sys.argv[1]
        while True:
            img_url, img_title, next_url= parse_page(url)
            if img_url:
                metadata[img_url.split("/")[-1]] = img_title
                save_img(img_url)
            if next_url:
                url = next_url
                sleep(0.1)
            else:
                break

        if metadata:
            with open('metadata.json', 'w') as mf:
                json.dump(metadata, mf, sort_keys=True, indent=4, separators=(',', ': '))

    else:
        LOGGER.error("You need to specify a starting url!")

if __name__ == '__main__':
    main()
