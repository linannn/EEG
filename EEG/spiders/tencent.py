# -*- coding: utf-8 -*-
import scrapy
import json
import bloomfilter
from EEG.items import EegItem

class TencentSpider(scrapy.Spider):
    name = 'tencent'
    allowed_domains = ['new.qq.com']
    start_urls = ['https://pacaio.match.qq.com/irs/rcd?cid=58&token=c232b098ee7611faeffc46409e836360&ext=tech&page=0']
    key_words_list = None
    current_page = 0
    bloom = 0
    conflict_num = 5
    conflict_max = 5
    def __init__(self, bloom=bloomfilter.Bloomfilter(100000, 10), keyword={'百度', '阿里巴巴', '腾讯'}):
        self.bloom = bloom
        self.key_words_list = keyword

    def parse(self, response):
        json_data = json.loads(response.body.decode('utf-8'))
        for item in json_data['data']:
            for key in self.key_words_list:
                if key in item['title']:
                    flag = item['title']
                    if self.bloom.test(flag):
                        self.conflict_num -= 1
                        print(flag)
                        if self.conflict_num <= 0:
                            print(self.name + ' stop')
                            return
                        break
                    if item['url'] == '':
                        break
                    self.bloom.add(flag)
                    self.conflict_num = self.conflict_max
                    eeg = EegItem()
                    eeg['date'] = item['publish_time']
                    yield scrapy.Request(
                        url=item['vurl'],
                        meta={'item': eeg},
                        callback=self.parse_detail,
                        dont_filter=True
                    )
                    break

            self.current_page += 1
            next_url = 'https://pacaio.match.qq.com/irs/rcd?cid=58&token=c232b098ee7611faeffc46409e836360&ext=tech&page='\
                        + str(self.current_page)
            print(next_url)
            yield scrapy.Request(next_url, callback=self.parse)


    def parse_detail(self, response):
        title = response.xpath('//h1/text()').extract()[0]
        textSelector = response.xpath('//div[@class="content-article"]/p')
        text = ''
        for subText in textSelector:
            text = text + subText.xpath('string(.)').extract()[0] + '\n'
        item = response.meta['item']
        item['title'] = title
        item['text'] = text
        item['source'] = 'tencent'
        item['source'] = 'tencent'
        yield item
