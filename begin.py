import os
import time
while True:
    os.system("scrapy crawlall -k 1")
    os.system("scrapy crawlall -k 0")
    print('crawl finish')
    time.sleep(86400)
# cmdline.execute("scrapy crawlall -k 0".split())
# cmdline.execute("Sscrapy crawlall -k 1".split())
#
