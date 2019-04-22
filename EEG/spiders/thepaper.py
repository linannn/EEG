# -*- coding: utf-8 -*-
import scrapy
from EEG.items import EegItem
import logging
from bloomfilter import bloomfilter

class ThepaperSpider(scrapy.Spider):
    name = 'thepaper'
    allowed_domains = ['thepaper.cn']
    start_urls = ['http://thepaper.cn/']

    key_word_list = {"ofo"}

    base_url2 = 'https://www.thepaper.cn/load_search.jsp?k={}&pagesize=20&searchPre=contentName_0:&orderType=1&pageidx={}'
    base_url = 'https://m.thepaper.cn/load_newsearch.jsp?k={}&f=all_0:&pageidx={}&type=1&_={}'

    conflict_count = 5
    confilt_max = 5

    def __init__(self, bloom=bloomfilter.Bloomfilter(100000, 10), keyword={'万科'}):
        self.bloom = bloom
        self.key_word_list = keyword
    # def __init__(self):
    #     self.bloom = bloomfilter.Bloomfilter(100000, 10)

    def start_requests(self):
        for key in self.key_word_list:
            url = self.base_url2.format(key, 1)
            # url = self.base_url.format(key, 1, int(round(time.time() * 1000)))
            yield scrapy.Request(
                url=url,
                meta={'page': 1,'key':key},
                callback=self.parse,
                dont_filter=True
            )


    def parse(self, response):
        key = response.meta['key']
        href_list = response.xpath('//h2/a')
        for href in href_list:
            id = href.xpath('./@href').extract()[0]
            url = 'https://www.thepaper.cn/' + href.xpath('./@href').extract()[0]
            if self.bloom.test(url+key):
                self.conflict_count -=1
                logging.info(url)
                if self.conflict_count <= 0:
                    logging(self.name+' ' + key+ ' stop')
                    return
            else:
                if self.bloom.test(url):
                    pass
                else:
                    self.bloom.add(url)
                    self.bloom.add(url+key)
                    self.conflict_count = self.confilt_max
                    yield scrapy.Request(
                        url=url,
                        meta={'id': id, 'key':key},
                        callback=self.parse_detail,
                        dont_filter=True
                    )
        page = response.meta['page']
        # if page > 50:
        #     return
        logging(str(page) + key)
        yield scrapy.Request(
            url = self.base_url2.format(key, page+1),
            meta={'page':page+1,'key':key},
            callback=self.parse,
            dont_filter=True
        )

    def parse_detail(self, response):
        try:
            title = response.xpath('//h1[@class="news_title"]/text()').extract()[0]
        except:
            return
        date = response.xpath('//div[@class="news_about"]/p')[1].xpath('string(.)').extract()[0]
        date = date.replace('\t', '').replace('\n', '')[:16]
        text = ''
        text = response.xpath('//div[@class="news_txt"]').xpath('string(.)').extract()[0]
        eeg = EegItem()
        eeg['title'] = title
        eeg['date'] = date
        eeg['text'] = text
        eeg['source'] = 'thepaper'
        eeg['id'] = response.meta['id']
        eeg['key'] = response.meta['key']

        yield eeg

