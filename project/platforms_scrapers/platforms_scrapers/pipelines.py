# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
from datetime import datetime

class ExternalSourcesPipeline:
    def __init__(self):
        self.con = sqlite3.connect("../server/events.db")
        self.cur = self.con.cursor()
        self.create_table()
    
    def create_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS event (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    exhibitors_link TEXT UNIQUE,
                    link TEXT,
                    start_date DATE,
                    end_date DATE,
                    sector TEXT,
                    host TEXT,
                    source TEXT,
                    in_grata BOOLEAN,
                    platform BOOLEAN,
                    grata_uid TEXT UNIQUE,
                    last_time_scraped TIMESTAMP,
                    created_at TIMESTAMP)
                    """)
    def process_item(self, item, spider):

        now = datetime.now()

        # Inserts into events table
        self.cur.execute("""INSERT OR IGNORE INTO event(name, link, start_date, end_date, platform, source, created_at) VALUES (?,?,?,?,?,?,?)""", 
        (item['name'], item['link'], item['start_date'], item['end_date'], item['platform'], item['source'], now))


        self.con.commit()

        return item
  

class PlatformsScrapersPipeline:
    def __init__(self):
        self.con = sqlite3.connect("../server/events.db")
        self.cur = self.con.cursor()
        self.create_table()
    
    def create_table(self):

        self.cur.execute("""CREATE TABLE IF NOT EXISTS company (
            id INTEGER PRIMARY KEY,
            domain text UNIQUE,
            linkedin TEXT
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS name (
            id INTEGER PRIMARY KEY,
            text TEXT UNIQUE
        )""")


        self.cur.execute("""CREATE TABLE IF NOT EXISTS company_name (
            id_company INTEGER,
            id_name INTEGER,
            CONSTRAINT company_name_pk PRIMARY KEY (id_company, id_name),
            CONSTRAINT company_fk FOREIGN KEY(id_company) REFERENCES company(id),
            CONSTRAINT name_fk FOREIGN KEY (id_name) REFERENCES name(id)
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS event_company (
            id_company INTEGER,
            id_event INTEGER,
            exhibitor_link TEXT,
            date_added TIMESTAMP,
            CONSTRAINT event_company_pk PRIMARY KEY (id_company, id_event),
            CONSTRAINT company_fk FOREIGN KEY(id_company) REFERENCES company(id),
            CONSTRAINT event_fk FOREIGN KEY (id_event) REFERENCES name(id)
        )""")

    def process_item(self, item, spider):

        try:
            linkedin = item['linkedin']
        except:
            linkedin = None

        try:
            domain = item['domain']
        except:
            domain = None
        
        print(linkedin)
        # Inserts into companies table
        self.cur.execute("""INSERT OR IGNORE INTO company(domain, linkedin) VALUES (?,?)""", (domain, linkedin))
        if domain is not None:
            company_row_id = self.cur.execute("SELECT id FROM company WHERE domain = (?)", (domain,)).fetchone()[0]
        else:
            company_row_id = self.cur.lastrowid

        # Inserts into names table (cause a company can have many names)
        self.cur.execute("""INSERT OR IGNORE INTO name(text) VALUES (?)""",(item['name'],))
        name_row_id = self.cur.execute("SELECT id FROM name WHERE text = (?)" ,(item['name'],)).fetchone()[0]

        # Inserts the relation between the both
        self.cur.execute("""INSERT OR IGNORE INTO company_name(id_company, id_name) VALUES (?,?)""",(company_row_id, name_row_id))

        # Inserts the event the new company is related to
        self.cur.execute("""INSERT OR IGNORE INTO event_company(id_company, id_event, exhibitor_link, date_added) VALUES (?,?,?,?)""",(company_row_id, item['event_id'], item['event_company_link'],datetime.now()))

        # Update last time scraped - event
        now = datetime.now()
        self.cur.execute("""UPDATE event SET last_time_scraped=? WHERE id=?""", (now, item['event_id']))
        
        self.con.commit()
        return item
