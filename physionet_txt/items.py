# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import json


class PhysionetTxtItem(scrapy.Item):
    """
    This is the item that will be passed to the pipeline for processing.
    """

    url = scrapy.Field()
    subject = scrapy.Field()
    study = scrapy.Field()
    filename = scrapy.Field()
    text = scrapy.Field()

    def __repr__(self):
        q = {
            'url': self['url'],
            'subject': self['subject'],
            'study': self['study'],
            'filename': self['filename'],
            'text': f"{len(self['text'])} chars"
        }
        return json.dumps(q)
