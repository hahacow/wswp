import re
import urlparse
import urllib2
import time
from datetime import datetime
import robotparser
import Queue
from common import download


def link_crawler(seed_url, link_regex=None, delay=0, max_depth=-1, max_urls=-1, headers=None, user_agent='wswp', proxy=None, num_retries=1):
    # """Crawl from the given seed URL following links matched by link_regex
    # """
    crawl_queue=Queue.deque([seed_url])
    #seen = set(crawl_queue) # keep track which URL's have seen before
    seen={seed_url: 0}
    throttle = Throttle(delay)
    num_urls=0
    headers = headers or {}
    if user_agent:
        headers['User-agent'] = user_agent

    while crawl_queue:
        print 'first url in queue:' +crawl_queue[0]
        print 'last url in queue:'+crawl_queue[-1]
        url = crawl_queue.pop()
        print len(crawl_queue)
        #throttle.wait(url)
        html = download(url,headers, proxy=proxy, num_retries=num_retries)
        links=[]
        print links
        depth=seen[url]
        if depth!=max_depth:
            #if link_regex:
            links.extend(link for link in get_links(html) )
            for link in links:
                print link
                link=normalize(seed_url,link)
                if link not in seen:
                    seen[link]=depth+1
                    if same_domain(seed_url,link):
                        crawl_queue.append(link)


       

class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """
    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}
        
    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()





def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link) # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)


def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc


def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp
        

def get_links(html):
    """Return a list of links from html 
    """
    print 'geting links'
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    #webpage_regex = re.compile(r'''(?i)href=["']([^\s"'<>]+)''')
    # list of all links from the webpage
    return webpage_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1)

