from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import datetime
import sqlite3
import datetime as dt

EC = 500
admn_pass = '56789'

app = Flask(__name__)

app.secret_key = 'thisisaverysecretkey'
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'studentlred'

class User(UserMixin):
    def __init__(self, id, NAME, password):
         self.id = id
         self.NAME = NAME
         self.password = password
         self.authenticated = False
         def is_active(self):
             return self.is_active()
         def is_anonymous(self):
             return False
         def is_authenticated(self):
             return self.authenticated
         def is_active(self):
             return True
         def get_id(self):
             return self.id

@login_manager.user_loader
def load_user(user_id):
   conn = sqlite3.connect('StudentBankDB.db')
   cur = conn.cursor()
   cur.execute("SELECT ID, NAME, PIN from Students where ID = (?)",[user_id])
   lu = cur.fetchone()
   conn.close()
   if lu is None:
      return None
   else:
      return User(int(lu[0]), lu[1], lu[2])


@app.route("/")
def index():
   return render_template('index.html')

@app.route('/studentlogin')
def studentlred():
    return redirect(url_for('index'))

@app.route('/studentlogin/<state>', methods=['POST'])
def studentlogin(state = 'null'):
     if state == 'null':
        return render_template('student_login.html')
   
     elif state == 'check':
#       if current_user.is_authenticated:
#           return redirect(url_for('studentdashboard'))
         try:
            StudentID = int(request.form['Student_ID'])
            Pin = int(request.form['Pin'])
         except:
            templateData = {'LoginError': "Invalid ID/Pin"}
            return render_template('student_login.html', **templateData)
            
         conn = sqlite3.connect('StudentBankDB.db')
         cur = conn.cursor()
         try:
             cur.execute("SELECT PIN, NoofTry, DISABLED, BLOCKED FROM Students WHERE ID= '%d'" % (StudentID))
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
                Us = load_user(StudentID)
                login_user(Us)
                if int(NoofTry) == -1:
                   return redirect(url_for('changepin', state = 'null', ID = StudentID))
                else:
                   conn = sqlite3.connect('StudentBankDB.db')
                   cur = conn.cursor()
                   cur.execute("UPDATE Students set NoofTry = 0 WHERE ID= '%d'" % (StudentID))
                   conn.commit()
                   conn.close()
                   return redirect(url_for('student_dashboard',ID = StudentID))

             elif Pin != int(PIN_DB) and int(NoofTry) != -1:
                print("Incorrect Pin")
                conn = sqlite3.connect('StudentBankDB.db')
                cur = conn.cursor()
                Curr_NoofTry = int(NoofTry) + 1
                Blocked = 1 if Curr_NoofTry >= 3 else 0 
                cur.execute("UPDATE Students set NoofTry = %d, BLOCKED = %d WHERE ID= '%d' " % (Curr_NoofTry, Blocked, StudentID))
                conn.commit()
                conn.close()
                templateData = {'LoginError': 'Incorrect Pin!'}
                return render_template('student_login.html', **templateData)
         except:
             print("Invalid Student ID")
             templateData = {'LoginError': 'Check Your Student ID!'}
             return render_template('student_login.html', **templateData)

@app.route('/adminlogin/<state>', methods=['POST'])
def adminlogin(state):
    if state == 'null':
        return render_template('adminlogin.html')
    elif state == 'check':
        Pin = request.form['Pin']
        if Pin == admn_pass:
            conn = sqlite3.connect('StudentBankDB.db')
            cur = conn.cursor()
            cur.execute("UPDATE AdmnStatus set Status = 1")
            conn.commit()
            conn.close()
            return redirect(url_for('admindashboard'))
        else:
            templateData = {'LoginError':'Wrong Pin'}
            return render_template('adminlogin.html', **templateData)
        
@app.route('/admindashboard')
def admindashboard():
    conn = sqlite3.connect('StudentBankDB.db')
    cur = conn.cursor()
    cur.execute("SELECT Status FROM AdmnStatus")
    admnstatus = int(cur.fetchone()[0])
    conn.close()
    if int(admnstatus) != 1:
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html')
     

@app.route('/admindashboard/Transactions', methods=['POST', 'GET'])
def ATransactions():
    conn = sqlite3.connect('StudentBankDB.db')
    cur = conn.cursor()
    cur.execute("SELECT Status FROM AdmnStatus")
    admnstatus = int(cur.fetchone()[0])
    conn.close()
    
    if int(admnstatus) != 1:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('StudentBankDB.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    TxID = request.form['TransactionID']
    if TxID != '0':
      cur.execute("SELECT TxDate, TxID, ID, RFID, AmtCr, AmtDr FROM Transactions WHERE TxID = '%s'" %(TxID))
      rows = cur.fetchall()
      print(rows)
      conn.close()
      return render_template('admin_dashboard.html',rows = rows)
    else:
      filteroptions = ''
      IDorRFID = request.form['IDorRFID']
      filterID = request.form['filterID']
      if IDorRFID != 'null' and filterID != '0':
        filteroptions += "WHERE %s = %s" % (IDorRFID, filterID)
        
      StartDate = request.form['StartDate']
      EndDate = request.form['EndDate']
      try:
          t = dt.datetime.strptime(StartDate, '%Y-%m-%d')
          t = dt.datetime.strptime(EndDate, '%Y-%m-%d')
          if filteroptions == '':
              filteroptions += "WHERE TxDate BETWEEN '%s' AND '%s'" % (StartDate, EndDate)
          else:
              filteroptions += " AND TxDate BETWEEN '%s' AND '%s'" % (StartDate, EndDate)
      except:      
          pass
      try:
          print(filteroptions)
          cur.execute("SELECT TxDate, TxID, ID, RFID, AmtCr, AmtDr FROM Transactions %s" % (filteroptions))
          rows = cur.fetchall()
          conn.close()
          return render_template('admin_dashboard.html', rows = rows)
      except:
          templateData = {'Error': "INVALID VALUES GIVEN!"}
          conn.close()
          return render_template('admin_dashboard.html', **templateData)

@app.route("/admindashboard/addnew/<state>", methods=['POST', 'GET'])
def addnew(state):
    conn = sqlite3.connect('StudentBankDB.db')
    cur = conn.cursor()
    cur.execute("SELECT Status FROM AdmnStatus")
    admnstatus = int(cur.fetchone()[0])
    conn.close()
    
    if int(admnstatus) != 1:
        return redirect(url_for('index'))
    
    if state == 'null':
        return render_template('addnew.html')
    elif state == 'add':
        NewRFID = request.form['NewRFID']
        NewName = request.form['NewName']
        NewPin = request.form['NewPin']
        NewAmount = float(request.form['NewAmount'])
        
        conn = sqlite3.connect('StudentBankDB.db')
        cur = conn.cursor()
        try:
            cur.execute("SELECT RFID FROM Students WHERE RFID = '%s'" %(NewRFID))
            checkRFID = cur.fetchone()[0]
        except:
            checkRFID = ''
        if checkRFID != '':
            templateData = {'Error': 'RFID Already Exists!'}
            conn.close()
            return render_template('addnew.html', **templateData)
        else:
            cur.execute("SELECT max(ID) FROM Students")
            lastID = str(cur.fetchone()[0])
            DT = dt.datetime.now()
            lastIDyear = lastID[0:4]
            
            if lastIDyear != str(DT.year):
                NewID = int("%s0000"%(DT.year)) + 1
                
            else:
                NewID = int(lastID) +1
            Amount = NewAmount - EC
            cur.execute("INSERT INTO Students VALUES (%d,%s,'%s',%s,%d,%d,0,0,-1);"%(NewID,NewRFID,NewName,NewPin,Amount, EC))
            conn.commit()
            cur.execute("SELECT * FROM Students WHERE ID = '%d'" %(NewID))
            newItem = cur.fetchall()
            templateData = {'Error': newItem}
            conn.close()
            return render_template('addnew.html', **templateData)
        
@app.route("/admindashboard/updatedata/<state>", methods=['POST', 'GET'])
def update(state):
    conn = sqlite3.connect('StudentBankDB.db')
    cur = conn.cursor()
    cur.execute("SELECT Status FROM AdmnStatus")
    admnstatus = int(cur.fetchone()[0])
    conn.close()
    
    if int(admnstatus) != 1:
        return redirect(url_for('index'))
    
    if state == 'null':
        return render_template('updatedata.html')
    elif state == 'update':
        ID = request.form['ID']
        toupdate = request.form['toupdate']
        valueupdate = request.form['valueupdate']
        
        conn = sqlite3.connect('StudentBankDB.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM Students WHERE ID = %s" %(ID))
        if cur.fetchone() == None:
            conn.close()
            templateData = {'Error': 'ID not found!'}
            return render_template('updatedata.html', **templateData)
        conn.close()
        if toupdate == 'null':
           templateData = {'Error': 'Please select a value to update'}
           return render_template('updatedata.html', **templateData)
        elif toupdate == 'Amount':
            try:
                TotalAmount = float(valueupdate)
            except:
                templateData = {'Error': 'Please enter valid amount'}
                return render_template('updatedata.html', **templateData)
            conn = sqlite3.connect('StudentBankDB.db')
            cur = conn.cursor()
            try:
                cur.execute("SELECT RFID, AMOUNT, EC FROM Students WHERE ID = %s" %(ID))
            except:
                conn.close()
                templateData = {'Error': 'Please enter valid ID'}
                return render_template('updatedata.html', **templateData)
            
            
            RFID, curAmount, curEC = cur.fetchone()
            DT = dt.datetime.now()
            TxID = "%s%s%s%s%s%s%s" % (int(ID)%10,DT.year,DT.month,DT.day,DT.hour,DT.minute,DT.second)
            cur.execute("INSERT INTO Transactions VALUES (date('now'),%s, %s, %s,%d, 0)" %(TxID, ID, RFID, TotalAmount))
            
            ECtoadd = EC-float(curEC)
            TotalAmount -= ECtoadd
            newEC = float(curEC) + ECtoadd
            newAmount = float(curAmount) + TotalAmount
            cur.execute("UPDATE Students SET AMOUNT = %d, EC = %d WHERE ID = %s" %(newAmount,newEC,ID))
            conn.commit()
            conn.close()
            templateData = {'Error': 'Success!'}
            return render_template('updatedata.html', **templateData)
        else:
            try:
                conn = sqlite3.connect('StudentBankDB.db')
                cur = conn.cursor()
                if toupdate == 'BLOCKED' and valueupdate == '0':
                    cur.execute("UPDATE Students SET NoofTry = 0 WHERE ID = %s" %(ID))
                cur.execute("UPDATE Students SET %s = '%s' WHERE ID = %s" %(toupdate, valueupdate,ID))
                conn.commit()
                conn.close()
                templateData = {'Error': 'Success!'}
            except:
                templateDate = {'Error': 'Enter valid value'}
            return render_template('updatedata.html', **templateData)

@app.route("/admindashboard/logout", methods=['POST'])
def adminlogout():
    conn = sqlite3.connect('StudentBankDB.db')
    cur = conn.cursor()
    cur.execute("UPDATE AdmnStatus set Status = 0")
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/changepin/<state>/<int:ID>", methods=['POST', 'GET'])
@login_required
def changepin(state,ID):
   curUsrID = current_user.get_id()
   if int(curUsrID) != ID:
       logout_user()
       return redirect(url_for('index'))
    
   if state == 'null':
      templateData = {'ID':ID}
      return render_template('changepin.html', **templateData)
   elif state == 'check':
      try:
          NewPin = int(request.form['NewPin'])
          ConfirmPin = int(request.form['ConfirmPin'])
      except:
          templateData = {'Error': "Only numbers are allowed", 'ID':ID}
          return render_template('changepin.html', **templateData)
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
@login_required
def student_dashboard(ID):
   curUsrID = current_user.get_id()
   if int(curUsrID) != ID:
       logout_user()
       return redirect(url_for('index'))
    
   conn = sqlite3.connect('StudentBankDB.db')
   cur = conn.cursor()
   cur.execute("SELECT RFID, NAME, AMOUNT, EC FROM Students WHERE ID = %d" %(ID))
   RFID, Name, Amount, ExtraCredit = cur.fetchone()
   templateData = {'ID': ID, 'RFID': RFID, 'NAME': Name, 'AMOUNT': Amount, 'EC': ExtraCredit}
   return render_template('student_dashboard.html', **templateData)

@app.route("/studen_dashboard/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/student_dashboard/Transactions/<int:ID>", methods=['POST', 'GET'])
@login_required
def STransactions(ID):
   curUsrID = current_user.get_id()
   if int(curUsrID) != ID:
       logout_user()
       return redirect(url_for('index'))
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
      return render_template('student_dashboard.html', **templateData, rows = rows)
   else:
      StartDate = request.form['StartDate']
      EndDate = request.form['EndDate']
      print(StartDate)
      print(EndDate)
      try:
          t = dt.datetime.strptime(StartDate, '%Y-%m-%d')
          t = dt.datetime.strptime(EndDate, '%Y-%m-%d')
      except:      
          templateData = {'ID': ID, 'RFID': RFID, 'NAME': Name, 'AMOUNT': Amount, 'EC': ExtraCredit, 'Error': "INVALID DATE GIVEN!"}
          conn.close()
          return render_template('student_dashboard.html', **templateData)
        
      cur.execute("SELECT TxDate, TxID, AmtCr, AmtDr FROM Transactions WHERE ID = %s AND TxDate BETWEEN '%s' AND '%s'" % (ID, StartDate, EndDate))
      rows = cur.fetchall()
      conn.close()
      templateData = {'ID': ID, 'RFID': RFID, 'NAME': Name, 'AMOUNT': Amount, 'EC': ExtraCredit}
      return render_template('student_dashboard.html', **templateData, rows = rows)
          

if __name__ == "__main__":
   app.run(host='192.168.1.9', port=8080, debug=True,threaded=True)
