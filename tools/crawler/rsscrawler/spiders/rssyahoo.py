#rssbase.py
from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import XmlXPathSelector
from scrapy.selector import HtmlXPathSelector
from scrapy.exceptions import CloseSpider
from scrapy import log

import json
import os
from rsscrawler.items import StoryItem 
from bs4 import BeautifulSoup

class MySpider(BaseSpider):
    name = 'rssyahoo'

    # References:
    # Yahoo RSS list: http://news.yahoo.com/sitemap/
    # GoogleReaderAPI: http://code.google.com/p/pyrfeed/wiki/GoogleReaderAPI
    # JSON Visualization Tool: http://chris.photobooks.com/json/default.htm

    allowed_domains = ['google.com', 'yahoo.com']
    
    #start_urls = ['http://www.google.com/reader/api/0/stream/contents/feed/http://news.yahoo.com/rss/elections-2012?n=100']
    #base_url = 'http://www.google.com/reader/api/0/stream/contents/feed/http://news.yahoo.com/rss/elections-2012?n=100'
    start_urls = []
    base_url = ''
    category = ''

    story_count = 0;
    image_count = 0;
    total_needed = 10000;

    def __init__(self, category=None):

        if category == None:
            category = 'politics'
        self.category = category
        self.base_url = 'http://www.google.com/reader/api/0/stream/contents/feed/http://news.yahoo.com/rss/%s?n=100' % category
        self.start_urls = [self.base_url]

        #self.settings['LOG_FILE'] = 'yahoo_%s.log' % category
        #self.settings['IMAGE_STORAGE'] = 'yahoo/%s-images/' % category


    def parse(self, response):
        rsscontent = json.loads(response.body);
        continuationCode = rsscontent['continuation'];
        self.log('Next page code: ' + continuationCode, level=log.INFO)
        nextFeedPageUrl = self.base_url + '&c=' + continuationCode; 
        items = rsscontent['items']
        storyLinks = []
        for item in items:
            try:
                link = item['alternate'][0]['href']
                if link[0:1] == '/':
                    link = 'http://news.yahoo.com' + link;
                elif link[0:8] == 'http:///':
                    link = link.replace('http:///', 'http://news.yahoo.com/')
                storyLinks.append(link)
            except:
                continue
        
        storyRequests = [Request(x, callback=self.parseStory) for x in storyLinks]
        nextpageRequest = Request(nextFeedPageUrl)
        storyRequests.append(nextpageRequest)
        return storyRequests

    def parseStory(self, response):
        self.story_count +=1
        self.log('Saving item #' + str(self.story_count), level=log.INFO)
        #if self.story_count == self.total_needed:
        #    raise CloseSpider(reason='We have collected enough data.')

        hxs = HtmlXPathSelector(response)
        imageSrc = hxs.select('//div[@class=\'yom-art-lead-img\']/img/@src').extract();
        imageCaption = hxs.select('//div[@class=\'yom-art-lead-img\']/img/@alt').extract();

        if len(imageSrc) == 0:
            imageSrc = hxs.select('//span[@class=\'yom-figure yom-fig-right\']/img/@src').extract();
            imageCaption = hxs.select('//span[@class=\'yom-figure yom-fig-right\']/img/@title').extract();

        if len(imageSrc) == 0:
            imageSrc = hxs.select('//span[@class=\'yom-figure yom-fig-left\']/img/@src').extract();
            imageCaption = hxs.select('//span[@class=\'yom-figure yom-fig-left\']/img/@title').extract();


        source = hxs.select('//div[@class=\'bd\']/cite/span[@class=\'provider org\']').extract();
        date = hxs.select('//div[@class=\'bd\']/cite/abbr/@title').extract();
        headline = hxs.select('//h1[@class=\'headline\']').extract();
        content = hxs.select('//div[@class=\'yom-mod yom-art-content \']').extract();

        url = response.url
        urlParts = url.split('/')

        item = StoryItem()
        item['url'] = url
        item['category'] = self.category
        item['filename'] = urlParts[-1]
        item['responseBody'] = response.body

        soupContent = BeautifulSoup(content[0])
        item['content'] = soupContent.get_text()

        soupHeadline = BeautifulSoup(headline[0])
        item['headline'] = soupHeadline.get_text()

        if (len(imageSrc) > 0):
            self.image_count += 1;
            self.log('Image #' + str(self.image_count), level=log.INFO)
            item['imageSrc'] = imageSrc[0]
        else:
            item['imageSrc'] = ''

        if (len(imageCaption) > 0):
            item['imageCaption'] = imageCaption[0]
        else:
            item['imageCaption'] = ''

        if (len(source) > 0):
            soup = BeautifulSoup(source[0])
            item['source'] = soup.get_text()
        else:
            item['source'] = 'N/A'

        if (len(date) > 0):
            item['date'] = date[0]
        else:
            item['date'] = ''

        return item