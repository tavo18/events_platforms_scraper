import sqlite3
from datetime import datetime

con  = sqlite3.connect('project/server/events.db')
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS event (
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

cur.execute("""INSERT INTO event(name, exhibitors_link, start_date, last_time_scraped, created_at, in_grata) VALUES(?,?,?,?,?,?)""", 
('American Society of Plumbing Engineers (ASPE) Convention & Expo 2022', 'https://s23.a2zinc.net/Clients/TaffyEvents/ASPE2022/public/exhibitors.aspx',
datetime(year=2022, month=9, day=16), None, datetime.now(), False))

cur.execute("""INSERT INTO event(name, exhibitors_link, start_date, last_time_scraped, created_at, in_grata) VALUES(?,?,?,?,?,?)""",
('American Agents Alliance (AAA) Conference & Expo 2019', 'https://s15.a2zinc.net/clients/agents/aaa2019/public/exhibitors.aspx', 
datetime(year=2019, month=9, day=26), None,datetime.now(), False))

con.commit()

con.close()