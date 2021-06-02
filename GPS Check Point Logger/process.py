import sqlite3
import time
from math import radians, degrees, sin, cos, asin, acos, sqrt
import datetime as dt
checkpointsDB = 'databases/checkpoints.db'
buffDB = 'databases/buff.db'

# The Great Circle Distance Formula
def distance(lat1, lon1, lat2, lon2):
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
	GCD = 6371 * (acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2)))
	return GCD

def timediff(date1, date2):
	fmt = '%Y-%m-%d %H:%M:%S'
	tstamp1 = dt.datetime.strptime(date1, fmt)
	tstamp2 = dt.datetime.strptime(date2, fmt)

	if tstamp1 > tstamp2:
	    td = tstamp1 - tstamp2
	else:
	    td = tstamp2 - tstamp1
	td_mins = int(round(td.total_seconds() / 60))
	return td_mins
	
while 1:
	while 1:
		time.sleep(2)
		try:
			conn = sqlite3.connect(buffDB)
			cur = conn.cursor()
			cur.execute("SELECT * FROM buffList")
			buff = cur.fetchone()
			conn.close()
			if buff == None:
				continue
			else:
				break
		except:
			try:
				conn.close()
			except:
				pass
			pass

	if buff == None:
		continue

	print(buff)
	TIMESTAMP, VID, VLAT, VLONG = buff
	conn = sqlite3.connect(checkpointsDB)
	cur = conn.cursor()
	cur.execute("SELECT * FROM checkpointsList")
	checkpoint = cur.fetchone()

	checkpointMatch = False
	while not checkpoint == None:
		CID, CLAT, CLONG = checkpoint
		print("Checkpoint : ")
		print(checkpoint)
		GCDdistance = distance(float(VLAT), float(VLONG), float(CLAT), float(CLONG))
		print(GCDdistance)
		if GCDdistance <= 0.5:
			print("Vehicle %s Detected at Checkpoint %s" % (VID,CID))
			checkpointMatch = True
			break
		else:
			checkpoint = cur.fetchone()
			pass
	conn.close()
	time.sleep(1)

	try:
		conn = sqlite3.connect(buffDB)
		conn.execute('''DELETE FROM buffList WHERE VID = '%s' ''' % (VID))
		conn.commit()
		conn.close()
	except:
		print('Database not open')
	print(checkpointMatch)
	if checkpointMatch == True:
		conn = sqlite3.connect('databases/checkpoints/%s.db' % (CID))
		cur = conn.cursor()
		cur.execute("SELECT TIMESTAMP FROM vehicleList WHERE VID = '%s' ORDER BY TIMESTAMP DESC" % (VID))
		try:
			lastTIMESTAMP = cur.fetchone()[0]
		except:
			lastTIMESTAMP = None
		if lastTIMESTAMP == None:
			print("Adding as new")
			cur.execute("INSERT INTO vehicleList VALUES (datetime('now','localtime'), '%s')" % (VID))
			conn.commit()
			conn.close()
		else:
			print('checking for last entry')
			curTIMESTAMP = str(dt.datetime.now()).split('.')[0]
			print("Cur: %s , last: %s" %(curTIMESTAMP, lastTIMESTAMP))
			mindiff = timediff(curTIMESTAMP, lastTIMESTAMP)

			print(mindiff)
			if mindiff > 5:
				print("Time limit over.. adding new")
				cur.execute("INSERT INTO vehicleList VALUES (datetime('now','localtime'), '%s')" % (VID))
				conn.commit()
				conn.close()
			else:
				conn.close()