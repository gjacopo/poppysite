#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sat Feb 17 00:39:38 2018

@author: gjacopo
"""


# Models for UNESCO scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import os, sys, re#analysis:ignore

import scrapy 
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, MapCompose, Join, TakeFirst, Identity
# from scrapy.item import DictItem, Field

from warnings import warn#analysis:ignore
from collections import defaultdict

import time

try:
    from datetime import datetime
except (ModuleNotFoundError,ImportError):
    def _now():
        return time.asctime()
else:
    def _now():
        return datetime.now.isoformat()

try:
    from datefinder import find_dates as _find_dates
except (ModuleNotFoundError,ImportError):
    def _find_dates(arg): 
        return arg

try:
    from unicode import strip as _strip
except (ModuleNotFoundError,ImportError):
    def _strip(arg): 
        try:    return arg.strip(' \r\t\n')
        except: return arg

try:
    from scrapy.utils.markup import remove_tags as _remove_tags
except ImportError:
    try:
        from w3lib.html import remove_tags as _remove_tags
    except (ModuleNotFoundError,ImportError):
        def _remove_tags(arg): 
            start = arg.find('<')
            while start != -1:
                end = arg.find('>')
                arg = _strip(arg[:start]) + ' ' + _strip(arg[end + 1:])
                start = arg.find('<')
            return arg

from . import settings


#==============================================================================
# GLOBAL VARIABLES
#==============================================================================

SITES_FIELDS        = ['Country', 'List', 'Link', 'Name']

try:
    assert COUNTRY_SELECTOR
    assert not COUNTRY_SELECTOR in (None,'')
except (NameError,AssertionError):
    COUNTRY_SELECTOR = '//a[starts-with(@href,"/{lang}/statesparties")]/ancestor::h4'.format(lang=settings.LANG)
    
try:
    assert SITES_PATH
    assert not (SITES_PATH in (None,{}) or all([v in ([],'',None) for v in SITES_PATH.values()]))
except (NameError,AssertionError):
    SITES_PATH      = dict.fromkeys(SITES_FIELDS)
    SITES_PATH['Country'] = '/a[starts-with(@href,"/{lang}/statesparties")]'.format(lang=settings.LANG)
    SITES_PATH['List']  = 'following-sibling::div[1]/ul/li'
    SITES_PATH['Link']  = 'following-sibling::div[1]/ul/li/a[1]/@href'
    SITES_PATH['Name']  = 'following-sibling::div[1]/ul/li/a[1]/text()'

#==============================================================================
# ITEM CLASSES
#==============================================================================

class WhscrapeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
