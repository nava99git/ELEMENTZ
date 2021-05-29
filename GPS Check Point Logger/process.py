import sqlite3
from math import radians, degrees, sin, cos, asin, acos, sqrt

chekpointsDB = 'databases/checkpoints.db'
buffDB = 'databases/buff.db'

# The Great Circle Distance Formula
def distance(lat1, long1, lat2, long2):
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
	return 6371 * (acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2)))

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
		break

	TIMESTAMP, VID, VLAT, VLONG = buff
	conn = sqlite3.connect(checkpointsDB)
	cur = conn.cursor()
	cur.execute("SELECT * FROM checkpointsList")
	checkpoint = cur.fetchone()

	checkpointMatch = False
	while not checkpoint == None:
		CID, CLAT, CLONG = checkpoint

		if distance(VLAT, VLONG, CLAT, CLONG) <= 0.1:
			print("Vehicle %s Detected at Checkpoint %s" % (VID,CID))
			checkpointMatch = True
			break
		else:
			checkpoint = cur.fetchone()
			pass
	conn.close()
	time.sleep(1)

	if checkpointMatch == True:
		conn = sqlite3.connect('databases/checkpoints/%s.db' % (CID))
		cur = conn.close()
		cur.execute("SELECT 'TIMESTAMP' FROM vehicleList WHERE VID = '%s' ORDER BY 'TIMESTAMP' DESC" % (VID))
		lastTIMESTAMP = cur.fetchone()[0]

		if lastTIMESTAMP == None:
			cur.execute("INSERT INTO vehicleList VALUES (datetime('now','localtime'), %s)" % (VID))
			conn.commit()
			conn.close()
		else:
			timediff = lastTIMESTAMP - datetime('now','localtime')
			minutediff = divmod(timediff.total_seconds(), 60)[0]
			if minutediff > 5:
				cur.execute("INSERT INTO vehicleList VALUES (datetime('now','localtime'), %s)" % (VID))
				conn.commit()
				conn.close()