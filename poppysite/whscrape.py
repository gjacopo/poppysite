#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 02:26:36 2018

@author: gjacopo
"""

import os
import multiprocessing
from multiprocessing import Pool


def _crawl(spider_name=None):
    if spider_name:
        os.system('scrapy crawl %s' % spider_name)
    return None

def run_crawler():

    spider_names = ['spider1', 'spider2', 'spider2']

    pool = Pool(processes=len(spider_names))
    pool.map(_crawl, spider_names)