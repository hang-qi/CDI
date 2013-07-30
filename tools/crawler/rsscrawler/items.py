# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class StoryItem(Item):
    # define the fields for your item here like:
    url = Field()
    category = Field()
    filename = Field()
    responseBody = Field()
    headline = Field()
    content = Field()
    imageSrc = Field()
    imageCaption = Field()
    source = Field()
    date = Field()    
    pass
