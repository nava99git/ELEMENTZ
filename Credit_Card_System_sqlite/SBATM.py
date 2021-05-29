import sqlite3
import datetime
from RPLCD.i2c import CharLCD
import time
from time import sleep
import digitalio
import board
import adafruit_matrixkeypad
import serial
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library

ser = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=0.5)
ser.flush()

cols = [digitalio.DigitalInOut(x) for x in (board.D26, board.D20, board.D21)]
rows = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]

keys = ((1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),
        ('*', 0, '#'))

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

lcd = CharLCD('PCF8574', 0x3f)
lcd = CharLCD(i2c_expander='PCF8574', address=0x3f, port=1,
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)

def keypad_in():
    keyinput = ""
    while True:
        keys = keypad.pressed_keys
        if keys:
            time.sleep(.5)
            for i in keys:
                if i == '*':
                    print(keyinput)
                    return keyinput
                else:
                    keyinput += str(i)
                    print(i)
                    lcd.cursor_pos = (1,0)
                    lcd.write_string(keyinput)

print('Scan Your RFID')
lcd.clear()
lcd.cursor_pos = (0,0)
lcd.write_string('Scan Your RFID')
while True:
    if ser.in_waiting > 0:
        RFID = ser.readline().decode('utf-8').rstrip()
        print(RFID)
        validRFID = 1
        try:
            conn = sqlite3.connect('StudentBankDB.db')
            cur = conn.cursor()
            cur.execute("SELECT ID, NAME, PIN, AMOUNT, EC, DISABLED, BLOCKED FROM Students WHERE RFID = %s" % (RFID))
            ID, NAME, PIN, AMOUNT, EC, DISABLED, BLOCKED = cur.fetchone()
            conn.close()
        except:
            print("Invalid RFID Detected!")
            lcd.clear()
            lcd.cursor_pos = (0,0)
            lcd.write_string('Invalid RFID')
            validRFID = 0
        if validRFID == 1:
            if DISABLED == 1 or BLOCKED == 1:
                print("Your account is blocked/disabled")
                lcd.clear()
                lcd.cursor_pos = (0,0)
                lcd.write_string('Blocked/Disabled')
            else:
                print('Enter Pin')
                lcd.clear()
                lcd.cursor_pos = (0,0)
                lcd.write_string('Enter Pin:')
                
                inPin = int(keypad_in())
                print(inPin)
                if inPin == int(PIN):
                    print("Successfully Logged in")
                    print("WELCOME")
                    print("ID: %s" %(ID))
                    print("NAME: %s" %(NAME))
                    print("AMOUNT: %s" %(AMOUNT))
                    print("EC: %s" %(EC))
                    
                    lcd.clear()
                    lcd.cursor_pos = (0,0)
                    lcd.write_string("WELCOME ID: %s" %(ID))
                    time.sleep(1)
                    lcd.clear()
                    lcd.cursor_pos = (0,0)
                    lcd.write_string("Bal: %s" % (AMOUNT))
                    lcd.cursor_pos = (1,0)
                    lcd.write_string("EC: %s" %(EC))
                    keypad_in()
                    
                    print('Enter Debit Amount')
                    lcd.clear()
                    lcd.cursor_pos = (0,0)
                    lcd.write_string('Enter Amount:')
                    
                    debitAmount = float(keypad_in())
                    print(debitAmount)
                    if debitAmount < float(AMOUNT) + float(EC):
                        if(debitAmount < float(AMOUNT)):
                            newAMOUNT = float(AMOUNT) - debitAmount
                            newEC = float(EC)
                        else:
                            newAMOUNT = 0
                            if(float(AMOUNT) != 0):
                                newEC = float(EC) - (debitAmount - float(AMOUNT))
                            else:
                                newEC = float(EC) - debitAmount                       
                        DT = datetime.datetime.now()
                        TxID = "%s%s%s%s%s%s%s" % (ID%10,DT.year,DT.month,DT.day,DT.hour,DT.minute,DT.second)
                        print(TxID)
                        conn = sqlite3.connect('StudentBankDB.db')
                        cur = conn.cursor()
                        cur.execute("UPDATE Students SET AMOUNT = %d, EC = %d WHERE RFID = %s" % (newAMOUNT, newEC, RFID))
                        conn.commit()
                        cur.execute("INSERT INTO Transactions VALUES(date('now'),%s, %s, %s,0, %d)" %(TxID, ID, RFID, debitAmount))
                        conn.commit()
                        conn.close()
                        
                        time.sleep(2)
                        
                        print("Your Receipt:")
                        print("TxID: %s" %(TxID))
                        print("Debit Amount: %d" % (debitAmount))
                        print("Balance: AMOUNT: %d EC: %d" % (newAMOUNT, newEC))
                        print("Time stamp: %s" %(DT))
                        
                        lcd.clear()
                        lcd.cursor_pos = (0,0)
                        lcd.write_string('Transaction')
                        lcd.cursor_pos = (1,0)
                        lcd.write_string('Successful')
                        keypad_in()
                        
                        lcd.clear()
                        lcd.cursor_pos = (0,0)
                        lcd.write_string('TxID:')
                        lcd.cursor_pos = (1,0)
                        lcd.write_string(TxID)
                        keypad_in()
                        
                        lcd.clear()
                        lcd.cursor_pos = (0,0)
                        lcd.write_string('Debit Amt:')
                        lcd.cursor_pos = (1,0)
                        lcd.write_string(str(debitAmount))
                        keypad_in()
                        
                        lcd.clear()
                        lcd.cursor_pos = (0,0)
                        lcd.write_string('Bal: ')
                        lcd.cursor_pos = (0,5)
                        lcd.write_string(str(newAMOUNT))
                        lcd.cursor_pos = (1,0)
                        lcd.write_string('EC: ')
                        lcd.cursor_pos = (1, 4)
                        lcd.write_string(str(newEC))
                        keypad_in()
                        
                        print("Updated Successfully")
                        
                    else:
                        print("Insufficent Balance")
                        lcd.clear()
                        lcd.cursor_pos = (0,0)
                        lcd.write_string('Insufficient')
                        lcd.cursor_pos = (1,0)
                        lcd.write_string('Balance!')
                else:
                    print("WRONG PIN!!!")
                    lcd.clear()
                    lcd.cursor_pos = (0,0)
                    lcd.write_string('Wrong Pin')
        time.sleep(2)                
        print('Scan Your RFID')
        lcd.clear()
        lcd.cursor_pos = (0,0)
        lcd.write_string('Scan Your RFID')                
