from flask import Flask, render_template, request, redirect, url_for
import datetime
import sqlite3

app = Flask(__name__)
@app.route("/")
def index():
   return render_template('index.html')

@app.route('/studentlogin/<state>', methods=['POST'])
def studentlogin(state):
   if state == 'null':
      return render_template('student_login.html')
   
   elif state == 'check':  
      StudentID = int(request.form['Student_ID'])
      Pin = int(request.form['Pin'])

      conn = sqlite3.connect('StudentBankDB.db')
      cur = conn.cursor()
      
      try:
         cur.execute("SELECT PIN, NoofTry, DISABLED, BLOCKED FROM Students WHERE ID='%d'" % (StudentID))
         PIN_DB, NoofTry, Disabled, Blocked = cur.fetchone()
         conn.close()

         if int(Disabled) == 1:
            templateData = {'LoginError': "Account is Disabled!"}
            return render_template('student_login.html', **templateData)

         elif int(Blocked) == 1:
            templateData = {'LoginError': "Account is Blocked!"}
            return render_template('student_login.html', **templateData)

         elif Pin == int(PIN_DB):
            print("Succesful Login")
            if int(NoofTry) == -1:
               return redirect(url_for('changepin', state = 'null', ID = StudentID))
            else:
               conn = sqlite3.connect('StudentBankDB.db')
               cur = conn.cursor()
               cur.execute("UPDATE Students set NoofTry = 0 WHERE ID=%d" % (StudentID))
               conn.commit()
               conn.close()
               return redirect(url_for('student_dashboard',ID = StudentID))

         elif Pin != int(PIN_DB):
            print("Incorrect Pin")
            conn = sqlite3.connect('StudentBankDB.db')
            cur = conn.cursor()
            Curr_NoofTry = int(NoofTry) + 1
            Disabled = 1 if NoofTry < 4 else 0 
            cur.execute("UPDATE Students set NoofTry = %d, DISABLED = %d WHERE ID=%d" % (Curr_NoofTry, Disabled, StudentID))
            conn.commit()
            conn.close()
            templateData = {'LoginError': "Incorrect Pin!"}
            return render_template('student_login.html', **templateData)
      except:
         print("Invalid Student ID")
         templateData = {'LoginError': "Invalid Student ID!"}
         return render_template('student_login.html', **templateData)

@app.route("/changepin/<state>/<int:ID>", methods=['POST', 'GET'])
def changepin(state,ID):
   if state == 'null':
      templateData = {'ID':ID}
      return render_template('changepin.html', **templateData)
   elif state == 'check':
      NewPin = int(request.form['NewPin'])
      ConfirmPin = int(request.form['ConfirmPin'])
      if NewPin == ConfirmPin:
         conn = sqlite3.connect('StudentBankDB.db')
         cur = conn.cursor()
         try:
            cur.execute("SELECT PIN FROM Students WHERE ID='%d'" % (ID))
            PIN_DB = int(cur.fetchone()[0])
            if NewPin == PIN_DB:
               print("Same as previous password")
               templateData = {'Error':"Same as previous password", 'ID': ID }
               conn.close()
               return render_template('changepin.html', **templateData)
            else:
               cur.execute("UPDATE Students set PIN = %d, NoofTry = 0 WHERE ID='%d'" % (NewPin, ID))
               conn.commit()
               conn.close()
               print("Pin Changed Succesfully")
               return redirect(url_for('student_dashboard', ID = ID))
         
         except:
            print("Something went wrong")
            return redirect(url_for('student_login', state = 'null'))
      else:
         print("Pins do not match")
         templateData = {'Error':"Pins do not match", 'ID': ID }
         return render_template('changepin.html', **templateData)

@app.route('/student_dashboard/<int:ID>', methods=['POST', 'GET'])
def student_dashboard(ID):
   conn = sqlite3.connect('StudentBankDB.db')
   cur = conn.cursor()
   cur.execute("SELECT RFID, NAME, AMOUNT, EC FROM Students WHERE ID = %d" %(ID))
   RFID, Name, Amount, ExtraCredit = cur.fetchone()
   templateData = {'ID': ID, 'RFID': RFID, 'NAME': Name, 'AMOUNT': Amount, 'EC': ExtraCredit}
   return render_template('student_dashboard.html', **templateData)

@app.route("/student_dashboard/Transactions/<int:ID>", methods=['POST', 'GET'])
def Transactions(ID):
   conn = sqlite3.connect('StudentBankDB.db')
   conn.row_factory = sqlite3.Row
   cur = conn.cursor()
   cur.execute("SELECT RFID, NAME, AMOUNT, EC FROM Students WHERE ID = %d" %(ID))
   RFID, Name, Amount, ExtraCredit = cur.fetchone()

   TxID = int(request.form['TransactionID'])
   if TxID != 0:
      cur.execute("SELECT TxDate, TxID, AmtCr, AmtDr FROM Transactions WHERE TxID = '%d'" %(TxID))
      rows = cur.fetchall()
      print(rows)
      conn.close()
      templateData = {'ID': ID, 'RFID': RFID, 'NAME': Name, 'AMOUNT': Amount, 'EC': ExtraCredit}
      return render_template('studentdashboard.html', **templateData, rows = rows)
   else:
      StartDate = request.form['StartDate']
      EndDate = request.form['EndDate']
      print(StartDate)
      print(EndDate)
      # try:
      cur.execute("SELECT TxDate, TxID, AmtCr, AmtDr FROM Transactions WHERE TxDate BETWEEN '%s' AND '%s'" % (StartDate, EndDate))
      rows = cur.fetchall()
      conn.close()
      templateData = {'ID': ID, 'RFID': RFID, 'NAME': Name, 'AMOUNT': Amount, 'EC': ExtraCredit}
      return render_template('student_dashboard.html', **templateData, rows = rows)
      # except:
      #    templateData = {'ID': ID, 'RFID': RFID, 'NAME': Name, 'AMOUNT': Amount, 'EC': ExtraCredit, 'Error': "INVALID DATE GIVEN!"}
      #    conn.close()
      #    return render_template('student_dashboard.html', **templateData)

if __name__ == "__main__":
   app.run(host='192.168.43.86', port=80, debug=True)
