# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from email.policy import default
import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join, Compose
import re

def get_domain(link):
    link = link.lower()
    link = re.sub('https?://','', link)
    link = re.sub('www\.','', link)
    link = link.split('/')[0]
    return link


class EventLoader(ItemLoader):
    default_output_processor = TakeFirst()

    name_in = MapCompose(str.title)
    domain_in = MapCompose(get_domain)
    linkedin_out = Compose(lambda x: None if x[0] == '' else x[0])

class EventItem(scrapy.Item):
    # define the fields for your item here like:
    domain = scrapy.Field()
    name = scrapy.Field()
    linkedin = scrapy.Field()
    event_id = scrapy.Field()
    event_company_link = scrapy.Field()