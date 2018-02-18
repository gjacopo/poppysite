#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 02:11:52 2018

@author: gjacopo
"""

from urllib.parse import urlparse

import scrapy
from scrapy import signals
from .. import settings

class WHSSpider(scrapy.Spider):
    name            = 'WorldHeritageSite'
    domain          = settings.UNESCO_URL
    # set the HTTP error codes that should be handled
    handle_httpstatus_list = [404]
    valid_url, invalid_url = [], []
    # set the maximum depth (used as a "safety" parameter)
    maxdepth        = 1

    def __init__(self, url=None, *args, **kwargs):
        super(WHSSpider, self).__init__(*args, **kwargs)
        if url in (None,''):
            url = settings.WH_URL
        if not isinstance(url,list):
            url = [url]
        self.start_urls = url

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(WHSSpider, cls).from_crawler(crawler, *args, **kwargs)
        # register the spider_closed handler on spider_closed signal
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def parse_sitelist(self, response):
        """Main method that parse downloaded pages. 
        """
        # set defaults for the first page that won't have any meta information
        from_url, from_country = '', ''
        sites = []
        depth = 0
        # extract the meta information from the response, if any
        if 'from' in response.meta:     from_url = response.meta['from']
        if 'country' in response.meta:  from_country = response.meta['country']
        if 'sites' in response.meta:    sites = response.meta['sites']
        if 'depth' in response.meta:    depth = response.meta['depth']
        # if first response, update domain (to manage redirect cases)
        if len(self.domain) == 0:
            parsed_uri = urlparse(response.url)
            self.domain = parsed_uri.netloc
        # 404 error, populate the broken links array
        if response.status == 404:
            self.invalid_url.append({'url': response.url,
                                     'from': from_url,
                                     'country': from_country,
                                     'sites': sites})
        else:
            # populate the working links array
            self.valid_url.append({'url': response.url,
                                   'from': from_url,
                                   'country': from_country,
                                   'sites': sites})
            # extract domain of current page
            parsed_uri = urlparse(response.url)
            # parse new links only:
            #   - if current page is not an extra domain
            #   - and depth is below maximum depth
            if parsed_uri.netloc == self.domain and depth < self.maxdepth:
                # get all the <h4 ... "statesparties"> tags
                a_selectors = response.xpath(settings.COUNTRY_SELECTOR)
                # loop on each tag
                for selector in a_selectors:
                    # extract the country reference
                    country = selector.xpath(settings.SITES_PATH['Country']).extract()
                    # extract the name of the site
                    name = selector.xpath(settings.SITES_PATH['Name']).extract()
                    # also retrieve the list of all other sites in the country
                    sites = selector.xpath(settings.SITES_PATH['List']).extract()
                    # finally extract the links href
                    link = selector.xpath(settings.SITES_PATH['Link']).extract()
                    # create a new Request object
                    if depth < self.maxdepth-1:
                        request = response.follow(link, callback=self.parse_sitelist)
                    else:
                        request = response.follow(link, callback=self.parse_site)     
                    # meta information: URL of the current page                        
                    request.meta['from'] = response.url;
                    # meta information: country where the site is located                      
                    request.meta['country'] = country
                    # meta information: name of the site                        
                    request.meta['name'] = name;
                    # meta information: list of all other sites in the same country                       
                    request.meta['sites'] = sites;
                    # meta information: depth of the link
                    request.meta['depth'] = depth + 1
                    # return it thanks to a generator
                    yield request

    def spider_closed(self):
        """Special handler for spider_closed signal.
        """
        print('----------')
        print('There are', len(self.valid_url), 'working links and',
              len(self.invalid_url), 'broken links.', sep=' ')
        if len(self.invalid_url) > 0:
            print('Broken links are:')
            for invalid in self.invalid_url:
                print(invalid)
        print('----------')

