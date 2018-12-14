# -*- coding: utf-8 -*-
import scrapy
import json
import time
from EEG.items import EegItem
from bloomfilter import bloomfilter

class A36krSpider(scrapy.Spider):
    name = '36kr'
    allowed_domains = ['36kr.com']
    start_urls = ["https://36kr.com/api/newsflash?b_id=0&per_page=50&_=1540362138360"]
    key_words_list = None
    bloom = 0
    page_size = 50
    conflict_count = 5
    confilt_max = 5
    def __init__(self, bloom=bloomfilter.Bloomfilter(100000, 10), keyword={'百度', '阿里巴巴', '腾讯'}):
        self.bloom = bloom
        self.key_words_list = keyword

    def parse(self, response):
        json_data = json.loads(response.body.decode('utf-8'))
        for item in json_data['data']['items']:
            for key in self.key_words_list:
                if key in item['title']:
                    flag =  item['title']
                    if self.bloom.test(flag):
                        self.conflict_count -= 1
                        print(flag)
                        if self.conflict_count <= 0:
                            print(self.name + ' stop')
                            return
                        break
                    eegItem = EegItem()
                    eegItem['source'] = '36kr'
                    eegItem['title'] = item['title'].replace('\t', ' ')
                    eegItem['date'] = item['published_at'].replace('\t', ' ')
                    eegItem['text'] = item['description'].replace('\t', ' ')
                    self.bloom.add(flag)
                    self.conflict_count = self.confilt_max
                    yield eegItem
                    break

        new_last_id = json_data['data']['items'][-1]['id']
        next_url = 'https://36kr.com/api/newsflash?b_id=' + str(new_last_id) + \
            '&per_page=' + str(self.page_size) + '&_=' + str(int(round(time.time() * 1000)))
        print(next_url)
        yield scrapy.Request(next_url, callback=self.parse)
