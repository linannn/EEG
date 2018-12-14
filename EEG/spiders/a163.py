# -*- coding: utf-8 -*-
import scrapy
import json
from EEG.items import EegItem
import bloomfilter

class A163Spider(scrapy.Spider):
    name = '163'
    allowed_domains = ['163.com']
    start_urls = ['https://3g.163.com/touch/reconstruct/article/list/BA8D4A3Rwangning/0-10.html']
    key_words_list = None
    page_size = 10
    current_id = 0
    bloom = 0
    conflict_count = 5
    conflict_max = 5
    def __init__(self, bloom=bloomfilter.Bloomfilter(100000, 10), keyword={'百度', '阿里巴巴', '腾讯'}):
        self.bloom = bloom
        self.key_words_list = keyword
    def parse(self, response):
        json_data = json.loads(response.body.decode('utf-8')[9:-1])
        for item in json_data['BA8D4A3Rwangning']:
            for key in self.key_words_list:
                if key in item['title'] and 'skipType' not in item:
                    flag = item['title']
                    if self.bloom.test(flag):
                        self.conflict_count -= 1
                        print(flag)
                        if self.conflict_count <= 0:
                            print(self.name + ' stop')
                            return
                        break
                    if item['url'] == '':
                        break
                    self.bloom.add(flag)
                    self.conflict_count = self.conflict_max
                    try:
                        yield scrapy.Request(
                            url=item['url'],
                            callback=self.parse_detail,
                            dont_filter=True
                        )
                    except:
                        pass
                    break

        self.current_id += self.page_size
        next_url = 'https://3g.163.com/touch/reconstruct/article/list/BA8D4A3Rwangning/'+\
                   str(self.current_id)+'-10.html'
        print(next_url)
        yield scrapy.Request(next_url, callback=self.parse)


    def parse_detail(self, response):
        newsTextSelector = response.xpath('//div[@class="page js-page on"]/p')
        newsTitle = response.xpath('//h1[@class="title"]/text()').extract()[0]
        newsDate = response.xpath('//span[@class="time js-time"]/text()').extract()[0]
        item = EegItem();
        item['title'] = newsTitle
        item['date'] = newsDate
        item['source'] = '163'
        newsText = ''
        for subText in newsTextSelector:
            newsText = newsText + subText.xpath('string(.)').extract()[0] + '\n'
        item['text'] = newsText
        yield item


