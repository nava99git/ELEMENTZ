import sqlite3
import datetime

while True:

	RFID = input('Enter RFID: ')

	try:
		conn = sqlite3.connect('StudentBankDB.db')
		cur = conn.cursor()
		cur.execute("SELECT ID, NAME, PIN, AMOUNT, EC, DISABLED, BLOCKED FROM Students WHERE RFID = %s" % (RFID))
		ID, NAME, PIN, AMOUNT, EC, DISABLED, BLOCKED = cur.fetchone()
		conn.close()
	except:
		print("Invalid RFID Detected!")
		break;
	if DISABLED == 1 or BLOCKED == 1:
		print("Your account is blocked/disabled")
	else:
		inPin = int(input('Enter PIN: '))
		if inPin == int(PIN):
			print("Successfully Logged in")
			print("WELCOME")
			print("ID: %s" %(ID))
			print("NAME: %s" %(NAME))
			print("AMOUNT: %s" %(AMOUNT))
			print("EC: %s" %(EC))

			debitAmount = float(input('Enter amount to be debited: '))
			if debitAmount < float(AMOUNT) + float(EC):
				if(debitAmount < float(AMOUNT)):
					newAMOUNT = float(AMOUNT) - debitAmount
					newEC = float(EC)
				else:
					newAMOUNT = 0
					if(float(AMOUNT) != 0):
						newEC = float(EC) - (float(AMOUNT) - debitAmount)
					else:
						newEC = float(EC) - debitAmount
				DT = datetime.datetime.now()
				TxID = "%s%s%s%s%s%s%s" % (ID,DT.year,DT.month,DT.day,DT.hour,DT.minute,DT.second)
				print("Your Receipt:")
				print("TxID: %s" %(TxID))
				print("Debit Amount: %d" % (debitAmount))
				print("Balance: AMOUNT: %d EC: %d" % (newAMOUNT, newEC))
				print("Time stamp: %s" %(DT))
				conn = sqlite3.connect('StudentBankDB.db')
				cur = conn.cursor()
				cur.execute("UPDATE Students SET AMOUNT = %d, EC = %d WHERE RFID = %s" % (newAMOUNT, newEC, RFID))
				conn.commit()
				cur.execute("INSERT INTO Transactions VALUES(date('now'),%s, %s,0, %d)" %(TxID, RFID, debitAmount))
				conn.commit()
				conn.close()
				print("Updated Successfully")
			else:
				print("Insufficent Balance")
		else:
			print("WRONG PIN!!!")
