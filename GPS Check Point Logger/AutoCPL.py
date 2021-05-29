from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import json
import datetime as dt

app = Flask(__name__)

checkpointsDB = 'databases/checkpoints.db'
buffDB = 'databases/buff.db'

@app.route('/gpsdata', methods = ['POST'])
def gpsdata():
	gpsloc = json.loads(request.data)
	print("VID : %s LAT : %d LONG : %d" % (gpsloc['VID'], gpsloc['lat'], gpsloc['long']))
	try:
		conn = sqlite3.connect(buffDB)
		cur = conn.cursor()
		cur.execute("SELECT * FROM buffList WHERE VID = '%s'" % (gpsloc['VID']))
		bufftry = cur.fetchall()
		if bufftry == None:
			cur.execute("INSERT INTO buffList VALUES (datetime('now', 'localtime'), '%s' , %d, %d)" % (gpsloc['VID'], gpsloc['lat'], gpsloc['long']))
		else:
			cur.execute("UPDATE buffList SET TIMESTAMP = datetime('now', 'localtime') LAT = %d, LONG = %d WHERE VID = '%s'" % (gpsloc['lat'], gpsloc['long'], gpsloc['VID']))
		conn.commit()
		conn.close()
	except:
		pass
	return ''

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/addcheckpoint/<state>', methods = ['POST'])
def addcheckpost(state):
	if state == 'null':
		return render_template('addcheckpoint.html')
	elif state == 'check':
		CID = request.form['NewCID']
		LAT = request.form['NewLAT']
		LONG = request.form['NewLONG']

		try:
			conn = sqlite3.connect(checkpointsDB)
			cur = conn.cursor()
			cur.execute("INSERT INTO checkpointsList VALUES ('%s', %s, %s)" % (CID, LAT, LONG))
			conn.commit()
			conn.close()
			DB = 'databases/checkpoints/%s.db' % (CID)
			conn = sqlite3.connect(DB)
			conn.execute('''CREATE TABLE vehicleList(TIMESTAMP TEXT not null,VID TEXT not null);''')
			conn.close()
			return render_template('addcheckpoint.html', ERROR = 'Checkpoint added successfully!')
		except:
			try:
				conn.close()
			except:
				pass
			return render_template('addcheckpoint.html', ERROR = 'Something went wrong!')

@app.route('/browse/<state>', methods = ['POST'])
def browse(state):
	if state == 'null':
		return render_template('browse.html')
	elif state == 'check':
		CID = request.form['CID']
		VID = request.form['VID']
		StartDate = request.form['StartDate']
		EndDate = request.form['EndDate']

		DB = 'databases/checkpoints/%s.db' % (CID)
		try:
			conn = sqlite3.connect(DB)
			conn.row_factory = sqlite3.Row
			cur = conn.cursor()
			filtermsg = ''
			try:
				t = dt.datetime.strptime(StartDate, '%Y-%m-%d')
				filtermsg = "WHERE date(TIMESTAMP) BETWEEN '%s' AND date('now','localtime')" % (StartDate)
				t = dt.datetime.strptime(EndDate, '%Y-%m-%d')
				filtermsg = "WHERE date(TIMESTAMP) BETWEEN '%s' AND '%s'" % (StartDate, EndDate)
			except:
				pass

			if VID != '':
				if filtermsg == '':
					filtermsg = "WHERE VID = '%s'" % (VID)
				else:
					filtermsg = " AND VID = '%s'" % (VID)

			print(filtermsg)
			cur.execute("SELECT * FROM vehicleList %s" % (filtermsg))
			rows = cur.fetchall()
			print(rows)
			return render_template('browse.html', rows = rows)
		except:
			try:
				conn.close()
			except:
				pass
			return render_template('browse.html', ERROR = 'Something went wrong!')

app.run(host='127.0.0.1', port=5000, debug=True)