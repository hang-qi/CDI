# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import os
import codecs

class SaveHTMLPipeLine(object):
    def process_item(self, item, spider):
        filename = "yahoo/{0}/{1}".format(item['category'], item['filename'])
        self.ensure_dir(filename);
        f = open(filename, 'w')
        f.write(item['responseBody'])
        f.close()

        rawtext = "yahoo/{0}/{1}.rawtxt".format(item['category'], item['filename'])
        self.ensure_dir(rawtext);
        fw = codecs.open(rawtext, encoding='utf-8', mode='w')       
        fw.write(item['headline'])
        fw.write('\n')
        fw.write(item['source'])
        fw.write('\n')
        fw.write(item['date'])
        fw.write('\n')
        fw.write(item['content'])
        fw.close()

        return item

    def ensure_dir(self, f):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

import os
import time
import urlparse
import rfc822
import subprocess
from cStringIO import StringIO
from collections import defaultdict

from twisted.internet import defer, threads

from scrapy import log
from scrapy.utils.misc import md5sum
from scrapy.http import Request
from scrapy.exceptions import DropItem, NotConfigured, IgnoreRequest
from scrapy.contrib.pipeline.media import MediaPipeline

class NoImageDrop(DropItem):
    """Product with no image exception"""

class ImageException(Exception):
    """General image error exception"""

class FSImageStore(object):
    def __init__(self, basedir):
        if '://' in basedir:
            basedir = basedir.split('://', 1)[1]
        self.basedir = basedir
        self._mkdir(self.basedir)
        self.created_directories = defaultdict(set)

    def persist_image(self, key, buf, info):
        absolute_path = self._get_filesystem_path(key)
        self._mkdir(os.path.dirname(absolute_path), info)
        f = open(absolute_path, "wb")
        f.write(buf)
        f.close()

    def _get_filesystem_path(self, key):
        path_comps = key.split('/')
        return os.path.join(self.basedir, *path_comps)

    def _mkdir(self, dirname, domain=None):
        seen = self.created_directories[domain] if domain else set()
        if dirname not in seen:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            seen.add(dirname)

class DownloadPipeline(MediaPipeline):
    base_url = ''

    def __init__(self, store_uri, download_func=None):
        if not store_uri:
            raise NotConfigured
        self.store = FSImageStore(store_uri)
        super(DownloadPipeline, self).__init__(download_func=download_func)

    def ensure_dir(self, f):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

    @classmethod
    def from_settings(cls, settings):
        DownloadPipeline.base_url = settings['IMAGE_STORAGE']
        return cls(DownloadPipeline.base_url)

    def get_media_requests(self, item, info):
        url = item['imageSrc']
        if (url[0:4] == "http"):
            yield Request(url)

    def item_completed(self, results, item, info):
        url = item['imageSrc']
        if url == '':
            #raise DropItem("Item contains no image")
            return item
        
        # write caption to the .cap file
        urlParts = url.split('/')
        imageName = urlParts[-1]
        imagePath =  DownloadPipeline.base_url + imageName;
        dateStr = item['date'].replace(':', '')

        newImagePath = DownloadPipeline.base_url + dateStr + '_' + imageName;

        ext = '.' + imageName.split('.')[-1]
        captionName = DownloadPipeline.base_url + dateStr + '_' + imageName.replace(ext, '.cap');

        subprocess.call(['mv', imagePath, newImagePath])
        
        f = codecs.open(captionName, encoding='utf-8', mode='w')
        f.write("HTML file: ")
        f.write(item['filename'])
        f.write('\n')
        f.write("Category: ")
        f.write(item['category'])
        f.write('\n')
        f.write("Source: ")
        f.write(item['source'])
        f.write('\n')
        f.write("Date: ")
        f.write(item['date'])
        f.write('\n')
        f.write("Image Caption: ")
        f.write(item['imageCaption'])
        f.close()
        return item

    def inc_stats(self, spider, status):
        spider.crawler.stats.inc_value('image_count', spider=spider)
        spider.crawler.stats.inc_value('image_status_count/%s' % status, spider=spider)

    def image_downloaded(self, response, request, info):
        for key, buf in self.get_image(response, request, info):
            self.store.persist_image(key, buf, info)
        return

    def get_image(self, response, request, info):
        key = self.image_key(request.url)
        buf = response.body
        yield key, buf

    def media_downloaded(self, response, request, info):
        referer = request.headers.get('Referer')

        if response.status != 200:
            log.msg(format='Image (code: %(status)s): Error downloading image from %(request)s referred in <%(referer)s>',
                    level=log.WARNING, spider=info.spider,
                    status=response.status, request=request, referer=referer)
            raise ImageException('download-error')

        if not response.body:
            log.msg(format='Image (empty-content): Empty image from %(request)s referred in <%(referer)s>: no-content',
                    level=log.WARNING, spider=info.spider,
                    request=request, referer=referer)
            raise ImageException('empty-content')

        status = 'cached' if 'cached' in response.flags else 'downloaded'
        log.msg(format='Image (%(status)s): Downloaded image from %(request)s referred in <%(referer)s>',
                level=log.DEBUG, spider=info.spider,
                status=status, request=request, referer=referer)
        self.inc_stats(info.spider, status)

        try:
            key = self.image_key(request.url)
            self.image_downloaded(response, request, info);
        except ImageException as exc:
            whyfmt = 'Image (error): Error processing image from %(request)s referred in <%(referer)s>: %(errormsg)s'
            log.msg(format=whyfmt, level=log.WARNING, spider=info.spider,
                    request=request, referer=referer, errormsg=str(exc))
            raise
        except Exception as exc:
            whyfmt = 'Image (unknown-error): Error processing image from %(request)s referred in <%(referer)s>'
            log.err(None, whyfmt % {'request': request, 'referer': referer}, spider=info.spider)
            raise ImageException(str(exc))

        return {'url': request.url, 'path': key}

    def image_key(self, url):
        return url.split('/')[-1]