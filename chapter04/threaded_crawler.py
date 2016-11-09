import time
import threading
import urlparse
import re
from downloader import Downloader

SLEEP_TIME = 1



def threaded_crawler(seed_url, link_regex=None,delay=5, cache=None, max_depth=-1, max_urls=-1, scrape_callback=None, user_agent='wswp', proxies=None, num_retries=1, max_threads=10, timeout=10):
    """Crawl this website in multiple threads
    """
    # the queue of URL's that still need to be crawled
    #crawl_queue = Queue.deque([seed_url])
    crawl_queue = [seed_url]
    # the URL's that have been seen 
    #seen = set([seed_url])
    seen={seed_url:0}
    #num_urls=0
    D = Downloader(cache=cache, delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, timeout=timeout)

    def process_queue():
        while True:
            try:
                url = crawl_queue.pop()
                depth=seen[url]
            except IndexError:
                # crawl queue is empty
                break
            else:
                html = D(url)
                links=[]
                if scrape_callback:
                    try:
                        scrape_callback(url, html) 
                    except Exception as e:
                        print 'Error in callback for: {}: {}'.format(url, e)
                if depth!=max_depth:
                    if link_regex:
                        links.extend(link for link in get_links(html) if re.match(link_regex, link))
                    for link in links:
                        link = normalize(seed_url, link)
                        # check whether already crawled this link
                        if link not in seen:
                            seen[link]=depth+1
                            if same_domain(seed_url, link):
                                crawl_queue.append(link)
                                #seen.add(link)
                                # add this new link to queue
                            
            #num_urls+=1
            #if num_urls>max_urls:
                #break

    # wait for all download threads to finish
    threads = []
    while threads or crawl_queue:
        # the crawl is still active
        for thread in threads:
            if not thread.is_alive():
                # remove the stopped threads
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            # can start some more threads
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True) # set daemon so main thread can exit when receives ctrl-c
            thread.start()
            threads.append(thread)
        # all threads have been processed
        # sleep temporarily so CPU can focus execution on other threads
        time.sleep(SLEEP_TIME)


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link) # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)


def scrape_callback(url, html):
    if re.search('/view/', url):
        #tree = lxml.html.fromstring(html)
        #row = [tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content() for field in FIELDS]
        #row=[re.search('<tr id="places_{}__row">.*?<td class="w2p_fw">(.*?)</td>'.format(field), html).groups()[0]  for field in FIELDS]
        webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
        return webpage_regex.findall(html)

def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc

def get_links(html):
    """Return a list of links from html 
    """
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    return webpage_regex.findall(html)

if __name__ == '__main__':
    #link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, user_agent='BadCrawler')
    url='http://example.webscraping.com'
    #cache1=MongoCache()
    #(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, user_agent='wswp', proxies=None, num_retries=1, scrape_callback=None, cache=None):
    #link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, max_depth=-1, user_agent='GoodCrawler',cache=cache1)
    threaded_crawler(url, '/(index|view)',delay=0, cache=None, scrape_callback=None, user_agent='wswp', proxies=None, num_retries=1, max_threads=10, timeout=10)
    #result=cache1[url]
    #print  result