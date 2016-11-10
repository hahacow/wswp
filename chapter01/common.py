# -*- coding: utf-8 -*-

import urllib2
import urlparse
import socket

def download1(url):
    """Simple downloader"""
    return urllib2.urlopen(url).read()


def download2(url):
    """Download function that catches errors"""
    print 'Downloading:', url
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
    return html


def download3(url, num_retries=2):
    """Download function that also retries 5XX errors"""
    print 'Downloading:', url
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                html = download3(url, num_retries-1)
    return html


def download4(url, user_agent='wswp', num_retries=2):
    """Download function that includes user agent support"""
    print 'Downloading:', url
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                html = download4(url, user_agent, num_retries-1)
    return html


def download5(url, user_agent='wswp', proxy=None, num_retries=2):
    """Download function with support for proxies"""
    print 'Downloading:', url
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    opener = urllib2.build_opener()
    html = None
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))
    try:
        response=opener.open(request,timeout=10)
        if str(response.getcode())=='200':
            html=response.read()
            print url+ "   has been downloaded  ---" +str(response.getcode())
    except socket.timeout as e:
        print 'Download error:' ,type(e)
        if num_retries > 0:
            html = download5(url, user_agent, proxy, num_retries-1)
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                html = download5(url, user_agent, proxy, num_retries-1)
    return html


download = download5


if __name__ == '__main__':
    download('http://example.webscraping.com')
