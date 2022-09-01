import scrapy
from bs4 import BeautifulSoup
import re
from platforms_scrapers.items import EventItem, EventLoader
from scrapy.http import Request
# from scrapy.loader import ItemLoader
import sqlite3

def read_data():
    con = sqlite3.connect('../server/events.db')
    cur = con.cursor()
    data = cur.execute("SELECT * FROM event WHERE last_time_scraped IS NULL").fetchall()
    return list(data)

def get_company_links(event_id):
    con = sqlite3.connect('../server/events.db')
    cur = con.cursor()
    data = cur.execute("SELECT company_link FROM event_company WHERE id_event=?",event_id).fetchall()
    return list(data)        

class A2zSpider(scrapy.Spider):
    name = 'a2z'
    # allowed_domains = ['a2zinc.net']
    links_data = read_data()

    custom_settings = {
        'ITEM_PIPELINES': {
            'platforms_scrapers.pipelines.PlatformsScrapersPipeline': 300,
        }
    }

    def start_requests(self):
        for url in self.links_data:
            print(url)
            yield Request(url[2], dont_filter=True, cb_kwargs={'event_id':url[0]})        

    def parse(self, response, event_id):
        print(event_id)
        soup = BeautifulSoup(response.text, 'lxml')
        links = [a['href'] for a in soup.find_all('a',{'class':'exhibitorName'})]
        print(links)
        for link in links:
            yield response.follow(link, callback=self.parse_profile, cb_kwargs={'event_id':event_id, 'slug': link})
    
    def parse_profile(self, response, event_id, slug):
        l = EventLoader(EventItem(), selector=response)

        soup = BeautifulSoup(response.text, 'lxml')
        name = soup.find('div', {'class':'panel-body'}).find('h1').text.strip()
        
        website_a = soup.find('div', {'class':'panel-body'}).find('a', {'id':'BoothContactUrl'})
        website = website_a.text.strip() if website_a else ''

        linkedin_a = soup.find('a',{'href': re.compile('linkedin\.')})
        linkedin = linkedin_a['href'] if linkedin_a else ''

        l.add_value('domain', website)
        l.add_value('name', name)
        l.add_value('linkedin', linkedin)
        l.add_value('event_id',event_id)
        l.add_value('event_company_link', slug)

        yield l.load_item()
