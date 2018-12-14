import os
import sys
import inspect
import bloomfilter


class SpiderInfo():
    spiders = set()
    spiders_name_new = set()
    spiders_name_old = set()
    keyword_new = set()
    keyword_old = set()
    bloom_dict = {}

    def __init__(self):
        self.get_spiders()
        self.get_keyword()
        self.get_old()
        self.get_bloom()

    def get_spiders(self):
        spiders = set()
        spiders_name = set()
        path = os.path.abspath('.')
        exploit = os.path.join(path, 'EEG/spiders')
        sys.path.append(exploit)
        spider_path = [x for x in os.listdir(exploit) if os.path.isfile(os.path.join(exploit, x))]
        for spider in spider_path:
            if spider != '__init__.py':
                module = __import__(os.path.splitext(spider)[0])
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and name != 'EegItem':
                    # if inspect.isclass(obj) and name == 'thepaper':
                        # process.crawl(obj)
                        spiders.add(obj)
                        spiders_name.add(name)
        self.spiders = spiders
        self.spiders_name_new = spiders_name

    def get_keyword(self):
        if not os.path.exists('property'):
            os.makedirs('property')
        with open('property/keyword', 'r', encoding='utf-8') as f:
            keyword_new = f.read().split('\n')
            for i in  keyword_new:
                if i != '':
                    self.keyword_new.add(i)
        # self.keyword_new = {"京东", "美团", "阿里巴巴", "淘宝", "谷歌", "微软", "特斯拉", "SpaceX", "马斯克"}

    def get_old(self):
        try:
            with open('property/spiders_old_name', 'r+', encoding='utf-8') as f:
                spider_old = f.read().split('\n')
                for i in spider_old:
                    if i != '':
                        self.spiders_name_old.add(i)
        except:
            pass
        with open('property/spiders_old_name', 'w', encoding='utf-8') as f:
            for i in self.spiders_name_new:
                f.write(i+'\n')
        try:
            with open('property/keyword_old', 'r+', encoding='utf-8') as f:
                keyword_old = f.read().split('\n')
                for i in keyword_old:
                    if i != '':
                        self.keyword_old.add(i)
        except:
            pass

    def set_keyword_old(self):
        with open('property/keyword_old', 'w', encoding='utf-8') as f:
            for i in self.keyword_new:
                f.write(i+'\n')

    def get_bloom(self):
        for spider in self.spiders:
            try:
                self.bloom_dict[spider.name] = bloomfilter.Bloomfilter('property/{}.bloom'.format(spider.name))
            except:
                self.bloom_dict[spider.name] = bloomfilter.Bloomfilter(100000, 10)

    def set_bloom(self):
        for key, value in self.bloom_dict.items():
            value.save('property/{}.bloom'.format(key))