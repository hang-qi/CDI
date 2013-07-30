# Scrapy settings for rsscrawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'rsscrawler'

SPIDER_MODULES = ['rsscrawler.spiders']
NEWSPIDER_MODULE = 'rsscrawler.spiders'

# Pipelines
ITEM_PIPELINES=['rsscrawler.pipelines.SaveHTMLPipeLine',
                'rsscrawler.pipelines.DownloadPipeline']

# Agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17'
#DOWNLOAD_DELAY = 0.5

# Logs
LOG_LEVEL = 'INFO'
LOG_STDOUT = True
LOG_FILE = 'rsscrawler_yahoo_world.log'

# Image storage
IMAGE_STORAGE = 'yahoo/world-images/'