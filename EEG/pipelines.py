# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import datetime
import os

class EegPipeline(object):
    csv_writer = 0
    a36kr_writer = 0
    def __init__(self):
        rootDir = 'result/'
        data = datetime.datetime.now().strftime('%Y-%m-%d')
        out = open(os.path.join(rootDir,'{}.csv'.format(data)), 'a+', newline='', encoding='utf-8')
        self.csv_write = csv.writer(out, dialect='excel')
        out_36kr = open(os.path.join(rootDir,'{}.csv'.format(data+'-36kr')), 'a+', newline='', encoding='utf-8')
        self.a36kr_writer = csv.writer(out_36kr, dialect='excel')
        key_id_map = open(os.path.join(rootDir, 'key_id_map.csv'), 'a+', newline='', encoding='utf-8')
        self.key_id_map_writer = csv.writer(key_id_map, dialect='excel')


    def process_item(self, item, spider):
        if item['source'] == '36kr':
            self.a36kr_writer.writerow([item['title'].replace('\"', '').replace('\n', '').replace(',', '，'),
                                        item['date'].replace('\"', '').replace('\n', ' '),
                                        item['text'].replace('\"', '').replace('\n', '').replace(',', '，'),
                                        item['id']
                                        ]

                                       )
        else:
            self.csv_write.writerow([item['source'],
                                     item['title'].replace('\"', '').replace('\n','').replace(',','，'),
                                     item['date'].replace('\"', '').replace('\n',' '),
                                     item['text'].replace('\"', '').replace('\n','').replace(',','，'),
                                     item['id']]
                                    )

        self.key_id_map_writer.writerow([item['key'], item['id']])
        return item
