from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerRunner
from scrapy.utils.conf import arglist_to_dict
from EEG.Info import SpiderInfo

class Command(ScrapyCommand):
    requires_project = True

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",
                          help="set spider argument (may be repeated)")
        parser.add_option("-o", "--output", metavar="FILE",
                          help="dump scraped items into FILE (use - for stdout)")
        parser.add_option("-t", "--output-format", metavar="FORMAT",
                          help="format to use for dumping items with -o")
        parser.add_option("-k", "--keyword",metavar="KEYWORD",
                          help="format to use for dumping items with -o")

    def process_options(self, args, opts):
        ScrapyCommand.process_options(self, args, opts)
        try:
            opts.spargs = arglist_to_dict(opts.spargs)
        except ValueError:
            # raise UsageError("Invalid -a value, use -a NAME=VALUE", print_help=False)
            pass

    def run(self, args, opts):
        # settings = get_project_settings()
        print("crawl begin")
        info = SpiderInfo()
        keyword = set()
        bloom_dict = info.bloom_dict
        if opts.keyword == '1':
            keyword = info.keyword_new - info.keyword_old
        elif opts.keyword == '0':
            keyword = info.keyword_old
            info.set_keyword_old()
        print(keyword)
        spider_loader = self.crawler_process.spider_loader
        for spidername in args or spider_loader.list():
            print("\n*********cralall spidername************" + spidername)
            if len(keyword) !=0:
                self.crawler_process.crawl(spidername, bloom_dict[spidername], keyword)
        self.crawler_process.start()
        info.set_bloom()