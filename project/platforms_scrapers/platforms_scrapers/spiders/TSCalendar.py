import scrapy
from bs4 import BeautifulSoup
import re
import math
from daterangeparser import parse

class TscalendarSpider(scrapy.Spider):
    name = 'TSCalendar'
    allowed_domains = ['thetradeshowcalendar.com']
    start_urls = ['https://thetradeshowcalendar.com/iaee_v2/index.php?&vShow=search&vCtry=United+States&vPos=0']

    custom_settings = {
        'ITEM_PIPELINES': {
            'platforms_scrapers.pipelines.ExternalSourcesPipeline': 300,
        }
    }

    def parse(self, response):

        soup = BeautifulSoup(response.text, 'lxml')

        table = soup.find('table', {'id':'show-table'})
        rows = table.find_all('tr')[1:]

        match = re.search(r'now showing .* out of (?P<total_events>\d+) exhibitions', response.text)

        if match:
           total_events = int(match.group('total_events'))
           pages = math.ceil(total_events/50)
           for page in range(1, pages+1):
                offset = page*50
                next_page_link = re.sub(r'vPos=\d+', f'vPos={offset}', response.request.url)
                yield scrapy.Request(url=next_page_link, callback= self.parse)

        for row in rows:
            raw_date_td = row.find('td', attrs={'class':'r-Dates'})
            
            if raw_date_td:
                raw_date = raw_date_td.text.replace('/',' ').strip()
                start, end = parse(raw_date)
                name = row.find('td', attrs={'class':'r-Name'}).text.strip()
                link = row.find('a')['href']
                platform = False
                source = 'TSCALENDAR'

                yield {
                    'name': name,
                    'link': link,
                    'start_date': start,
                    'end_date': end,
                    'platform': platform,
                    'source': source
                }
