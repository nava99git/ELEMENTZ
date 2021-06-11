from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import json

app = Flask(__name__)

dustbinDB = 'databases/dustbin.db'


@app.route('/dustbinStatus', methods=['POST'])
def dustbinStatus():
    status = json.loads(request.data)
    print("Dustbin : %s Status : %s" % (status['ID'], status['STATUS']))
    try:
        conn = sqlite3.connect(dustbinDB)
    except:
        print('Database Busy!')
        return 'Busy'
    cur = conn.cursor()
    cur.execute("SELECT ID FROM DustbinList WHERE ID = '%s'" % (status['ID']))
    try:
        ID = cur.fetchone()[0]
    except:
        ID = None
        print('New Bin ID detected... Adding to database!')
    if ID == None:
        cur.execute("INSERT INTO DustbinList VALUES ('%s', '%s')" %
                    (status['ID'], status['STATUS']))
    else:
        cur.execute("UPDATE DustbinList SET STATUS = '%s' WHERE ID = '%s'" % (
            status['STATUS'], status['ID']))
    conn.commit()
    conn.close()
    return 'UPDATED'

@app.route('/')
def index():
    return render_template('bin.html')

@app.route('/status', methods = ['GET'])
def status():
    try:
        conn = sqlite3.connect(dustbinDB)
        cur = conn.cursor()
        conn.row_factory = sqlite3.Row
        cur.execute("SELECT * FROM DustbinList")
        rows = cur.fetchall()
        conn.close()
        print(rows)
        return render_template('status.html', rows = rows)
    except:
        error = 'Error fetching data!'
        return render_template('status.html', error = error)

app.run(host='0.0.0.0', port= 8000, debug=True)
