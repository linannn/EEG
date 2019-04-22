# -*- coding: utf-8 -*-
import scrapy
import json
from EEG.items import EegItem
from bloomfilter import bloomfilter
import logging

class A36krSpider(scrapy.Spider):
    name = '36kr'
    allowed_domains = ['36kr.com']
    start_urls = ["https://36kr.com/api/newsflash?b_id=0&per_page=50&_=1540362138360"]
    base_url = "https://36kr.com/api//search/entity-search?page={}&per_page=50&keyword={}&entity_type=newsflash";
    key_words_list = None
    bloom = 0
    page_size = 50
    conflict_count = 5
    confilt_max = 5
    def __init__(self, bloom=bloomfilter.Bloomfilter(100000, 10), keyword={'百度', '阿里巴巴', '腾讯'}):
        self.bloom = bloom
        self.key_words_list = keyword

    def start_requests(self):
        for key in self.key_words_list:
            url = self.base_url.format(1, key)
            yield scrapy.Request(
                url=url,
                meta={'page':1, 'key':key},
                callback=self.parse,
                dont_filter=True
            )

    def parse(self, response):
        key = response.meta['key']
        page = response.meta['page']
        json_data = json.loads(response.body.decode('utf-8'))
        for item in json_data['data']['items']:
            for key in self.key_words_list:
                if key in item['title']:
                    flag =  item['title']
                    if self.bloom.test(flag+key):
                        self.conflict_count -= 1
                        logging.info(flag+'conflict')
                        if self.conflict_count <= 0:
                            logging.info(self.name+'stop')
                            return
                    else:
                        if self.blom.test(flag):
                            pass
                        else:
                            eegItem = EegItem()
                            eegItem['source'] = '36kr'
                            eegItem['title'] = item['title'].replace('\t', ' ')
                            eegItem['date'] = item['published_at'].replace('\t', ' ')
                            eegItem['text'] = item['description'].replace('\t', ' ')
                            eegItem['id'] = item['id']
                            eegItem['key'] = key
                            self.bloom.add(flag)
                            self.bloom.add(flag+key)
                            self.conflict_count = self.confilt_max
                            yield eegItem

        # new_last_id = json_data['data']['items'][-1]['id']
        next_url = self.base_url.format(page+1, key)
        # next_url = 'https://36kr.com/api/newsflash?b_id=' + str(new_last_id) + \
        #     '&per_page=' + str(self.page_size) + '&_=' + str(int(round(time.time() * 1000)))
        # print(next_url)
        logging.info('next: '+next_url)
        yield scrapy.Request(next_url, callback=self.parse)
