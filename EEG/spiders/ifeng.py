# -*- coding: utf-8 -*-
import scrapy
import json
import bloomfilter
from EEG.items import EegItem

class IfengSpider(scrapy.Spider):
    name = 'ifeng'
    allowed_domains = ['tech.ifeng.com']
    start_urls = ['http://tech.ifeng.com/listpage/800/0/1/rtlist.shtml']
    key_words_list = None
    current_page = 0
    bloom = 0
    conflict_count = 5
    conflict_max = 5

    def __init__(self, bloom=bloomfilter.Bloomfilter(100000, 10), keyword={'百度', '阿里巴巴', '腾讯'}):
        self.bloom = bloom
        self.key_words_list = keyword
    def parse(self, response):
        news_selector = response.xpath('//div[@class="zheng_list pl10 box"]')
        for news in news_selector:
            tmp = news.xpath('./h1/a | h2/a')
            flag = tmp.xpath('@href').extract()[0]
            title = tmp.xpath('text()').extract()[0]
            for key in self.key_words_list:
                if key in title:
                    if self.bloom.test(flag):
                        self.conflict_count -= 1
                        print(flag)
                        if self.conflict_count <= 0:
                            print(self.name + ' stop')
                            return
                        break
                    self.bloom.add(flag)
                    self.conflict_count = self.conflict_max
                    yield scrapy.Request(
                        url=flag,
                        callback=self.parse_detail,
                        dont_filter=True
                    )
        next_url = response.xpath('//a[@style="cursor:pointer;"]/@href').extract()[0]
        print(next_url)
        yield scrapy.Request(next_url, callback=self.parse)


    def parse_detail(self, response):
        title = response.xpath('//h1[@id="artical_topic"]/text()').extract()[0]
        date = response.xpath('//span[@class="ss01"]/text()').extract()[0]
        text_selector = response.xpath('//div[@id="main_content"]/p')
        text = ''
        for subText in text_selector:
            try:
                text += subText.xpath('./text()').extract()[0] + '\n'
            except:
                pass
        item = EegItem()
        item['date'] = date
        item['title'] = title
        item['text'] = text
        item['source'] = 'ifeng'
        yield item
