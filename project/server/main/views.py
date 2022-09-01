# project/server/main/views.py


from datetime import datetime
from flask import render_template, Blueprint, jsonify, request, redirect, url_for
import sqlite3


main_blueprint = Blueprint("main", __name__,)


@main_blueprint.route("/", methods=["GET"])
def home():
    return render_template("main/home.html")

@main_blueprint.route("/events", methods=["GET"])
def events():
    # Get past tasks
    conn = sqlite3.connect('project/server/events.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
       
    event_data_fetch = c.execute("""SELECT * FROM event""").fetchall()
    
    event_data = [dict(item) for item in event_data_fetch]
    for i,item in enumerate(event_data):
        total_companies = len(c.execute("""SELECT id_company FROM event_company WHERE event_company.id_event = ?""", (item['id'],)).fetchall())
        missing_domains = len(c.execute("""SELECT id_company FROM event_company, company WHERE event_company.id_event = ? 
        AND event_company.id_company = company.id AND company.domain IS NULL""", (item['id'],)).fetchall())
        
        # event_data[i]['missing_domains'] = missing_domains
        event_data[i]['total_companies'] = total_companies
        event_data[i]['total_domains'] = total_companies-missing_domains


    c.close()
    conn.close()
    
    event_data.sort(key=lambda item:item['created_at'], reverse=True)
    
    return render_template("main/events.html", events = event_data)

@main_blueprint.route("/events/<event_id>", methods=["GET"])
def event_companies(event_id):

    conn = sqlite3.connect('project/server/events.db')
    c = conn.cursor()
    
    event_data_fetch = c.execute("""SELECT name, last_time_scraped FROM event WHERE id = ?""", (event_id,)).fetchone()
    
    event_data = dict()
    companies = []
    has_missing = False
    if event_data_fetch:

        c.execute("""SELECT company.id, name.text, company.domain, event_company.date_added FROM name, company_name, company, event_company 
        WHERE event_company.id_event=? AND company.id = event_company.id_company 
        AND company.id = company_name.id_company AND name.id = company_name.id_name""",(event_id,))

        companies = c.fetchall()

        companies = [{'id': item[0],'name': item[1], 'domain': item[2],'date_added': item[3]} for item in companies]

        for company in companies:
            if company['domain'] is None:
                has_missing = True
                break

        companies.sort(key=lambda item:item['name'])

        event_data['id'] = event_id
        event_data['name'] = event_data_fetch[0]
        event_data['last_time_scraped'] = event_data_fetch[1]
     
    c.close()
    conn.close()
    
    # events.sort(key=lambda item:item['date_created'], reverse=True)
    
    return render_template("main/companies.html", companies = companies, event_data = event_data, has_missing = has_missing)

@main_blueprint.route("/events/edit_domains/<event_id>", methods=["GET"])
def edit_domains(event_id):

    conn = sqlite3.connect('project/server/events.db')
    c = conn.cursor()
    
    event_data_fetch = c.execute("""SELECT name, last_time_scraped FROM event WHERE id = ?""", (event_id,)).fetchone()
    
    event_data = dict()
    companies = []
    if event_data_fetch:

        c.execute("""SELECT company.id, name.text, company.domain, event_company.date_added FROM name, company_name, company, event_company 
        WHERE event_company.id_event=? AND company.id = event_company.id_company 
        AND company.id = company_name.id_company AND name.id = company_name.id_name AND company.domain IS NULL""",(event_id,))

        companies = c.fetchall()

        companies = [{'id': item[0],'name': item[1], 'domain': item[2],'date_added': item[3]} for item in companies]

        companies.sort(key=lambda item:item['name'])

        event_data['id'] = event_id
        event_data['name'] = event_data_fetch[0]
        event_data['last_time_scraped'] = event_data_fetch[1]
     
    c.close()
    conn.close()
    
    # events.sort(key=lambda item:item['date_created'], reverse=True)
    
    return render_template("main/edit_domains.html", companies = companies, event_data = event_data)

@main_blueprint.route("/edit_event/<event_id>")
def edit_event(event_id):
    conn = sqlite3.connect('project/server/events.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
       
    event_data_fetch = c.execute("""SELECT * FROM event WHERE id = ?""", (event_id,)).fetchone()
    
    event_data = dict(event_data_fetch)
    return render_template("main/edit_event.html", event_data = event_data)

@main_blueprint.route('/update_event', methods=["POST"])
def update_event():

    event_id = request.form['event_id']

    event_name = request.form['event_name']

    event_start_date = request.form['event_start_date']
    event_start_date = datetime.strptime(event_start_date, "%Y-%m-%d")

    event_end_date = request.form['event_end_date']
    event_end_date = datetime.strptime(event_end_date, "%Y-%m-%d")

    event_url = request.form['event_url']

    event_source = request.form['event_source']

    event_host = request.form['event_host']

    event_sector = request.form['event_sector']

    in_grata = request.form.get('in_grata')

    grata_uid = request.form['grata_uid']

    # Validate event url

    # Update event
    con = sqlite3.connect('project/server/events.db')
    cur = con.cursor()
    cur.execute("""UPDATE event SET name=?, exhibitors_link=?, start_date=?, 
                end_date=?, source=?, host=?, sector=?, in_grata=?, grata_uid=? WHERE id = ?""",
                (event_name, event_url, event_start_date, event_end_date, 
                event_source, event_host, event_sector, in_grata, grata_uid, event_id))
    con.commit()
    con.close()

    # return jsonify({'request': datetime.strptime(event_date, "%Y-%m-%d")}), 202
    return redirect(url_for('main.events', event_id = event_id), code = 302)


@main_blueprint.route('/add_event', methods=["POST"])
def add_event():
    event_name = request.form['event_name']
    event_date = request.form['event_date']
    event_date = datetime.strptime(event_date, "%Y-%m-%d")
    event_url = request.form['event_url']

    # Validate event url

    # Persist event
    con = sqlite3.connect('project/server/events.db')
    cur = con.cursor()
    cur.execute("""INSERT OR IGNORE INTO event(name, exhibitors_link, start_date, created_at) VALUES (?,?,?,?)""",
        (event_name, event_url, event_date, datetime.now()))
    con.commit()
    con.close()

    return redirect(url_for('main.events'), code = 302)

