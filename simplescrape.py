#!/usr/bin/python
import sys, base64, urllib, urllib.request, urllib.error, urllib.parse, tempfile, os, time
from lxml import etree
from hashlib import md5
"""
Little helper lib for web scraping.
"""

def dl2(url, referrer=None, ua=None, data=None, auth=None, doCache=True):
    """
    Simplified downloader for scraping.  With an extremely simple cache mechanism.

    url - url to download
    referrer - referrer to use
    ua - user agent
    data - POST data to send
    auth - authentication (http basic), dict must contain:
        realm, user, passwd
    """
    # first check the tempfile to see if we cached this:
    cache = os.path.join(tempfile.gettempdir(),md5(url.encode('ascii')).hexdigest())
    if doCache and os.path.exists(cache):
        #print("CACHED")
        return open(cache,'rb').read()
    request = urllib.request.Request(url)
    if data is not None:
        request.add_data(urllib.urlencode(data))
    if referrer is not None:
        request.add_header('Referrer',referrer)
    if ua is not None:
        request.add_header('User-Agent', ua)
    if auth is not None:
        uauth = urllib.request.HTTPBasicAuthHandler()
        uauth.add_password(realm=auth["realm"], uri=request, user=auth["user"], passwd=auth["passwd"])
        urllib.request.install_opener(urllib.build_opener(uauth))
    p = urllib.request.urlopen(request)
    result = p.read()
    time.sleep(5) # keep it slow to prevent being banned
    if doCache:
        open(cache,'wb').write(result)
    return result

def autoUnpage(firstPageUrl, nextXpath, dlFunc=dl2):
    """
    Automatically unpages webpages with pagination.
    Yields each page as a lxml document.

    firstPageUrl - url of first page to load (should have a pagination on it)
    nextXpath - xpath expression to extract next page URL
    dlFunc - function to use to load pages, given one argument that is the next url
    """
    current = firstPageUrl
    while True:
        contents = dlFunc(current)
        yield contents
        # extract the next link
        match = docExtract({'next': nextXpath}, contents)
        if 'next' not in match: break
        # possible for there to be multiple next links
        if isinstance(match['next'],list): match['next'] = match['next'][0]
        current = urllib.parse.urljoin(firstPageUrl,match['next'])

def docExtractR(map,doc):
    """
    Recursive document extract.
    See: docExtract
    """
    data = {}
    for k,v in map.items():
        if v==None: continue
        if isinstance(v,dict):
            if not 'each' in v: continue
            val = doc.xpath(v['each'])
            news = dict(v)
            del news['each']
            data[k] = []
            for doc in val:
                data[k].append( docExtractR(news,doc) )
        else:
            val = doc.xpath(v)
            # we don't care about unicode! explicitly destroy it
            if len(val) > 1:
                data[k] = []
                for v in val:
                    data[k].append(v.encode('ascii', 'xmlcharrefreplace').decode('ascii') )
            else:
                for v in val:
                    data[k] = v.encode('ascii', 'xmlcharrefreplace').decode('ascii')
    return data

def docExtract(map,html):
    """
    Document extract.

    html - html document to extract from
    map - data to extract
    """
    if not etree.iselement(html):
        html = etree.HTML(html)
    return docExtractR(map,html)
